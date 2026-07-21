"""
seed.py - 5 段知识种子 (Knowledge Seed)

全息胚类比：5 段种子 = 数字全息胚的 5 个功能区
v0.2 扩展：新增 metadata / memory / collaboration / health 段落

标准参考：8.8-hais-v0.2-design.md §3.1, 8.9-holoagent-v1.0-design.md §4.1
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class KnowledgeSeed:
    """HAIS 5 段知识种子

    每个 HoloAgent 通过这 5 段种子定义自己的"全息身份"。
    v0.2 在 5 段基础上增加了可选的扩展段。

    Attributes:
        identity:   段 1 — 我是谁 (Agent 身份声明)
        capability: 段 2 — 我能做什么 (能力列表)
        boundary:   段 3 — 我不能做什么 / 边界条件
        voice:      段 4 — 我如何回应 (语气、风格、格式)
        escalation: 段 5 — 何时升级 / 何时求助

        metadata (v0.2 新增):   元信息 (创建时间、标签、分类)
        memory (v0.2 新增):     记忆配置 (各层开关、隔离级别)
        collaboration (v0.2 新增): 协作配置 (角色、模式、并发)
        health (v0.2 新增):     健康检查端点、超时、重试
    """

    # ── 5 段必选种子 ──
    identity: str
    """我是谁：Agent 的身份声明，如"你是翻译 Agent，专门负责中英互译"。"""

    capability: list[str]
    """我能做什么：能力列表，每项一句，如["把中文翻译成英文", "技术术语保持专业"]。"""

    boundary: str
    """边界：不能做什么，如"不翻译代码"、"不处理长文档"。"""

    voice: str
    """语气风格：如"风格专业、语气简洁、输出纯文本"。"""

    escalation: str
    """升级规则：何时转交人或更专业的 Agent。"""

    # ── v0.2 扩展段 (可选) ──
    metadata: dict = field(default_factory=lambda: {
        "tags": [],
        "category": "general",
    })
    """元信息：agent 版本、标签、分类等。"""

    memory: dict = field(default_factory=lambda: {
        "working": True,
        "short_term": True,
        "long_term": False,  # 默认关闭，需要显式启用
        "isolation": "strict",
    })
    """记忆配置：各层开关、隔离级别 (strict / shared / public)。"""

    collaboration: dict = field(default_factory=lambda: {
        "role": "worker",
        "max_concurrent": 3,
        "preferred_modes": ["sequential", "parallel"],
    })
    """协作配置：角色 (master/worker/peer)、并发上限、偏好模式。"""

    health: dict = field(default_factory=lambda: {
        "timeout_s": 30,
        "retry": 3,
    })
    """健康检查配置：超时、重试次数。"""

    def to_prompt(self) -> str:
        """把 5 段种子拼接成 LLM prompt

        用于 HoloAgent.act() 的 prompt 构建。
        v0.2 版本采用自然语气 + "我是 X" 第一人称。
        """
        lines = [
            f"# 身份 (Identity)",
            self.identity,
            "",
            "# 能力 (Capability)",
        ]
        lines.extend(f"- {c}" for c in self.capability)
        lines += [
            "",
            "# 边界 (Boundary)",
            self.boundary,
            "",
            "# 语气 (Voice)",
            self.voice,
            "",
            "# 升级规则 (Escalation)",
            self.escalation,
        ]
        return "\n".join(lines)

    def validate(self) -> list[str]:
        """验证 5 段种子是否完整，返回缺失项列表"""
        errors = []
        if not self.identity or len(self.identity.strip()) < 5:
            errors.append("identity: 必须 >= 5 字符")
        if not self.capability or len(self.capability) < 1:
            errors.append("capability: 至少需要 1 项能力")
        if not self.boundary or len(self.boundary.strip()) < 5:
            errors.append("boundary: 必须 >= 5 字符")
        if not self.voice or len(self.voice.strip()) < 5:
            errors.append("voice: 必须 >= 5 字符")
        if not self.escalation or len(self.escalation.strip()) < 5:
            errors.append("escalation: 必须 >= 5 字符")
        return errors

    def to_dict(self) -> dict:
        """序列化为 dict"""
        return {
            "identity": self.identity,
            "capability": self.capability,
            "boundary": self.boundary,
            "voice": self.voice,
            "escalation": self.escalation,
            "metadata": self.metadata,
            "memory": self.memory,
            "collaboration": self.collaboration,
            "health": self.health,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeSeed":
        """从 dict 反序列化"""
        return cls(
            identity=data.get("identity", ""),
            capability=data.get("capability", []),
            boundary=data.get("boundary", ""),
            voice=data.get("voice", ""),
            escalation=data.get("escalation", ""),
            metadata=data.get("metadata", {}),
            memory=data.get("memory", {}),
            collaboration=data.get("collaboration", {}),
            health=data.get("health", {}),
        )


# ── 预设种子模板 ──

def translator_seed() -> KnowledgeSeed:
    """翻译 Agent 的种子模板"""
    return KnowledgeSeed(
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
    )


def proofreader_seed() -> KnowledgeSeed:
    """校对 Agent 的种子模板"""
    return KnowledgeSeed(
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
        collaboration={"role": "worker", "max_concurrent": 3, "preferred_modes": ["sequential"]},
    )


def summarizer_seed() -> KnowledgeSeed:
    """摘要 Agent 的种子模板"""
    return KnowledgeSeed(
        identity="你是'摘要 Agent'。你负责把长篇内容压缩为简洁摘要。",
        capability=[
            "把长文本（1000-10000 字）压缩为 200 字以内的摘要",
            "保留关键信息和核心论点",
            "按重要性排序输出要点",
            "支持中英文摘要",
        ],
        boundary="我不翻译。我不改写风格。我不添加原文没有的信息。我不处理图像内容。",
        voice="风格：精炼、客观。语气：中性。格式：要点列表或段落。长度：短（<200 字）。",
        escalation="当原文有严重矛盾时，标记矛盾点并询问主人。",
        metadata={"tags": ["summarization", "nlp"], "category": "nlp"},
        collaboration={"role": "worker", "max_concurrent": 5, "preferred_modes": ["parallel"]},
    )
