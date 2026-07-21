"""
orchestrator.py - 任务分解 + Agent 调度

参考：8.8-hais-v0.2-design.md §5

核心职责 (8.8 §5.1):
  - task_decomposition: 复杂任务分解为子任务
  - agent_selection: 选择最合适的 Agent
  - dependency_management: 子任务依赖 (DAG)
  - result_aggregation: 汇聚结果
  - error_recovery: 失败处理
  - load_balancing: 负载均衡

工作流示例 (8.8 §5.2):
  task: "翻译 100 页中文文档到英文"
  decomposition:
    - subtask: "翻译"     → agent: translator
    - subtask: "校对"     → agent: proofreader  (依赖: translator)
    - subtask: "摘要"     → agent: summarizer   (依赖: proofreader)
"""

from __future__ import annotations
import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Callable, Optional


_logger = None  # 延迟初始化


def _get_logger():
    global _logger
    if _logger is None:
        import logging
        _logger = logging.getLogger("holoagent.orchestrator")
    return _logger


# ============================================================
# 任务模型
# ============================================================

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class SubTask:
    """子任务"""
    id: str = ""
    name: str = ""                       # 任务名 (如 "translate")
    agent_id: str = ""                   # 执行 Agent
    input: Any = None                    # 输入数据
    output: Any = None                   # 输出数据
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)  # 依赖的子任务 ID 列表
    error: Optional[str] = None
    latency_ms: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = f"task-{uuid.uuid4().hex[:10]}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "dependencies": self.dependencies,
            "error": self.error,
            "latency_ms": self.latency_ms,
        }


@dataclass
class TaskPlan:
    """完整任务计划"""
    name: str = ""
    subtasks: list[SubTask] = field(default_factory=list)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    def add(self, name: str, agent_id: str, input_data: Any = None,
            depends_on: list[str] = None) -> SubTask:
        """添加子任务

        Args:
            name: 子任务名
            agent_id: 执行 Agent
            input_data: 输入
            depends_on: 依赖的子任务 name 列表

        Returns:
            创建的子任务
        """
        # 解析依赖 ID
        dep_ids = []
        if depends_on:
            for dep_name in depends_on:
                for st in self.subtasks:
                    if st.name == dep_name:
                        dep_ids.append(st.id)
                        break

        task = SubTask(
            name=name,
            agent_id=agent_id,
            input=input_data,
            dependencies=dep_ids,
        )
        self.subtasks.append(task)
        return task

    def stages(self) -> list[list[SubTask]]:
        """按拓扑排序返回执行阶段

        Stage 0: 无依赖的任务 (可并行)
        Stage 1: 依赖 Stage 0 的任务
        ...

        Returns:
            [[stage0_task1, stage0_task2], [stage1_task1, ...], ...]
        """
        stages = []
        remaining = set(st.id for st in self.subtasks)
        completed = set()

        while remaining:
            # 找所有依赖已满足的任务
            ready = [
                st for st in self.subtasks
                if st.id in remaining and all(d in completed for d in st.dependencies)
            ]
            if not ready:
                break  # 有环或无法满足的依赖

            stages.append(ready)
            for st in ready:
                remaining.discard(st.id)
                completed.add(st.id)

        return stages

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "subtasks": [st.to_dict() for st in self.subtasks],
            "stages": [[st.id for st in stage] for stage in self.stages()],
        }


# ============================================================
# Orchestrator
# ============================================================

class Orchestrator:
    """任务编排器

    负责任务分解、Agent 调度、依赖管理、结果汇聚。

    用法：
        orch = Orchestrator()

        # 注册 Agent 处理器
        orch.register_agent("translator", my_translator_handler)
        orch.register_agent("proofreader", my_proofreader_handler)
        orch.register_agent("summarizer", my_summarizer_handler)

        # 构建计划
        plan = TaskPlan(name="翻译文档")
        plan.add("translate", "translator", "原文...")
        plan.add("proofread", "proofreader", depends_on=["translate"])
        plan.add("summarize", "summarizer", depends_on=["proofread"])

        # 执行
        result = orch.execute(plan)
    """

    def __init__(self, name: str = "orchestrator"):
        self.name = name
        # agent_id -> handler(input) -> output
        self._agents: dict[str, Callable] = {}
        self._execution_history: list[dict] = []

    def register_agent(self, agent_id: str, handler: Callable) -> None:
        """注册 Agent 处理器

        Args:
            agent_id: Agent ID
            handler: 接收输入，返回输出
        """
        self._agents[agent_id] = handler

    def unregister_agent(self, agent_id: str) -> None:
        self._agents.pop(agent_id, None)

    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

    # ── 任务分解 (LLM-based) ──

    def decompose(self, task_description: str,
                  available_agents: list[str] = None) -> TaskPlan:
        """把自然语言任务描述分解为 TaskPlan

        使用简单规则进行分解。生产环境可用 LLM 做更复杂的分解。

        Args:
            task_description: 自然语言任务描述
            available_agents: 可用 Agent 列表 (None = 所有已注册)

        Returns:
            TaskPlan 实例
        """
        agents = available_agents or self.list_agents()
        plan = TaskPlan(name=f"分解: {task_description[:50]}...")

        # 简单启发式分解
        desc_lower = task_description.lower()

        if "翻译" in desc_lower or "translate" in desc_lower:
            if "translator" in agents:
                plan.add("translate", "translator", task_description)

        if "校对" in desc_lower or "proofread" in desc_lower or "review" in desc_lower:
            target = "proofreader" if "proofreader" in agents else None
            if target:
                depends = ["translate"] if any(st.name == "translate" for st in plan.subtasks) else []
                plan.add("proofread", target, depends_on=depends)

        if "摘要" in desc_lower or "summarize" in desc_lower:
            target = "summarizer" if "summarizer" in agents else None
            if target:
                deps = []
                if any(st.name == "proofread" for st in plan.subtasks):
                    deps.append("proofread")
                elif any(st.name == "translate" for st in plan.subtasks):
                    deps.append("translate")
                plan.add("summarize", target, depends_on=deps)

        # 没有匹配到任何子任务：全量发给第一个可用 Agent
        if not plan.subtasks and agents:
            plan.add("default", agents[0], task_description)

        return plan

    # ── 计划执行 ──

    def execute(self, plan: TaskPlan) -> dict:
        """执行任务计划

        按阶段执行，同阶段子任务并行。

        Args:
            plan: 任务计划

        Returns:
            执行结果 dict
        """
        log = _get_logger()
        log.info(f"Executing plan: {plan.name} ({len(plan.subtasks)} subtasks)")

        stages = plan.stages()
        results = {}
        t_start = time.time()

        for stage_idx, stage_tasks in enumerate(stages):
            log.info(f"  Stage {stage_idx}: {len(stage_tasks)} task(s)")

            for task in stage_tasks:
                task.status = TaskStatus.RUNNING
                t0 = time.time()

                handler = self._agents.get(task.agent_id)
                if handler is None:
                    task.status = TaskStatus.FAILED
                    task.error = f"Agent '{task.agent_id}' not registered"
                    continue

                try:
                    # 把依赖的输出合并到输入
                    combined_input = task.input
                    if task.dependencies:
                        dep_outputs = {}
                        for dep_id in task.dependencies:
                            dep_task = next(
                                (st for st in plan.subtasks if st.id == dep_id),
                                None,
                            )
                            if dep_task and dep_task.status == TaskStatus.SUCCESS:
                                dep_outputs[dep_task.name] = dep_task.output
                        if isinstance(combined_input, dict):
                            combined_input["_dependencies"] = dep_outputs
                        elif combined_input is None:
                            combined_input = {"_dependencies": dep_outputs}
                        else:
                            combined_input = {"input": combined_input, "_dependencies": dep_outputs}

                    task.output = handler(combined_input)
                    task.status = TaskStatus.SUCCESS
                    task.latency_ms = (time.time() - t0) * 1000
                    results[task.name] = task.output
                    log.info(f"    {task.name} ({task.agent_id}): {task.latency_ms:.0f}ms ✅")

                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    task.latency_ms = (time.time() - t0) * 1000
                    log.error(f"    {task.name} ({task.agent_id}): {e} ❌")

        total_time = (time.time() - t_start) * 1000
        execution_record = {
            "plan_name": plan.name,
            "total_time_ms": total_time,
            "subtasks": len(plan.subtasks),
            "success": sum(1 for st in plan.subtasks if st.status == TaskStatus.SUCCESS),
            "failed": sum(1 for st in plan.subtasks if st.status == TaskStatus.FAILED),
            "stages": len(stages),
        }
        self._execution_history.append(execution_record)

        return {
            "success": all(st.status == TaskStatus.SUCCESS for st in plan.subtasks),
            "total_time_ms": total_time,
            "stages": len(stages),
            "results": results,
            "tasks": [st.to_dict() for st in plan.subtasks],
        }

    # ── 历史 ──

    def get_history(self, n: int = 10) -> list[dict]:
        return self._execution_history[-n:]

    def reset(self) -> None:
        self._execution_history.clear()
