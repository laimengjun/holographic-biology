"""
holoagent - HAIS v0.2 实现包

HAIS = Holographic Agent Interaction Standard
每个 Agent = 数字全息胚，5段种子 = 5功能区，7 API = 7穴位

模块清单:
  core.py       - HoloAgent 基类 (v0.2 升级版)
  seed.py       - 5 段知识种子
  memory.py     - 3 层记忆系统 (工作/短期/长期)
  message_bus.py- HoloMessage Protocol v1.0 消息总线
  collaborator.py- collaborate() API + 协作模式
  orchestrator.py- 任务分解 + Agent 调度
  security.py   - 身份认证 + 签名 + ACL
"""

__version__ = "0.2.0"
__standard__ = "HAIS v0.2"
__author__ = "laimengjun@amoy 2026 — CC BY 4.0"

from .core import HoloAgent
from .seed import KnowledgeSeed
from .memory import (
    WorkingMemory,
    ShortTermMemory,
    LongTermMemory,
    MemorySystem,
)
from .collaborator import (
    Collaborate,
    Workflow,
    CollaborationMode,
)

__all__ = [
    "HoloAgent",
    "KnowledgeSeed",
    "WorkingMemory",
    "ShortTermMemory",
    "LongTermMemory",
    "MemorySystem",
    "Collaborate",
    "Workflow",
    "CollaborationMode",
]
