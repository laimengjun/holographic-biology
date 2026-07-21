"""
message_bus.py - HoloMessage Protocol v1.0 消息总线

全息胚类比：消息总线 = 全息胚间的神经递质系统

HoloMessage Protocol v1.0 (8.8-hais-v0.2-design.md §3.3, §7):
  - 应用层：JSON 消息 (HoloMessage v1.0)
  - 传输层：WebSocket / HTTP / 内存管道
  - 路由层：topic-based + agent-id direct

消息类型:
  request / response / event / broadcast / ack / error

设计原则:
  - 最小依赖：内存模式零依赖，WebSocket 模式只需 websockets 库
  - Agent 身份透明：每条消息携带 from/to agent_id
  - 可审计：每条消息有唯一 ID 和 trace_id
"""

from __future__ import annotations
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Optional


_logger = logging.getLogger("holoagent.bus")


# ============================================================
# HoloMessage Protocol v1.0
# ============================================================

class MessageType(str, Enum):
    """HoloMessage 消息类型"""
    REQUEST = "request"       # 请求
    RESPONSE = "response"     # 响应
    EVENT = "event"          # 事件通知
    BROADCAST = "broadcast"  # 广播
    QUERY = "query"          # 查询
    ACK = "ack"              # 确认
    ERROR = "error"          # 错误


@dataclass
class HoloMessage:
    """HoloMessage Protocol v1.0 消息格式

    参考：8.8-hais-v0.2-design.md §3.3.1
    """
    id: str = ""                          # 消息唯一 ID
    version: str = "1.0"                  # 协议版本
    from_agent: str = ""                  # 发送方 Agent ID
    from_session: str = ""                # 发送方 session ID
    to_agent: str = ""                    # 接收方 ("*" = 广播)
    to_session: str = ""                  # 接收方 session (可选)
    topic: str = "default"                # 主题
    type: MessageType = MessageType.EVENT # 消息类型
    payload: dict = field(default_factory=dict)  # 消息体
    priority: str = "normal"              # low / normal / high / urgent
    ttl: int = 300                        # 过期时间 (秒)
    trace_id: str = ""                    # 追踪 ID
    parent_id: str = ""                   # 父消息 ID
    timestamp: float = 0.0                # Unix 时间戳
    signature: str = ""                   # 消息签名 (可选)

    def __post_init__(self):
        if not self.id:
            self.id = f"msg-{uuid.uuid4().hex[:16]}"
        if not self.timestamp:
            self.timestamp = time.time()
        if not self.trace_id:
            self.trace_id = f"trace-{uuid.uuid4().hex[:12]}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["type"] = self.type.value if isinstance(self.type, MessageType) else self.type
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "HoloMessage":
        data["type"] = MessageType(data.get("type", "event"))
        return cls(**{k.replace("-", "_"): v for k, v in data.items()})

    @classmethod
    def from_json(cls, text: str) -> "HoloMessage":
        return cls.from_dict(json.loads(text))

    def is_expired(self) -> bool:
        return time.time() > self.timestamp + self.ttl

    def is_broadcast(self) -> bool:
        return self.to_agent == "*"


# ============================================================
# 消息总线 (内存实现)
# ============================================================

class HoloMessageBus:
    """HoloMessage 消息总线 (内存版本)

    提供核心路由功能，无需外部依赖。
    生产环境可替换为 WebSocket/TCP 实现。

    路由规则 (8.8-hais-v0.2-design.md §3.3.3):
      - 直发：按 to_agent 投递
      - 广播：to_agent = "*"，投递给订阅了对应 topic 的所有 Agent
      - Topic 订阅：Agent 可订阅特定 topic

    用法：
        bus = HoloMessageBus()

        # Agent A 注册
        bus.register("agent_a", handler_a)

        # 发送消息 (直发)
        bus.send(HoloMessage(from_agent="orchestrator", to_agent="agent_a", ...))

        # 广播
        bus.send(HoloMessage(from_agent="orchestrator", to_agent="*", topic="system:announce", ...))

        # 订阅 topic
        bus.subscribe("agent_b", "task:translate")
    """

    def __init__(self, name: str = "default"):
        self.name = name
        # agent_id -> handler function (接收 HoloMessage 返回 Any)
        self._handlers: dict[str, Callable] = {}
        # topic -> [agent_id] (订阅列表)
        self._subscriptions: dict[str, set[str]] = defaultdict(set)
        # 历史消息 (用于审计和调试)
        self._history: list[HoloMessage] = []
        self._max_history = 1000
        # 统计
        self._stats = {
            "messages_sent": 0,
            "messages_delivered": 0,
            "messages_expired": 0,
            "errors": 0,
        }
        _logger.info(f"HoloMessageBus '{name}' initialized")

    # ── Agent 注册 / 注销 ──

    def register(self, agent_id: str, handler: Callable[[HoloMessage], Any]) -> None:
        """注册 Agent 的消息处理器

        Args:
            agent_id: Agent 唯一 ID
            handler: 接收 HoloMessage 返回响应数据的函数
        """
        self._handlers[agent_id] = handler
        _logger.info(f"Agent '{agent_id}' registered")

    def unregister(self, agent_id: str) -> None:
        """注销 Agent"""
        self._handlers.pop(agent_id, None)
        for topic in self._subscriptions:
            self._subscriptions[topic].discard(agent_id)
        _logger.info(f"Agent '{agent_id}' unregistered")

    def is_registered(self, agent_id: str) -> bool:
        return agent_id in self._handlers

    def list_agents(self) -> list[str]:
        return list(self._handlers.keys())

    # ── Topic 订阅 ──

    def subscribe(self, agent_id: str, topic: str) -> None:
        """订阅 topic

        Args:
            agent_id: 订阅者
            topic: 主题名 (支持通配符: task:* 匹配所有 task: 前缀)
        """
        self._subscriptions[topic].add(agent_id)
        _logger.debug(f"Agent '{agent_id}' subscribed to '{topic}'")

    def unsubscribe(self, agent_id: str, topic: str) -> None:
        """取消订阅"""
        self._subscriptions[topic].discard(agent_id)

    def subscriptions(self, agent_id: str) -> list[str]:
        """Agent 当前订阅的所有 topic"""
        return [t for t, subs in self._subscriptions.items() if agent_id in subs]

    # ── 消息发送 ──

    def send(self, message: HoloMessage) -> list[Any]:
        """发送消息

        Args:
            message: HoloMessage

        Returns:
            响应列表 (每个接收方的响应)
        """
        self._stats["messages_sent"] += 1
        self._history.append(message)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # 检查过期
        if message.is_expired():
            self._stats["messages_expired"] += 1
            _logger.warning(f"Message {message.id} expired (ttl={message.ttl}s)")
            return []

        responses = []

        if message.is_broadcast():
            # 广播模式
            recipients = self._find_broadcast_recipients(message.topic)
            for agent_id in recipients:
                if agent_id == message.from_agent:
                    continue  # 不广播给自己
                response = self._deliver(agent_id, message)
                if response is not None:
                    responses.append(response)
        else:
            # 直发模式
            response = self._deliver(message.to_agent, message)
            if response is not None:
                responses.append(response)

        return responses

    def publish(self, topic: str, payload: dict,
                from_agent: str = "system") -> list[Any]:
        """便捷方法：发送事件广播

        Args:
            topic: 主题
            payload: 消息体
            from_agent: 发送方

        Returns:
            响应列表
        """
        msg = HoloMessage(
            from_agent=from_agent,
            to_agent="*",
            topic=topic,
            type=MessageType.EVENT,
            payload=payload,
        )
        return self.send(msg)

    def request(self, from_agent: str, to_agent: str,
                topic: str, payload: dict) -> Optional[Any]:
        """便捷方法：发送请求并等待单个响应

        Args:
            from_agent: 发送方
            to_agent: 接收方
            topic: 主题
            payload: 消息体

        Returns:
            单个响应数据 (或 None)
        """
        msg = HoloMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            topic=topic,
            type=MessageType.REQUEST,
            payload=payload,
        )
        responses = self.send(msg)
        return responses[0] if responses else None

    # ── 内部方法 ──

    def _deliver(self, agent_id: str, message: HoloMessage) -> Optional[Any]:
        """投递消息到单个 Agent"""
        handler = self._handlers.get(agent_id)
        if handler is None:
            self._stats["errors"] += 1
            _logger.warning(f"Message {message.id}: target '{agent_id}' not registered")
            return None

        try:
            result = handler(message)
            self._stats["messages_delivered"] += 1
            return result
        except Exception as e:
            self._stats["errors"] += 1
            _logger.error(f"Delivery to '{agent_id}' failed: {e}")
            return None

    def _find_broadcast_recipients(self, topic: str) -> set[str]:
        """找到匹配 topic 的所有接收方

        匹配规则：
          - 精确匹配
          - 通配符匹配 (task:* 匹配 task:translate 等)
        """
        recipients: set[str] = set()

        # 精确匹配
        recipients.update(self._subscriptions.get(topic, set()))

        # 通配符匹配
        for sub_topic, subs in self._subscriptions.items():
            if sub_topic.endswith("*"):
                prefix = sub_topic[:-1]
                if topic.startswith(prefix):
                    recipients.update(subs)

        return recipients

    # ── 状态 ──

    def get_stats(self) -> dict:
        return {**self._stats, "agents": len(self._handlers), "subscribers": len(self._subscriptions)}

    def get_history(self, n: int = 10) -> list[dict]:
        return [m.to_dict() for m in self._history[-n:]]

    def clear_history(self) -> None:
        self._history.clear()

    def reset(self) -> None:
        self._handlers.clear()
        self._subscriptions.clear()
        self._history.clear()
        self._stats = {"messages_sent": 0, "messages_delivered": 0, "messages_expired": 0, "errors": 0}
