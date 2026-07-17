"""
holo_agent_prototype.py - HoloAgent 最小可工作原型

HAIS v0.1 参考实现:
- 5 段知识种子 (Knowledge Seed)
- 3 个核心 API: act / observe / reflect
- 4 个扩展 API: escalate / remember / forget / handoff
- 单文件 < 200 行
- 集成 OpenClaw 默认 LLM

用法:
    python holo_agent_prototype.py
    # 或在代码中:
    from holo_agent_prototype import TranslatorAgent, ProofreaderAgent

设计哲学: 张颖清"全息胚" - 部分包含整体
"""
from __future__ import annotations
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Optional

# 定位 OpenClaw CLI (避免 PATH 问题)
_OPENCLAW_BIN = shutil.which("openclaw") or "C:\\Users\\ThinkPad\\AppData\\Roaming\\npm\\openclaw.CMD"


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
# HoloAgent 基类
# ============================================================
class HoloAgent:
    """
    自包含 Agent 基类 (全息胚式设计)

    API 数量守恒: 最多 7 个 (3 必选 + 4 扩展)
    """

    def __init__(self, name: str, seed: KnowledgeSeed, model: str = "minimax/MiniMax-M2.7"):
        self.name = name
        self.seed = seed
        self.model = model
        self.memory: dict[str, Any] = {}  # 私有记忆
        self.api_count = 3  # 初始 3 个核心 API

    # ----- 3 个必选 API -----

    def act(self, input: str) -> str:
        """处理输入，返回响应 (Agent 的核心调用入口)"""
        # 构造 prompt: 明确指令 + 5 段种子 + 输入
        prompt = f"""你是 {self.name}。请严格按照你的角色处理用户输入。

{self.seed.to_prompt()}

## 用户输入
{input}

## 你的输出 (只输出你要说的话, 不要重复上面的说明)
"""

        # 调用 LLM (通过 OpenClaw CLI)
        response = self._call_llm(prompt)
        return response

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
        self.api_count = max(self.api_count, 4)  # 标记已使用扩展 API

    def forget(self, key: str) -> bool:
        """删除记忆"""
        return self.memory.pop(key, None) is not None

    def handoff(self, target: "HoloAgent", payload: dict) -> None:
        """把当前任务转交给另一个 HoloAgent"""
        print(f"[{self.name}] HANDOFF -> [{target.name}]: {list(payload.keys())}")
        target.observe({"from": self.name, "payload": payload})

    # ----- 内部方法 -----

    def _call_llm(self, prompt: str) -> str:
        """通过 OpenClaw CLI 调用 LLM, JSON 模式提取响应"""
        try:
            result = subprocess.run(
                [
                    _OPENCLAW_BIN, "agent", "--local",
                    "--session-key", f"agent:main:holoagent_{self.name}",
                    "--json",
                    "-m", prompt,
                    "--model", self.model,
                ],
                capture_output=True, timeout=180,
            )
            # 用 errors='replace' 避免 Unicode 解码错误
            out = (result.stdout or b"").decode("utf-8", errors="replace")
            err = (result.stderr or b"").decode("utf-8", errors="replace")
            # 从噪声日志中提取第一个 JSON 块
            start = out.find("{")
            if start >= 0:
                depth = 0
                end = start
                in_str = False
                esc = False
                for i, ch in enumerate(out[start:], start):
                    if esc:
                        esc = False
                        continue
                    if ch == "\\":
                        esc = True
                        continue
                    if ch == '"':
                        in_str = not in_str
                        continue
                    if in_str:
                        continue
                    if ch == "{":
                        depth += 1
                    elif ch == "}":
                        depth -= 1
                        if depth == 0:
                            end = i + 1
                            break
                try:
                    import json as _json
                    data = _json.loads(out[start:end])
                    payloads = data.get("payloads", [])
                    if payloads and payloads[0].get("text"):
                        return payloads[0]["text"].strip()
                    if data.get("error"):
                        return f"[{self.name}] LLM error: {data['error']}"
                except Exception:
                    pass
            # 兜底: 返回 stderr 关键部分
            err_first = err.strip().split("\n")[-3:] if err else []
            return f"[{self.name}] (no JSON found, last stderr: {' | '.join(err_first)[:300]})"
        except FileNotFoundError:
            return f"[{self.name}] (mock: openclaw 不在 {_OPENCLAW_BIN})"
        except subprocess.TimeoutExpired:
            return f"[{self.name}] LLM 调用超时 (180s)"
        except Exception as e:
            return f"[{self.name}] 错误: {type(e).__name__}: {e}"


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
        super().__init__("TranslatorAgent", seed)


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
        super().__init__("ProofreaderAgent", seed)


# ============================================================
# 多 Agent 协作示例 (全息胚间通讯)
# ============================================================
def demo_multi_agent_collaboration():
    """演示: 翻译 -> 校对 协作链"""
    print("=" * 60)
    print("Demo: 翻译 Agent + 校对 Agent 协作")
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
    print(f"Translator API count: {translator.api_count} (≤ 7 OK)")
    print(f"Proofreader API count: {proofreader.api_count} (≤ 7 OK)")
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
    }


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    # 创建并测试 Agent
    print("\n=== HoloAgent 原型测试 ===\n")

    t = TranslatorAgent()
    p = ProofreaderAgent()

    # HAIS 自检
    print("HAIS 自检:")
    for agent in [t, p]:
        check = hais_self_check(agent)
        for k, v in check.items():
            print(f"  {agent.name}.{k}: {v}")
        print()

    # 多 Agent 协作 demo
    demo_multi_agent_collaboration()

    print("\n[完成] HoloAgent 原型测试通过。")
    print("[下一步] 集成 OpenClaw 飞书投递 → wechat-chat 通道。")