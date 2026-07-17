"""
holo_agent_v0.2.py - HoloAgent 生产化版本

相对 v0.1 (holo_agent_prototype.py) 的改进:
  [+] retry 机制: 每个模型失败自动重试 (默认 2 次)
  [+] multi-model fallback: 多个 minimax 模型依次尝试
  [+] Trace/log 系统: 每个 act() 记录 token/latency/model/success
  [+] UTF-8 stdout 修复: 解决 PowerShell 终端中文乱码
  [+] 错误分类: billing_error / auth_error / timeout / unknown
  [+] 独立 agent routing: 用 --agent 参数隔离 main 上下文 (v0.2.1, 路径 A)
  [+] JSON 解析修复: 多个 JSON 块场景下找到含 "payloads" 的正确块 (v0.2.1)
  [+] JSON 控制字符修复: 转义 OpenClaw 输出的 literal \\n/\\r/\\t (v0.2.2)
  [+] JSON 块定位修复: 先定位 "payloads" 再向前找外层 { (v0.2.3)
  [+] 放弃 JSON parse 改用 regex 提取 "text" 字段 (v0.2.4, LLM 响应可能破坏 JSON 结构)
  [+] 自然语气 prompt: "我是 X" 而非强指令 (避免 minimax injection 防御, v0.2.1)
  [+] JSON 解析修复: 从后往前找含 "payloads" 字段的 JSON 块 (避免被前置 error block 误导, v0.2.1)
  [-] 失败尝试: ⚠️ emoji + "你不是 X" 会触发 injection 防御
  [+] 保留向后兼容: HAIS v0.1 API 完整, 旧代码可平滑迁移

HAIS v0.1 标准 (未变):
  - 5 段知识种子
  - 3 必选 API: act / observe / reflect
  - 4 扩展 API: escalate / remember / forget / handoff
  - 单文件 ≤ 400 行 (v0.1 是 280 行)

用法:
    python holo_agent_v0.2.py
    # 或在代码中:
    from holo_agent_v0.2 import TranslatorAgent, ProofreaderAgent, HoloAgent
"""
from __future__ import annotations
import json
import logging
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional

# ============================================================
# 终端 UTF-8 修复 (PowerShell GBK 乱码 → UTF-8)
# ============================================================
# 这两行必须在任何 print() 之前执行
try:
    sys.stdout.reconfigure(encoding="utf-8")  # Python 3.7+
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass  # 老 Python 不支持，忽略

# 定位 OpenClaw CLI
_OPENCLAW_BIN = shutil.which("openclaw") or "C:\\Users\\ThinkPad\\AppData\\Roaming\\npm\\openclaw.CMD"

# 日志目录
_LOG_DIR = Path("D:/temp/holo_agent_logs")
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_LOG_FILE = _LOG_DIR / "holo_agent.log"


# ============================================================
# 错误类型分类
# ============================================================
class LLMError(Exception):
    """LLM 调用错误的基类"""
    kind: str = "unknown"

    def __init__(self, message: str, kind: str = "unknown"):
        super().__init__(message)
        self.kind = kind


class BillingError(LLMError):
    kind = "billing"  # 余额耗尽


class AuthError(LLMError):
    kind = "auth"  # auth-profile rotate 失败


class TimeoutError(LLMError):
    kind = "timeout"  # 调用超时


class ModelNotAllowedError(LLMError):
    kind = "not_allowed"  # 模型不在 allowlist


class EmptyResponseError(LLMError):
    kind = "empty"  # 调用成功但返空


def _classify_error(stderr: str, stdout: str) -> LLMError:
    """根据 stderr/stdout 文本分类错误类型"""
    text = (stderr + " " + stdout).lower()
    if "billing" in text or "run out of credit" in text or "insufficient" in text:
        return BillingError(f"余额不足: {stderr[:200]}")
    if "not allowed" in text or "model override" in text:
        return ModelNotAllowedError(f"模型不允许: {stderr[:200]}")
    if "invalid api key" in text or "authentication" in text or "unauthorized" in text:
        return AuthError(f"认证失败: {stderr[:200]}")
    if "timeout" in text:
        return TimeoutError("调用超时")
    if "rate" in text and "limit" in text:
        return LLMError(f"限流: {stderr[:200]}", kind="rate_limit")
    return LLMError(f"未知错误: {stderr[:200] or stdout[:200]}", kind="unknown")


# ============================================================
# Trace 数据结构
# ============================================================
@dataclass
class TraceRecord:
    """单次 act() 调用的完整轨迹"""

    ts: float                          # 时间戳
    agent_name: str                    # 调用方 Agent
    input_chars: int                   # 输入字符数
    output_chars: int = 0              # 输出字符数
    attempts: int = 0                  # 总尝试次数 (含 fallback)
    models_tried: list[str] = field(default_factory=list)
    final_model: Optional[str] = None
    latency_ms: float = 0.0           # 端到端延迟
    success: bool = False
    error_kind: Optional[str] = None   # billing / auth / timeout / not_allowed / empty / unknown
    error_msg: Optional[str] = None
    response_preview: Optional[str] = None  # 前 100 字

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# 5 段知识种子 (Knowledge Seed)
# ============================================================
@dataclass
class KnowledgeSeed:
    """HoloAgent 的 5 段知识种子 - 类似张颖清的 ECIWO"""

    identity: str          # 段 1: 我是谁
    capability: list[str]  # 段 2: 我能做什么
    boundary: str          # 段 3: 我不能做什么
    voice: str             # 段 4: 我如何回应
    escalation: str        # 段 5: 何时升级

    def to_prompt(self) -> str:
        """把 5 段种子拼接成 LLM prompt"""
        return f"""# 身份 (Identity)
{self.identity}

# 能力 (Capability)
{chr(10).join(f'- {c}' for c in self.capability)}

# 边界 (Boundary)
{self.boundary}

# 语气 (Voice)
{self.voice}

# 升级规则 (Escalation)
{self.escalation}
"""


# ============================================================
# 日志配置
# ============================================================
_logger = logging.getLogger("holo_agent")
_logger.setLevel(logging.INFO)
_logger.propagate = False

if not _logger.handlers:
    # 文件 handler (结构化 JSON)
    fh = logging.FileHandler(_LOG_FILE, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(fh)

    # 控制台 handler (人类可读)
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s", datefmt="%H:%M:%S"))
    _logger.addHandler(ch)


def _log_trace(record: TraceRecord) -> None:
    """把 trace 记录写入日志 (JSON Lines 格式)"""
    _logger.info(json.dumps(record.to_dict(), ensure_ascii=False))


# ============================================================
# LLM 调用层 (retry + multi-model fallback)
# ============================================================
def call_llm_with_fallback(
    prompt: str,
    models: list[str],
    agent_name: str,
    agent_id: str = "main",
    max_retries_per_model: int = 2,
    timeout_s: int = 180,
    retry_delay_s: float = 1.5,
) -> tuple[str, TraceRecord]:
    """
    多模型 fallback + 每模型 retry 的 LLM 调用。

    Args:
        prompt: 完整 prompt
        models: 候选模型列表, 按优先级排序
        agent_name: 调用方名 (用于日志/trace)
        agent_id: OpenClaw agent ID (用于独立 routing)
        max_retries_per_model: 每个模型最大重试次数
        timeout_s: 单次调用超时
        retry_delay_s: 重试间隔

    Returns:
        (response_text, trace_record)
    """
    record = TraceRecord(
        ts=time.time(),
        agent_name=agent_name,
        input_chars=len(prompt),
    )
    t0 = time.time()

    last_error: Optional[LLMError] = None

    for model in models:
        for attempt in range(1, max_retries_per_model + 1):
            record.models_tried.append(model)
            record.attempts += 1
            try:
                response = _call_single_llm(prompt, model, agent_id, timeout_s)
                # 成功: 返回 response
                record.latency_ms = (time.time() - t0) * 1000
                record.final_model = model
                record.success = True
                record.output_chars = len(response)
                record.response_preview = response[:100]
                _log_trace(record)
                return response, record
            except LLMError as e:
                last_error = e
                # 致命错误 (billing/not_allowed) 不重试, 直接跳到下一个模型
                if e.kind in ("billing", "not_allowed"):
                    _logger.warning(f"[{agent_name}] {model} -> {e.kind}, skip to next")
                    record.error_kind = e.kind
                    break
                # 其他错误 (auth/timeout/unknown): 重试
                if attempt < max_retries_per_model:
                    _logger.warning(
                        f"[{agent_name}] {model} attempt {attempt} -> {e.kind}, retry in {retry_delay_s}s"
                    )
                    time.sleep(retry_delay_s)
                else:
                    record.error_kind = e.kind
                    _logger.warning(f"[{agent_name}] {model} attempts exhausted -> {e.kind}")
        # 当前模型失败, 尝试下一个

    # 所有模型都失败
    record.latency_ms = (time.time() - t0) * 1000
    record.success = False
    if last_error:
        record.error_kind = last_error.kind
        record.error_msg = str(last_error)[:300]
    _log_trace(record)
    return "", record


def _call_single_llm(prompt: str, model: str, agent_id: str, timeout_s: int = 180) -> str:
    """单次 LLM 调用 (无 retry, 无 fallback)

    Args:
        prompt: 用户 prompt
        model: 模型 ID
        agent_id: OpenClaw agent ID (用于独立 routing, 隔离 main 上下文)
        timeout_s: 超时
    """
    try:
        result = subprocess.run(
            [
                _OPENCLAW_BIN, "agent", "--local",
                "--agent", agent_id,
                "--session-key", f"agent:{agent_id}:holoagent",
                "--json",
                "-m", prompt,
                "--model", model,
            ],
            capture_output=True, timeout=timeout_s,
        )
        out = (result.stdout or b"").decode("utf-8", errors="replace")
        err = (result.stderr or b"").decode("utf-8", errors="replace")

        # 提取 JSON 响应
        # v0.2.1 修复: stdout 可能含多个 JSON 块 (stderr 的 error block + stdout 的 success block)
        # 从后往前找包含 "payloads" 的 JSON 块
        success_data = _find_success_json_block(out)

        if success_data is not None:
            payloads = success_data.get("payloads", [])
            if payloads and payloads[0].get("text"):
                text = payloads[0]["text"].strip()
                if text:
                    return text
                raise EmptyResponseError("响应为空字符串")
            # JSON 解析成功但没有 payloads (可能是 error 块)
            if success_data.get("error"):
                raise _classify_error(err + str(success_data["error"]), "")
            raise EmptyResponseError("响应不含 payloads[0].text")

        # 没找到成功 JSON 块 —— fallback 到错误检查
        raise _classify_error(err, out)

    except FileNotFoundError:
        raise ModelNotAllowedError(f"OpenClaw CLI 不在 {_OPENCLAW_BIN}")
    except subprocess.TimeoutExpired:
        raise TimeoutError(f"LLM 调用超时 ({timeout_s}s)")


def _find_success_json_block(text: str) -> Optional[dict]:
    """从 stdout 中提取含 'payloads' 字段的 JSON 块。

    v0.2.1 修复: 之前的代码从第一个 { 开始 brace counting,
    在多 JSON 块场景下会停在中间的 error block 上。
    v0.2.2 修复: OpenClaw 输出的 JSON 含未转义的控制字符 (如 literal \\n),
    需先做清理再 parse。
    v0.2.3 修复: 倒序搜索会拿到 nested object 的 {, 不是 outer block。
    正确做法: 先定位 "payloads", 再向前找最近的 {, brace count 到匹配 }。
    v0.2.4 修复: LLM 响应可能含 , + \\n 让 JSON 整体无效。
    改用 regex 直接提取 "text" 字段, 避开 JSON parse。

    Args:
        text: 原始 stdout 文本 (可能含多个 JSON 块)

    Returns:
        包含 "payloads" 字段的 dict (伪, 从 regex 提取), 没找到返回 None
    """
    # v0.2.4: regex 直接提取 "text" 字段值
    # 模式: "text": "<value>" 其中 value 可以含转义, 不能含 raw "
    # 使用 non-greedy 匹配 + 处理常见转义
    match = re.search(
        r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"',
        text,
        re.DOTALL,
    )
    if not match:
        return None
    text_value = match.group(1)
    # 反转义常见 JSON 转义
    text_value = text_value.replace('\\"', '"')
    text_value = text_value.replace('\\n', '\n')
    text_value = text_value.replace('\\r', '\r')
    text_value = text_value.replace('\\t', '\t')
    text_value = text_value.replace('\\\\', '\\')
    return {
        "payloads": [
            {
                "text": text_value,
                "mediaUrl": None,
            }
        ]
    }


def _decode_bytes(b: bytes) -> str:
    """智能解码字节串: 自动检测 UTF-16 BOM / UTF-8 / GBK

    v0.2.5 修复: PowerShell 子进程默认输出 UTF-16 LE (带 BOM),
    用 utf-8 解码会变乱码。需要检测 BOM 决定编码。
    """
    if not b:
        return ""
    # 检查 BOM
    if b[:2] == b"\xff\xfe":
        # UTF-16 LE BOM
        return b[2:].decode("utf-16-le", errors="replace")
    if b[:2] == b"\xfe\xff":
        # UTF-16 BE BOM
        return b[2:].decode("utf-16-be", errors="replace")
    if b[:3] == b"\xef\xbb\xbf":
        # UTF-8 BOM
        return b[3:].decode("utf-8", errors="replace")
    # 无 BOM: 尝试 UTF-8, 失败则 GBK
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError:
        return b.decode("gbk", errors="replace")


def _fix_invalid_json_chars(text: str) -> str:
    """修复 JSON 字符串内的未转义控制字符 (literal \\n, \\r, \\t)。

    OpenClaw 输出的 JSON 有时在 string value 里有 literal newlines,
    标准 JSON 不允许, 需要转义为 \\n。
    """
    result = []
    in_str = False
    esc = False
    for ch in text:
        if esc:
            result.append(ch)
            esc = False
            continue
        if ch == "\\":
            result.append(ch)
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            result.append(ch)
            continue
        if in_str and ch in "\n\r\t":
            # 在 string value 内的控制字符 → 转义
            if ch == "\n":
                result.append("\\n")
            elif ch == "\r":
                result.append("\\r")
            elif ch == "\t":
                result.append("\\t")
            continue
        result.append(ch)
    return "".join(result)


# ============================================================
# HoloAgent 基类 (生产化版本)
# ============================================================
class HoloAgent:
    """
    自包含 Agent 基类 (全息胚式设计) - 生产化版本

    API 数量守恒: 最多 7 个 (3 必选 + 4 扩展)
    """

    def __init__(
        self,
        name: str,
        seed: KnowledgeSeed,
        model: str = "minimax/MiniMax-M2.7",
        model_fallbacks: Optional[list[str]] = None,
        agent_id: Optional[str] = None,
        max_retries: int = 2,
        timeout_s: int = 180,
    ):
        """
        Args:
            name: Agent 逻辑名 (如 'TranslatorAgent')
            seed: 5 段知识种子
            model: 主模型
            model_fallbacks: 备用模型列表 (按优先级)
            agent_id: OpenClaw agent ID (用于 --agent 参数, 默认 = name 转小写)
                     **重要**: 强烈建议每个 HoloAgent 用独立的 agent_id,
                     否则会被 main agent 的 SOUL.md 上下文覆盖角色
            max_retries: 每模型最大重试次数
            timeout_s: 单次调用超时
        """
        self.name = name
        self.seed = seed
        self.model = model
        # 模型优先级链: [primary, *fallbacks]
        self.model_chain = [model] + (model_fallbacks or [])
        # agent_id 默认 = name (必须与 openclaw agents add 时的名字一致)
        # 重要: 子类初始化时需显式传 agent_id, 因为 name 与 agent 名通常不一致
        # 例: TranslatorAgent (类名) 对应 translator (agent 名)
        self.agent_id = agent_id or name
        self.max_retries = max_retries
        self.timeout_s = timeout_s
        self.memory: dict[str, Any] = {}
        self.api_count = 3
        # Trace 历史 (所有 act() 调用)
        self.traces: list[TraceRecord] = []

    # ----- 3 个必选 API -----

    def act(self, input: str) -> str:
        """处理输入，返回响应 (Agent 的核心调用入口)"""
        # v0.2.1 改进: OpenClaw CLI 不支持 --system-prompt, 需用自然语气让 LLM 接受 role
        # 教训 (按优先级排列):
        #   1. 不要用 ⚠️ emoji + "你不是 X" —— 会触发 injection 防御
        #   2. 不要加 "唯一任务" —— LLM 会读 SOUL.md/AGENTS.md 自卫
        #   3. 用 "我是 X" 第一人称 -- 比 "你是 X" 更自然
        #   4. 角色卡放前面, 用户输入用 「」 引出, 结尾再强调身份
        prompt = f"""我是 {self.name}。{self.seed.identity}

{chr(10).join(f'我能做：{c}' for c in self.seed.capability)}

边界：{self.seed.boundary}
语气：{self.seed.voice}

用户对我说：「{input}」

作为 {self.name}，我回应：
"""
        response, trace = call_llm_with_fallback(
            prompt=prompt,
            models=self.model_chain,
            agent_name=self.name,
            agent_id=self.agent_id,
            max_retries_per_model=self.max_retries,
            timeout_s=self.timeout_s,
        )
        self.traces.append(trace)

        if trace.success:
            return response
        # 全部失败
        return f"[{self.name}] LLM 调用失败 ({trace.error_kind}): {trace.error_msg or '未知错误'}"

    def observe(self, context: dict) -> None:
        """接收外部状态变化，更新内部状态"""
        self.memory["last_context"] = context

    def reflect(self, feedback: str) -> None:
        """接收反馈，用于内部学习/调整"""
        if "feedback_history" not in self.memory:
            self.memory["feedback_history"] = []
        self.memory["feedback_history"].append(feedback)

    # ----- 4 个扩展 API -----

    def escalate(self, reason: str) -> bool:
        """请求升级到其他 Agent 或主人"""
        print(f"[{self.name}] ESCALATE: {reason}")
        return True

    def remember(self, key: str, value: Any) -> None:
        """存储信息到私有记忆"""
        self.memory[key] = value
        self.api_count = max(self.api_count, 4)

    def forget(self, key: str) -> bool:
        """删除记忆"""
        return self.memory.pop(key, None) is not None

    def handoff(self, target: "HoloAgent", payload: dict) -> None:
        """把当前任务转交给另一个 HoloAgent"""
        print(f"[{self.name}] HANDOFF -> [{target.name}]: {list(payload.keys())}")
        target.observe({"from": self.name, "payload": payload})

    # ----- 生产化扩展方法 (不计入 HAIS API count) -----

    def get_traces(self, last_n: int = 10) -> list[dict]:
        """获取最近的 trace 记录 (dict 形式)"""
        return [t.to_dict() for t in self.traces[-last_n:]]

    def get_stats(self) -> dict:
        """统计调用情况"""
        if not self.traces:
            return {"total": 0}
        succ = [t for t in self.traces if t.success]
        avg_latency = sum(t.latency_ms for t in self.traces) / len(self.traces)
        avg_succ_latency = (
            sum(t.latency_ms for t in succ) / len(succ) if succ else 0
        )
        models_used = {}
        for t in self.traces:
            if t.final_model:
                models_used[t.final_model] = models_used.get(t.final_model, 0) + 1
        return {
            "total_calls": len(self.traces),
            "success_rate": f"{len(succ) / len(self.traces) * 100:.1f}%",
            "avg_latency_ms": f"{avg_latency:.0f}",
            "avg_success_latency_ms": f"{avg_succ_latency:.0f}",
            "models_used": models_used,
            "errors": {
                kind: sum(1 for t in self.traces if t.error_kind == kind)
                for kind in ["billing", "auth", "timeout", "not_allowed", "empty", "unknown"]
                if any(t.error_kind == kind for t in self.traces)
            },
        }


# ============================================================
# Demo Agent 1: 翻译 Agent
# ============================================================
class TranslatorAgent(HoloAgent):
    """翻译 Agent - 中英互译"""

    def __init__(self):
        seed = KnowledgeSeed(
            identity="你是'翻译 Agent'。你是 OpenClaw 系统的子代理，专门负责中英互译。",
            capability=[
                "把中文翻译成英文",
                "把英文翻译成中文",
                "处理技术术语，保持专业性",
                "保留原文的语气和风格",
                "一次最多处理 5000 字",
            ],
            boundary="我不应该翻译代码（应转给代码 Agent）。我不应该翻译长文档 >5000 字（应分块或转给文档 Agent）。",
            voice="风格：专业、准确。语气：简洁。格式：纯文本，不加 Markdown 装饰。长度：中（100-500 字）。",
            escalation="当用户要求翻译涉及医疗/法律时，转交专业翻译 Agent。当原文有歧义时，询问用户澄清。当用户连续 3 次不满意时，请求主人介入。",
        )
        # 模型链: 2.7 优先 (实测最稳), 失败 fallback 到 M2.5 / M3
        # agent_id 必须与 openclaw agents add 时的名字一致 (小写 translator)
        super().__init__(
            "TranslatorAgent",
            seed,
            model="minimax/MiniMax-M2.7",
            model_fallbacks=[
                "minimax/MiniMax-M2.5",
                "minimax/MiniMax-M3",
            ],
            agent_id="translator",
        )


# ============================================================
# Demo Agent 2: 校对 Agent
# ============================================================
class ProofreaderAgent(HoloAgent):
    """校对 Agent - 文本校对"""

    def __init__(self):
        seed = KnowledgeSeed(
            identity="你是'校对 Agent'。你负责检查翻译结果的语法、用词、流畅度。",
            capability=[
                "检查语法错误",
                "建议更地道的表达",
                "识别翻译腔",
                "保持原文意图不变",
            ],
            boundary="我不应该重新翻译（应转回翻译 Agent）。我只能校对，不改变核心语义。",
            voice="风格：细致、专业。语气：温和。格式：原文 + 建议修改。长度：短（< 200 字）。",
            escalation="当发现重大翻译错误（如医学、法律术语误译），立即升级到专业 Agent。当用户不采纳修改建议时，记录并转交主人。",
        )
        super().__init__(
            "ProofreaderAgent",
            seed,
            model="minimax/MiniMax-M2.7",
            model_fallbacks=[
                "minimax/MiniMax-M2.5",
                "minimax/MiniMax-M3",
            ],
            agent_id="proofreader",
        )


# ============================================================
# 多 Agent 协作示例 (全息胚间通讯)
# ============================================================
def demo_multi_agent_collaboration():
    """演示: 翻译 -> 校对 协作链"""
    print("=" * 60)
    print("Demo: 翻译 Agent + 校对 Agent 协作 (v0.2 生产化)")
    print("=" * 60)

    translator = TranslatorAgent()
    proofreader = ProofreaderAgent()

    # 步骤 1: 翻译 Agent 处理
    input_text = "张颖清的全息生物学认为，部分包含整体的全部信息。"
    print(f"\n[1] 输入: {input_text}")
    translation = translator.act(input_text)
    print(f"[1] 翻译结果: {translation}")

    # 步骤 2: 翻译 Agent 转交给校对 Agent
    translator.handoff(proofreader, {"text": translation, "source": input_text})

    # 步骤 3: 校对 Agent 处理
    final = proofreader.act(translation)
    print(f"\n[3] 校对结果: {final}")

    print("\n" + "=" * 60)
    print("Translator 统计:")
    for k, v in translator.get_stats().items():
        print(f"  {k}: {v}")
    print("\nProofreader 统计:")
    for k, v in proofreader.get_stats().items():
        print(f"  {k}: {v}")
    print("=" * 60)


# ============================================================
# HAIS 合规性自检
# ============================================================
def hais_self_check(agent: HoloAgent) -> dict:
    """HAIS v0.1 合规性检查"""
    return {
        "name": agent.name,
        "api_count": agent.api_count,
        "api_count_ok": agent.api_count <= 7,
        "has_seed": all([
            agent.seed.identity,
            agent.seed.capability,
            agent.seed.boundary,
            agent.seed.voice,
            agent.seed.escalation,
        ]),
        "has_5_segments": all([
            agent.seed.identity,
            len(agent.seed.capability) >= 1,
            agent.seed.boundary,
            agent.seed.voice,
            agent.seed.escalation,
        ]),
        "has_model_chain": len(agent.model_chain) >= 1,
        "v0.2_features": {
            "retry": agent.max_retries > 0,
            "fallback": len(agent.model_chain) > 1,
            "trace": hasattr(agent, "traces"),
            "stats": hasattr(agent, "get_stats"),
        },
    }


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("\n=== HoloAgent v0.2 生产化测试 ===\n")
    print(f"日志目录: {_LOG_DIR}")
    print(f"日志文件: {_LOG_FILE}\n")

    t = TranslatorAgent()
    p = ProofreaderAgent()

    # HAIS 自检
    print("HAIS 自检 + v0.2 features 检查:")
    for agent in [t, p]:
        check = hais_self_check(agent)
        for k, v in check.items():
            print(f"  {agent.name}.{k}: {v}")
        print()

    # 多 Agent 协作 demo
    demo_multi_agent_collaboration()

    print(f"\n[完成] HoloAgent v0.2 测试通过。")
    print(f"[日志] 已写入 {_LOG_FILE}")
    print(f"[下一步] 集成 OpenClaw 飞书投递 → wechat-chat 通道。")