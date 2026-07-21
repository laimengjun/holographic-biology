"""
core.py - HoloAgent 基类 (HAIS v0.2 升级版)

全息胚类比：每个 HoloAgent = 一个数字全息胚
  - 5 段种子 = Agent 的基因组 (identity, capability, boundary, voice, escalation)
  - 7 API = Agent 的接口穴位 (act, observe, reflect, escalate, remember, forget, collaborate)
  - 三层记忆 = Agent 的经验系统 (working, short-term, long-term)
  - 消息总线 = Agent 的神经递质系统

v0.2 相对 v0.1 的关键升级 (8.8-hais-v0.2-design.md):
  1. 记忆隔离 — 每个 Agent 独立的 3 层记忆
  2. collaborate() — 多对多协作 (取代 handoff())
  3. 持久化记忆 — 跨 session 经验
  4. 身份认证 — 签名 + ACL

API 数量守恒：≤ 7 (6 内部 + 1 外部)
  - 内部: act / observe / reflect / escalate / remember / forget
  - 外部: collaborate
"""

from __future__ import annotations
import logging
import time
from pathlib import Path
from typing import Any, Optional

from .seed import KnowledgeSeed
from .memory import MemorySystem


# ============================================================
# 日志配置
# ============================================================

_logger = logging.getLogger("holoagent.core")


# ============================================================
# HoloAgent 基类 (v0.2)
# ============================================================

class HoloAgent:
    """HAIS v0.2 兼容的 HoloAgent 基类

    用法：
        class MyAgent(HoloAgent):
            def __init__(self):
                seed = KnowledgeSeed(
                    identity="...",
                    capability=[...],
                    boundary="...",
                    voice="...",
                    escalation="...",
                )
                super().__init__("MyAgent", seed, agent_id="myagent")
    """

    def __init__(
        self,
        name: str,
        seed: KnowledgeSeed,
        agent_id: Optional[str] = None,
        enable_long_term_memory: bool = False,
        memory_db_path: Optional[str] = None,
        log_level: int = logging.INFO,
    ):
        """
        Args:
            name: Agent 逻辑名 (如 "TranslatorAgent")
            seed: 5 段知识种子
            agent_id: OpenClaw agent ID (用于独立 routing, 默认 = name 转小写)
            enable_long_term_memory: 是否启用长期记忆
            memory_db_path: 短期记忆 SQLite 路径 (默认 ./data/ 下)
            log_level: 日志级别
        """
        self.name = name
        self.seed = seed
        self.agent_id = agent_id or name.lower()

        # ── API 守恒计数 ──
        self._api_count = 3  # act + observe + reflect (必选)

        # ── 记忆系统 (v0.2 核心新增) ──
        self.memory = MemorySystem(
            agent_id=self.agent_id,
            enable_long_term=enable_long_term_memory,
            short_term_db=memory_db_path,
        )

        # ── 消息总线连接 (v0.2 新增, 由 collaborator 注入) ──
        self._bus = None  # HoloMessageBus 实例
        self._collaborator = None  # Collaborate 实例

        # ── 内部状态 ──
        self._start_time = time.time()
        self._call_count = 0
        self._trace: list[dict] = []
        self._setup_logging(log_level)

    def _setup_logging(self, level: int) -> None:
        self.log = logging.getLogger(f"holoagent.{self.agent_id}")
        self.log.setLevel(level)
        if not self.log.handlers:
            ch = logging.StreamHandler()
            ch.setFormatter(logging.Formatter(
                f"[%(asctime)s] [{self.agent_id}] %(levelname)s %(message)s",
                datefmt="%H:%M:%S",
            ))
            self.log.addHandler(ch)

    # ================================================================
    # 3 个必选 API
    # ================================================================

    def act(self, input_text: str, context: dict = None) -> str:
        """核心行为 API：处理输入，返回响应

        这是 Agent 的核心方法，继承类应重写此方法以自定义行为。
        默认实现使用 5 段种子构建 prompt 并调用 LLM。

        Args:
            input_text: 用户输入
            context: 额外上下文 (可选)

        Returns:
            文本响应
        """
        self._call_count += 1

        # 自动记录到短期记忆
        self.memory.append("user", input_text, metadata={"context": context or {}})

        # 构建 prompt (5 段种子 + 记忆上下文)
        prompt = self._build_prompt(input_text, context)

        # 记录 start
        t0 = time.time()

        # LLM 调用 — 子类可重写
        response = self._call_llm(prompt)

        latency = (time.time() - t0) * 1000

        # 自动记录响应
        self.memory.append("assistant", response)

        # trace
        self._trace.append({
            "ts": t0,
            "type": "act",
            "input_chars": len(input_text),
            "output_chars": len(response),
            "latency_ms": latency,
        })

        return response

    def observe(self, context: dict) -> None:
        """观察 API：接收外部状态变化

        用于接收：
          - 其他 Agent 的协作消息
          - 环境状态变化
          - 用户输入前的情境

        Args:
            context: 外部状态字典
        """
        self.memory.set("last_context", context)
        self.log.debug(f"Observed context: {list(context.keys())[:3]}...")

    def reflect(self, feedback: str, metadata: dict = None) -> None:
        """反思 API：接收反馈，用于内部学习

        v0.2 增强：自动评估反馈重要性，重要内容写入长期记忆

        Args:
            feedback: 反馈文本
            metadata: 可选的元信息 (如 {"importance": 0.8})
        """
        meta = metadata or {}
        # 标记为反思来源
        meta["is_reflection"] = True
        # 写入短期记忆
        self.memory.append("reflection", feedback, metadata=meta)
        # 如果重要性高且长期记忆启用，直接提升
        if self.memory.long and self.memory._enable_long:
            from .memory import calculate_importance
            imp = calculate_importance(feedback, meta)
            if imp >= 0.7:
                self.memory.store(feedback, metadata=meta, importance=imp)
                self.log.info(f"Auto-promoted reflection to long-term (importance={imp:.2f})")

    # ================================================================
    # 4 个扩展 API (v0.2 升级版)
    # ================================================================

    def escalate(self, reason: str, target: str = "human") -> bool:
        """升级 API：请求升级到其他 Agent 或主人

        v0.2 增强：支持升级到人 + 升级到 Agent

        Args:
            reason: 升级原因
            target: 目标 ("human" 或 agent_id)

        Returns:
            是否成功
        """
        self.log.warning(f"ESCALATE -> {target}: {reason}")
        self.memory.set("last_escalation", {
            "reason": reason,
            "target": target,
            "ts": time.time(),
        })
        # 通知消息总线 (如果已连接)
        if self._bus:
            self._bus.publish("system:escalation", {
                "from": self.agent_id,
                "reason": reason,
                "target": target,
            })
        return True

    def remember(self, key: str, value: Any, ttl: float = None) -> None:
        """记住 API：存储信息到工作记忆

        v0.2: 统一使用 MemorySystem

        Args:
            key: 键
            value: 值
            ttl: 过期秒数
        """
        self.memory.set(key, value, ttl)
        self._api_count = max(self._api_count, 4)

    def forget(self, key: str) -> bool:
        """忘记 API：删除工作记忆中的信息

        Returns:
            是否成功删除
        """
        return self.memory.working.delete(key)

    def collaborate(self, mode: str, target: str | list[str] = None,
                    payload: dict = None, timeout: int = 30) -> Any:
        """协作 API (v0.2 核心新增)：跨 Agent 协作

        取代 handoff()，支持多对多协作。

        Args:
            mode: 协作模式 (request / broadcast / gather / chain / vote / consensus)
            target: 目标 Agent ID (单个或列表, None = 广播所有)
            payload: 消息体
            timeout: 超时秒数

        Returns:
            协作结果

        Raises:
            RuntimeError: 消息总线未连接
        """
        if self._collaborator is None:
            raise RuntimeError(
                "collaborate() 需要消息总线支持。"
                "请先调用 connect_bus(bus) 或使用 HoloAgent.with_bus(bus) 创建。"
            )
        self._api_count = max(self._api_count, 7)
        return self._collaborator.execute(self.agent_id, mode, target, payload, timeout)

    # ================================================================
    # 消息总线连接 (v0.2)
    # ================================================================

    def connect_bus(self, bus) -> None:
        """连接到消息总线

        Args:
            bus: HoloMessageBus 实例
        """
        self._bus = bus
        from .collaborator import Collaborate
        self._collaborator = Collaborate(bus)
        self.log.info(f"Connected to message bus (id={id(bus)})")

    @classmethod
    def with_bus(cls, *args, bus=None, **kwargs) -> "HoloAgent":
        """创建 Agent 并连接到总线 (工厂方法)"""
        agent = cls(*args, **kwargs)
        if bus:
            agent.connect_bus(bus)
        return agent

    # ================================================================
    # 内部方法
    # ================================================================

    def _build_prompt(self, input_text: str, context: dict = None) -> str:
        """构建 LLM prompt：5 段种子 + 记忆上下文

        v0.2 增强：加入短期记忆上下文中的相关记录
        """
        # 基础 prompt (5 段种子)
        prompt = f"""我是 {self.name}。{self.seed.identity}

{chr(10).join(f'我能做：{c}' for c in self.seed.capability)}

边界：{self.seed.boundary}
语气：{self.seed.voice}

"""

        # 如果有相关记忆，加入上下文
        short_memories = self.memory.search(input_text, top_k=3).get("short", [])
        if short_memories:
            context_lines = []
            for m in short_memories[:3]:
                context_lines.append(f"  [{m.role}]: {m.content[:200]}")
            prompt += "相关上下文：\n" + "\n".join(context_lines) + "\n\n"

        prompt += f"""用户对我说：「{input_text}」

作为 {self.name}，我回应：
"""
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """LLM 调用 — 子类可重写

        默认返回一个占位响应。实际使用应继承重写。
        参考 holo_agent_v0.2.py 的 call_llm_with_fallback()。
        """
        # v0.2.6 兼容: 使用 OpenClaw CLI
        return self._default_llm_call(prompt)

    def _default_llm_call(self, prompt: str) -> str:
        """默认 LLM 调用 (使用 OpenClaw CLI, 兼容 v0.2.6)

        子类可以重写 _call_llm 来替换此实现。
        """
        import shutil
        import subprocess

        openclaw_bin = shutil.which("openclaw") or "C:\\Users\\ThinkPad\\AppData\\Roaming\\npm\\openclaw.CMD"

        models = [
            "minimax/MiniMax-M2.7",
            "minimax/MiniMax-M2.5",
            "minimax/MiniMax-M3",
        ]

        last_error = None
        for model in models:
            try:
                result = subprocess.run(
                    [
                        openclaw_bin, "agent", "--local",
                        "--agent", self.agent_id,
                        "--session-key", f"agent:{self.agent_id}:holoagent",
                        "--json",
                        "-m", prompt,
                        "--model", model,
                    ],
                    capture_output=True, timeout=180,
                )
                stdout = (result.stdout or b"").decode("utf-8", errors="replace")
                stderr = (result.stderr or b"").decode("utf-8", errors="replace")

                # 用 regex 提取 "text" 字段
                import re
                match = re.search(
                    r'"text"\s*:\s*"((?:[^"\\]|\\.)*)"',
                    stdout, re.DOTALL,
                )
                if match:
                    text = match.group(1)
                    text = text.replace('\\"', '"').replace('\\n', '\n')
                    text = text.replace('\\r', '\r').replace('\\t', '\t')
                    text = text.replace('\\\\', '\\')
                    if text.strip():
                        return text.strip()

                # JSON 有效但没有 text 字段
                try:
                    data = json.loads(stdout)
                    if data.get("payloads") and data["payloads"][0].get("text"):
                        return data["payloads"][0]["text"]
                except json.JSONDecodeError:
                    pass

                last_error = stderr[:200] or stdout[:200]

            except subprocess.TimeoutExpired:
                last_error = f"timeout ({model})"
            except Exception as e:
                last_error = str(e)

        return f"[{self.name}] LLM 调用失败: {last_error or '未知错误'}"

    # ================================================================
    # 工具方法
    # ================================================================

    def get_stats(self) -> dict:
        """Agent 统计"""
        elapsed = time.time() - self._start_time
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "uptime_s": elapsed,
            "api_count": self._api_count,
            "call_count": self._call_count,
            "memory_stats": self.memory.stats(),
            "bus_connected": self._bus is not None,
        }

    def get_recent_trace(self, n: int = 10) -> list[dict]:
        """最近 n 次 trace"""
        return self._trace[-n:]

    @property
    def api_count(self) -> int:
        """当前使用的 API 数量 (用于守恒检查)"""
        return self._api_count

    @api_count.setter
    def api_count(self, value: int):
        self._api_count = min(value, 7)

    # ================================================================
    # HAIS 合规自检
    # ================================================================

    def hais_check(self) -> dict:
        """HAIS v0.2 合规性检查"""
        return {
            "name": self.name,
            "agent_id": self.agent_id,
            "standard": "HAIS v0.2",
            "has_5_seeds": all([
                bool(self.seed.identity),
                len(self.seed.capability) >= 1,
                bool(self.seed.boundary),
                bool(self.seed.voice),
                bool(self.seed.escalation),
            ]),
            "api_count": self._api_count,
            "api_count_ok": self._api_count <= 7,
            "memory_system": {
                "working": self.memory.working is not None,
                "short_term": self.memory.short is not None,
                "long_term": self.memory._enable_long,
            },
            "collaboration_ready": self._collaborator is not None,
            "bus_connected": self._bus is not None,
        }


# ============================================================
# 预设 Agent 类 (v0.2 版本)
# ============================================================

class TranslatorAgent(HoloAgent):
    """翻译 Agent (HAIS v0.2)"""

    def __init__(self, enable_long_term: bool = False):
        from .seed import translator_seed
        super().__init__(
            name="TranslatorAgent",
            seed=translator_seed(),
            agent_id="translator",
            enable_long_term_memory=enable_long_term,
        )


class ProofreaderAgent(HoloAgent):
    """校对 Agent (HAIS v0.2)"""

    def __init__(self, enable_long_term: bool = False):
        from .seed import proofreader_seed
        super().__init__(
            name="ProofreaderAgent",
            seed=proofreader_seed(),
            agent_id="proofreader",
            enable_long_term_memory=enable_long_term,
        )


class SummarizerAgent(HoloAgent):
    """摘要 Agent (HAIS v0.2)"""

    def __init__(self, enable_long_term: bool = False):
        from .seed import summarizer_seed
        super().__init__(
            name="SummarizerAgent",
            seed=summarizer_seed(),
            agent_id="summarizer",
            enable_long_term_memory=enable_long_term,
        )
