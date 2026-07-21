"""
collaborator.py - collaborate() API + 协作模式 + Workflow 引擎

全息胚类比：协作 = 多个全息胚之间的信号传导与功能耦合

v0.2 核心新增：取代 handoff() 的一对一模式，支持多对多协作。

协作模式 (8.8-hais-v0.2-design.md §4.3):
  - request:    一对一请求
  - broadcast:  一对多广播
  - gather:     汇聚多个 Agent 响应
  - chain:      顺序链 (A→B→C)
  - vote:       多 Agent 投票 (多数决)
  - consensus:  多 Agent 共识 (全员同意)

API 守恒：collaborate() 是唯一的"外部 API"(1/7)
"""

from __future__ import annotations
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Optional


class CollaborationMode(str, Enum):
    """HAIS 协作模式"""
    REQUEST = "request"        # 一对一请求
    BROADCAST = "broadcast"   # 一对多广播
    GATHER = "gather"         # 汇聚响应
    CHAIN = "chain"           # 顺序链
    VOTE = "vote"             # 投票 (多数决)
    CONSENSUS = "consensus"   # 共识 (全员同意)


@dataclass
class CollaborationRequest:
    """协作请求"""
    id: str = ""
    mode: CollaborationMode = CollaborationMode.REQUEST
    from_agent: str = ""
    to_agent: str | list[str] = ""
    topic: str = "default"
    payload: dict = field(default_factory=dict)
    timeout_s: int = 30
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"collab-{uuid.uuid4().hex[:12]}"
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class CollaborationResponse:
    """协作响应"""
    request_id: str = ""
    from_agent: str = ""
    success: bool = True
    data: Any = None
    error: Optional[str] = None
    latency_ms: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


class CollaborationResult:
    """协作结果 (汇聚多个响应)"""

    def __init__(self, responses: list[CollaborationResponse]):
        self.responses = responses

    @property
    def all_success(self) -> bool:
        return all(r.success for r in self.responses)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.responses if r.success)

    @property
    def failure_count(self) -> int:
        return sum(1 for r in self.responses if not r.success)

    @property
    def majority(self) -> Optional[Any]:
        """多数决结果 (vote 模式)"""
        from collections import Counter
        data = [json.dumps(r.data, sort_keys=True) for r in self.responses if r.success and r.data]
        if not data:
            return None
        counter = Counter(data)
        winner_json, count = counter.most_common(1)[0]
        if count > len(self.responses) / 2:
            return json.loads(winner_json)
        return None

    @property
    def consensus(self) -> Optional[Any]:
        """共识结果 (consensus 模式)"""
        if not self.responses:
            return None
        first = self.responses[0].data
        for r in self.responses[1:]:
            if r.data != first:
                return None  # 未达成共识
        return first

    @property
    def merged(self) -> dict:
        """汇聚结果 (gather 模式)"""
        result = {}
        for r in self.responses:
            if r.success and isinstance(r.data, dict):
                result.update(r.data)
        return result


# ============================================================
# Collaborate API (v0.2 核心外部 API)
# ============================================================

class Collaborate:
    """collaborate() API 实现

    通过消息总线实现跨 Agent 协作。

    用法：
        bus = HoloMessageBus()
        collab = Collaborate(bus)

        # 一对一请求
        result = await collab.request("translator", "translate", {"text": "Hello"})

        # 广播
        results = await collab.broadcast("announcement", {"msg": "系统维护"})

        # 并行汇聚
        responses = await collab.gather(["agent_a", "agent_b"], "process", payload)

        # 顺序链
        final = await collab.chain(["translator", "proofreader"], input_data)

        # 投票
        result = await collab.vote(["judge1", "judge2", "judge3"], "evaluate", data)

        # 共识
        result = await collab.consensus(["validator_a", "validator_b"], "verify", data)
    """

    def __init__(self, bus=None):
        """
        Args:
            bus: HoloMessageBus 实例 (为 None 则用内存模拟)
        """
        self.bus = bus
        self._memory_registry: dict[str, Callable] = {}  # agent_id -> handler

    def register(self, agent_id: str, handler: Callable) -> None:
        """注册本地 Agent 的协作 handler

        Args:
            agent_id: Agent ID
            handler: 接收 payload dict 返回响应数据的函数
        """
        self._memory_registry[agent_id] = handler

    def unregister(self, agent_id: str) -> None:
        """注销 Agent"""
        self._memory_registry.pop(agent_id, None)

    # ── 5 种协作模式 ──

    def execute(self, from_agent: str, mode: str,
                target: str | list[str] = None,
                payload: dict = None,
                timeout: int = 30) -> Any:
        """执行协作 (同步入口, 实际调用对应模式)

        Args:
            from_agent: 发起方 Agent ID
            mode: 协作模式 (request / broadcast / gather / chain / vote / consensus)
            target: 目标 Agent ID
            payload: 消息体
            timeout: 超时秒数

        Returns:
            协作结果 (类型取决于模式)
        """
        if mode == CollaborationMode.REQUEST:
            return self._request(from_agent, target, payload, timeout)
        elif mode == CollaborationMode.BROADCAST:
            return self._broadcast(from_agent, payload, timeout)
        elif mode == CollaborationMode.GATHER:
            return self._gather(from_agent, list(target) if target else [], payload, timeout)
        elif mode == CollaborationMode.CHAIN:
            return self._chain(from_agent, list(target) if target else [], payload, timeout)
        elif mode == CollaborationMode.VOTE:
            return self._vote(from_agent, list(target) if target else [], payload, timeout)
        elif mode == CollaborationMode.CONSENSUS:
            return self._consensus(from_agent, list(target) if target else [], payload, timeout)
        else:
            raise ValueError(f"Unknown collaboration mode: {mode}")

    def _request(self, from_agent: str, to_agent: str,
                 payload: dict, timeout: int) -> CollaborationResponse:
        """一对一请求"""
        t0 = time.time()
        handler = self._memory_registry.get(str(to_agent))
        if handler is None:
            return CollaborationResponse(
                request_id=f"req-{uuid.uuid4().hex[:8]}",
                from_agent=from_agent,
                success=False,
                error=f"Agent '{to_agent}' not registered",
            )
        try:
            result = handler(payload)
            return CollaborationResponse(
                request_id=f"req-{uuid.uuid4().hex[:8]}",
                from_agent=str(to_agent),
                success=True,
                data=result,
                latency_ms=(time.time() - t0) * 1000,
            )
        except Exception as e:
            return CollaborationResponse(
                request_id=f"req-{uuid.uuid4().hex[:8]}",
                from_agent=str(to_agent),
                success=False,
                error=str(e),
                latency_ms=(time.time() - t0) * 1000,
            )

    def _broadcast(self, from_agent: str, payload: dict,
                   timeout: int) -> CollaborationResult:
        """广播给所有已注册的 Agent"""
        responses = []
        for agent_id, handler in self._memory_registry.items():
            if agent_id == from_agent:
                continue  # 不广播给自己
            t0 = time.time()
            try:
                result = handler(payload)
                responses.append(CollaborationResponse(
                    request_id=f"bc-{uuid.uuid4().hex[:8]}",
                    from_agent=agent_id,
                    success=True,
                    data=result,
                    latency_ms=(time.time() - t0) * 1000,
                ))
            except Exception as e:
                responses.append(CollaborationResponse(
                    request_id=f"bc-{uuid.uuid4().hex[:8]}",
                    from_agent=agent_id,
                    success=False,
                    error=str(e),
                ))
        return CollaborationResult(responses)

    def _gather(self, from_agent: str, agent_ids: list[str],
                payload: dict, timeout: int) -> CollaborationResult:
        """汇聚多个 Agent 的响应 (并行)"""
        responses = []
        for agent_id in agent_ids:
            t0 = time.time()
            handler = self._memory_registry.get(agent_id)
            if handler is None:
                responses.append(CollaborationResponse(
                    from_agent=agent_id, success=False,
                    error=f"Not registered",
                ))
                continue
            try:
                result = handler(payload)
                responses.append(CollaborationResponse(
                    from_agent=agent_id, success=True,
                    data=result,
                    latency_ms=(time.time() - t0) * 1000,
                ))
            except Exception as e:
                responses.append(CollaborationResponse(
                    from_agent=agent_id, success=False,
                    error=str(e),
                ))
        return CollaborationResult(responses)

    def _chain(self, from_agent: str, agent_ids: list[str],
               payload: dict, timeout: int) -> CollaborationResponse:
        """顺序链 A→B→C"""
        current_payload = payload
        for agent_id in agent_ids:
            resp = self._request(from_agent, agent_id, current_payload, timeout)
            if not resp.success:
                return resp
            if isinstance(resp.data, dict):
                current_payload = resp.data
            else:
                current_payload = {"result": resp.data}
        return CollaborationResponse(
            request_id=f"chain-{uuid.uuid4().hex[:8]}",
            from_agent=agent_ids[-1] if agent_ids else from_agent,
            success=True,
            data=current_payload,
        )

    def _vote(self, from_agent: str, agent_ids: list[str],
              payload: dict, timeout: int) -> CollaborationResult:
        """投票 (返回多数决结果)"""
        result = self._gather(from_agent, agent_ids, payload, timeout)
        return result  # 调用者可用 result.majority 获取多数决

    def _consensus(self, from_agent: str, agent_ids: list[str],
                   payload: dict, timeout: int) -> CollaborationResult:
        """共识 (全员同意)"""
        result = self._gather(from_agent, agent_ids, payload, timeout)
        return result  # 调用者可用 result.consensus 获取共识


# ============================================================
# Workflow 引擎 (DAG 工作流)
# ============================================================

class Workflow:
    """DAG 工作流引擎

    把 collaborate() 的多种模式组合为可重用的工作流。

    用法：
        wf = Workflow("translate-review-publish")
        wf.add_stage("translate", ["translator"], mode="sequential")
        wf.add_stage("review", ["proofreader"], mode="sequential")
        wf.add_stage("quality_check", ["reviewer_a", "reviewer_b"], mode="vote")
        result = wf.run(initial_payload={"text": "..."}, collaborator=my_collab)
    """

    def __init__(self, name: str, description: str = ""):
        """
        Args:
            name: 工作流名称
            description: 可选描述
        """
        self.name = name
        self.description = description
        self._stages: list[dict] = []

    def add_stage(self, name: str, agents: list[str],
                  mode: str = "parallel",
                  payload_template: dict = None) -> "Workflow":
        """添加工作流阶段

        Args:
            name: 阶段名称
            agents: 参与 Agent 列表
            mode: 协作模式 (sequential / parallel / vote / consensus)
            payload_template: 可选的 payload 模板 (在运行时用当前 payload 填充)

        Returns:
            self (链式调用)
        """
        self._stages.append({
            "name": name,
            "agents": agents,
            "mode": mode,
            "payload_template": payload_template or {},
        })
        return self

    def run(self, initial_payload: dict,
            collaborator: Collaborate,
            from_agent: str = "orchestrator") -> dict:
        """执行工作流

        Args:
            initial_payload: 初始输入
            collaborator: Collaborate 实例
            from_agent: 发起方标识

        Returns:
            最终结果 dict (含每阶段的输出)
        """
        current_payload = initial_payload
        stage_results = {}

        for stage in self._stages:
            stage_payload = {**stage["payload_template"], **current_payload}
            mode = stage["mode"]
            agents = stage["agents"]

            if mode == "sequential" and agents:
                # 顺序: 每个 Agent 依次处理
                result = collaborator._chain(None, agents, stage_payload, 30)
                if result.success and isinstance(result.data, dict):
                    current_payload = result.data
                stage_results[stage["name"]] = result.to_dict() if hasattr(result, 'to_dict') else {"success": result.success}

            elif mode == "parallel" and agents:
                # 并行: 所有 Agent 同时处理
                result = collaborator._gather(None, agents, stage_payload, 30)
                merged = result.merged
                current_payload.update(merged)
                stage_results[stage["name"]] = {
                    "success": result.all_success,
                    "agents_responded": result.success_count,
                    "merged_keys": list(merged.keys()),
                }

            elif mode == "vote" and agents:
                # 投票
                result = collaborator._vote(None, agents, stage_payload, 30)
                majority = result.majority
                if majority:
                    current_payload["vote_result"] = majority
                stage_results[stage["name"]] = {
                    "success": result.success_count >= len(agents) / 2,
                    "majority_found": majority is not None,
                    "votes_for": result.success_count,
                    "votes_against": result.failure_count,
                }

            elif mode == "consensus" and agents:
                # 共识
                result = collaborator._consensus(None, agents, stage_payload, 30)
                consensus = result.consensus
                if consensus is not None:
                    current_payload["consensus_result"] = consensus
                stage_results[stage["name"]] = {
                    "success": result.all_success,
                    "consensus_reached": consensus is not None,
                    "agents_agreed": result.success_count,
                }

        return {
            "workflow": self.name,
            "final_payload": current_payload,
            "stages": stage_results,
        }

    def to_dict(self) -> dict:
        """序列化工作流定义"""
        return {
            "name": self.name,
            "description": self.description,
            "stages": self._stages,
        }


# ============================================================
# 预设工作流模板
# ============================================================

def translate_proofread_workflow() -> Workflow:
    """翻译→校对的经典流水线"""
    return Workflow(
        name="translate-and-proofread",
        description="翻译 + 校对流水线：先翻译，再校对",
    ).add_stage("translate", ["translator"], mode="sequential").add_stage(
        "proofread", ["proofreader"], mode="sequential"
    )


def multi_review_workflow() -> Workflow:
    """多 Agent 评审"""
    return Workflow(
        name="multi-review",
        description="多 Agent 并行评审 + 投票决定",
    ).add_stage(
        "review", ["reviewer_a", "reviewer_b", "reviewer_c"],
        mode="parallel",
    ).add_stage(
        "vote", ["judge"], mode="vote",
    )
