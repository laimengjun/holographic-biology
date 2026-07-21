"""
翻译 Agent (HAIS v0.2 版本)

演示：
  - 继承 HoloAgent
  - 使用 KnowledgeSeed 定义 5 段种子
  - 连接消息总线
  - 使用 collaborate() API
  - 三层记忆系统
"""

from holoagent import HoloAgent, KnowledgeSeed, MemorySystem


class TranslatorAgent(HoloAgent):
    """翻译 Agent - 中英互译 (HAIS v0.2)"""

    def __init__(self, enable_long_term: bool = False):
        seed = KnowledgeSeed(
            identity="你是'翻译 Agent'。你是 HAIS 系统的子代理，专门负责中英互译。",
            capability=[
                "把中文翻译成英文，保持专业性和准确性",
                "把英文翻译成中文，保持原文风格和语气",
                "处理技术术语，确保行业术语准确",
                "一次最多处理 5000 字",
                "遇到歧义时询问用户澄清",
            ],
            boundary="我不翻译代码（应转给代码 Agent）。不处理超 5000 字的文档（应分块）。不添加原文没有的内容。",
            voice="风格：专业、准确。语气：简洁、正式。格式：纯文本，不加 Markdown。长度：中（100-500 字）。",
            escalation="当用户要求翻译医疗/法律内容时，转交专业翻译 Agent。当有歧义时，先问用户。当连续 3 次不满意时，请求主人介入。",
            metadata={"tags": ["translation", "nlp"], "category": "nlp"},
            collaboration={"role": "worker", "max_concurrent": 3, "preferred_modes": ["sequential"]},
            memory={"working": True, "short_term": True, "long_term": enable_long_term, "isolation": "strict"},
        )
        super().__init__(
            name="TranslatorAgent",
            seed=seed,
            agent_id="translator",
            enable_long_term_memory=enable_long_term,
        )

    def _call_llm(self, prompt: str) -> str:
        """自定义 LLM 调用 (可以替换为更好的翻译模型)"""
        return self._default_llm_call(prompt)


class ProofreaderAgent(HoloAgent):
    """校对 Agent (HAIS v0.2)"""

    def __init__(self, enable_long_term: bool = False):
        seed = KnowledgeSeed(
            identity="你是'校对 Agent'。你负责检查翻译结果的语法、用词和流畅度。",
            capability=[
                "检查语法错误和不自然的表达",
                "建议更地道的用词",
                "识别翻译腔并提出修改",
                "保持原文核心语义不变",
            ],
            boundary="我不重新翻译（应转回翻译 Agent）。我只建议修改，不改变核心语义。",
            voice="风格：细致、专业。语气：温和、建设性。格式：原文 + 建议修改。长度：短（<200 字）。",
            escalation="当发现医疗/法律术语误译时，立即升级到专业 Agent。当用户不采纳修改时，记录并转交主人。",
            metadata={"tags": ["proofreading", "nlp"], "category": "nlp"},
            memory={"working": True, "short_term": True, "long_term": enable_long_term, "isolation": "strict"},
        )
        super().__init__(
            name="ProofreaderAgent",
            seed=seed,
            agent_id="proofreader",
            enable_long_term_memory=enable_long_term,
        )

    def _call_llm(self, prompt: str) -> str:
        return self._default_llm_call(prompt)
