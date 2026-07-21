"""
security.py - HAIS v0.2 身份认证 + 消息签名 + ACL

参考：8.8-hais-v0.2-design.md §3.4, §8

设计原则:
  1. 每个 Agent 有唯一身份 (Agent ID)
  2. 消息签名验证 (HMAC-SHA256)
  3. 访问控制 (ACL: 读/写/执行)
  4. 加密支持 (可选，敏感消息用 Fernet)
  5. 最小权限原则
"""

from __future__ import annotations
import hashlib
import hmac
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


# ============================================================
# 身份认证
# ============================================================

@dataclass
class AgentIdentity:
    """Agent 身份信息

    参考：8.8-hais-v0.2-design.md §3.4.1
    """
    agent_id: str                         # 全局唯一 ID
    display_name: str = ""                # 显示名
    public_key: str = ""                  # 公钥 (用于消息验证)
    created_at: float = 0.0               # 创建时间
    tags: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "display_name": self.display_name,
            "public_key": self.public_key[:20] + "..." if len(self.public_key) > 20 else self.public_key,
            "created_at": self.created_at,
            "tags": self.tags,
        }


# ============================================================
# 消息签名
# ============================================================

class MessageSigner:
    """消息签名 / 验证 (HMAC-SHA256)

    参考：8.8-hais-v0.2-design.md §8.2

    用法：
        signer = MessageSigner()
        agent_a_secret = signer.generate_secret()
        agent_b_secret = signer.generate_secret()

        msg = {"from": "a", "to": "b", "payload": "hello"}
        sig = signer.sign(msg, agent_a_secret)
        assert signer.verify(msg, sig, agent_a_secret)  # ✅
        assert not signer.verify(msg, sig, agent_b_secret)  # ❌
    """

    @staticmethod
    def generate_secret(length: int = 32) -> str:
        """生成 agent 密钥

        Args:
            length: 字节数

        Returns:
            十六进制密钥字符串
        """
        return uuid.uuid4().hex[:length * 2]

    @staticmethod
    def sign(message: dict, secret_key: str) -> str:
        """HMAC-SHA256 签名

        对 dict 先按 key 排序再 JSON 序列化，确保签名可重现。

        Args:
            message: 要签名的消息 (dict)
            secret_key: Agent 密钥

        Returns:
            十六进制签名字符串
        """
        msg_str = json.dumps(message, sort_keys=True, separators=(",", ":"))
        return hmac.new(
            secret_key.encode(),
            msg_str.encode(),
            hashlib.sha256,
        ).hexdigest()

    @staticmethod
    def verify(message: dict, signature: str, secret_key: str) -> bool:
        """验证 HMAC-SHA256 签名"""
        expected = MessageSigner.sign(message, secret_key)
        return hmac.compare_digest(expected, signature)

    @staticmethod
    def sign_holo_message(msg_dict: dict, secret_key: str) -> str:
        """对 HoloMessage dict 签名 (排除已有 signature 字段)"""
        clean = {k: v for k, v in msg_dict.items() if k != "signature"}
        return MessageSigner.sign(clean, secret_key)


# ============================================================
# 加密 (可选)
# ============================================================

class MessageEncryptor:
    """消息加密 (Fernet 对称加密)

    用于敏感消息的端到端加密。
    需要 cryptography 库。

    pip install cryptography
    """

    @staticmethod
    def generate_key() -> str:
        """生成 Fernet 密钥"""
        try:
            from cryptography.fernet import Fernet
            return Fernet.generate_key().decode()
        except ImportError:
            raise ImportError("需要 cryptography 库: pip install cryptography")

    @staticmethod
    def encrypt(payload: dict, key: str) -> str:
        """加密消息体"""
        try:
            from cryptography.fernet import Fernet
            f = Fernet(key.encode() if isinstance(key, str) else key)
            return f.encrypt(json.dumps(payload, ensure_ascii=False).encode()).decode()
        except ImportError:
            raise ImportError("需要 cryptography 库: pip install cryptography")

    @staticmethod
    def decrypt(encrypted: str, key: str) -> dict:
        """解密消息体"""
        try:
            from cryptography.fernet import Fernet
            f = Fernet(key.encode() if isinstance(key, str) else key)
            return json.loads(f.decrypt(encrypted.encode()))
        except ImportError:
            raise ImportError("需要 cryptography 库: pip install cryptography")


# ============================================================
# 访问控制 (ACL)
# ============================================================

class AccessControlList:
    """Agent 访问控制列表

    参考：8.8-hais-v0.2-design.md §3.4.3, 8.9-holoagent-v1.0-design.md §8.3

    权限类型：
      read:    可以读取的资源
      write:   可以写入的资源
      exec:    可以执行的 API
      max_concurrent: 最大并发数
      rate_limit: 速率限制

    用法：
        acl = AccessControlList()
        acl.set("translator", read=["global:glossary"], exec=["act", "observe"])
        assert acl.check("translator", "read", "global:glossary")  # ✅
        assert not acl.check("translator", "write", "global:glossary")  # ❌
    """

    def __init__(self):
        self._acls: dict[str, dict] = {}

    def set(self, agent_id: str, read: list[str] = None,
            write: list[str] = None, exec_: list[str] = None,
            max_concurrent: int = 3, rate_limit: str = "100/min") -> None:
        """设置 Agent 的 ACL

        Args:
            agent_id: Agent ID
            read: 可读资源列表
            write: 可写资源列表
            exec_: 可执行 API 列表
            max_concurrent: 最大并发数
            rate_limit: 速率限制 (格式: "次数/时间单位")
        """
        self._acls[agent_id] = {
            "read": set(read or []),
            "write": set(write or []),
            "exec": set(exec_ or []),
            "max_concurrent": max_concurrent,
            "rate_limit": rate_limit,
        }

    def check(self, agent_id: str, action: str, resource: str) -> bool:
        """检查 Agent 是否有权限执行操作

        Args:
            agent_id: Agent ID
            action: 操作类型 (read / write / exec)
            resource: 目标资源 (如 "global:glossary", "act")

        Returns:
            True = 允许
        """
        acl = self._acls.get(agent_id)
        if acl is None:
            return False  # 未注册 → 默认拒绝

        if action == "exec":
            return resource in acl["exec"]
        elif action == "read":
            return resource in acl["read"]
        elif action == "write":
            return resource in acl["write"]
        else:
            return False

    def can_read(self, agent_id: str, resource: str) -> bool:
        return self.check(agent_id, "read", resource)

    def can_write(self, agent_id: str, resource: str) -> bool:
        return self.check(agent_id, "write", resource)

    def can_exec(self, agent_id: str, api_name: str) -> bool:
        return self.check(agent_id, "exec", api_name)

    def remove(self, agent_id: str) -> None:
        """删除 Agent 的 ACL"""
        self._acls.pop(agent_id, None)

    def list(self) -> dict:
        """列出所有 ACL"""
        return {
            agent_id: {
                "read": list(acl["read"]),
                "write": list(acl["write"]),
                "exec": list(acl["exec"]),
                "max_concurrent": acl["max_concurrent"],
                "rate_limit": acl["rate_limit"],
            }
            for agent_id, acl in self._acls.items()
        }

    @staticmethod
    def default_agent_acl(agent_id: str) -> dict:
        """生成默认 ACL (最小权限)"""
        return {
            "read": [f"agent:{agent_id}:cache", f"agent:{agent_id}:output"],
            "write": [f"agent:{agent_id}:cache"],
            "exec": ["act", "observe", "reflect", "remember", "forget", "escalate", "collaborate"],
            "max_concurrent": 3,
            "rate_limit": "100/min",
        }


# ============================================================
# 安全上下文 (整合)
# ============================================================

class SecurityContext:
    """安全上下文 — 签名 + ACL + 加密 的统一入口

    用法：
        security = SecurityContext()

        # 注册 Agent
        secret = security.register_agent("translator", "翻译 Agent")

        # 签名消息
        msg = {"from": "translator", "to": "proofreader", "payload": "hello"}
        msg["signature"] = security.sign("translator", msg)

        # 验证
        assert security.verify("translator", msg, msg["signature"])
    """

    def __init__(self):
        self.signer = MessageSigner()
        self.encryptor = MessageEncryptor()
        self.acl = AccessControlList()
        # agent_id -> (identity, secret_key)
        self._registry: dict[str, tuple[AgentIdentity, str]] = {}

    def register_agent(self, agent_id: str, display_name: str = "",
                       tags: list[str] = None) -> str:
        """注册新 Agent，返回密钥

        Args:
            agent_id: 唯一 ID
            display_name: 显示名
            tags: 标签

        Returns:
            secret_key (调用方需保存，仅返回一次)
        """
        secret = MessageSigner.generate_secret()
        identity = AgentIdentity(
            agent_id=agent_id,
            display_name=display_name or agent_id,
            tags=tags or [],
        )
        self._registry[agent_id] = (identity, secret)
        # 设置默认 ACL
        default_acl = AccessControlList.default_agent_acl(agent_id)
        self.acl.set(
            agent_id,
            read=default_acl["read"],
            write=default_acl["write"],
            exec_=default_acl["exec"],
            max_concurrent=default_acl["max_concurrent"],
            rate_limit=default_acl["rate_limit"],
        )

        return secret

    def get_identity(self, agent_id: str) -> Optional[AgentIdentity]:
        """获取 Agent 身份信息"""
        pair = self._registry.get(agent_id)
        return pair[0] if pair else None

    def sign(self, agent_id: str, message: dict) -> str:
        """用 Agent 密钥签名"""
        pair = self._registry.get(agent_id)
        if pair is None:
            raise ValueError(f"Agent '{agent_id}' not registered")
        return MessageSigner.sign(message, pair[1])

    def verify(self, agent_id: str, message: dict, signature: str) -> bool:
        """验证 Agent 签名"""
        pair = self._registry.get(agent_id)
        if pair is None:
            return False
        return MessageSigner.verify(message, signature, pair[1])

    def can(self, agent_id: str, action: str, resource: str) -> bool:
        """权限检查"""
        return self.acl.check(agent_id, action, resource)

    def list_agents(self) -> list[dict]:
        """列出所有已注册 Agent"""
        return [identity.to_dict() for identity, _ in self._registry.values()]

    def remove_agent(self, agent_id: str) -> None:
        """注销 Agent"""
        self._registry.pop(agent_id, None)
        self.acl.remove(agent_id)
