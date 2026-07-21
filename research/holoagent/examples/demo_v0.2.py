"""
HAIS v0.2 多 Agent 协作演示

演示内容：
  1. 创建 3 个 Agent (翻译/校对/摘要)
  2. 连接消息总线
  3. 记忆隔离验证
  4. collaborate() 协作 (顺序链)
  5. Workflow 引擎
  6. Orchestrator 任务分解
  7. HAIS 合规自检
"""

import logging
import sys
import time

# 确保可导入 holoagent 包
sys.path.insert(0, "D:/obsidian/Holographic-Biology/research")

from holoagent import (
    HoloAgent,
    KnowledgeSeed,
    MemorySystem,
    Collaborate,
    Workflow,
    CollaborationMode,
)
from holoagent.message_bus import HoloMessageBus, HoloMessage, MessageType
from holoagent.security import SecurityContext, MessageSigner, AccessControlList
from holoagent.orchestrator import Orchestrator, TaskPlan, SubTask
from holoagent.examples.translator import TranslatorAgent, ProofreaderAgent

logging.basicConfig(level=logging.WARNING, format="[%(levelname)s] %(message)s")


# ============================================================
# Part 1: 记忆系统演示
# ============================================================

def demo_memory_system():
    """演示三层记忆系统 + 隔离"""
    print("\n" + "=" * 60)
    print("1️⃣ 记忆系统演示")
    print("=" * 60)

    agent_a = HoloAgent(
        name="AgentA",
        seed=KnowledgeSeed(
            identity="我是 Agent A。",
            capability=["处理文本"],
            boundary="无",
            voice="简洁",
            escalation="无",
        ),
        agent_id="agent_a",
    )

    agent_b = HoloAgent(
        name="AgentB",
        seed=KnowledgeSeed(
            identity="我是 Agent B。",
            capability=["分析数据"],
            boundary="无",
            voice="简洁",
            escalation="无",
        ),
        agent_id="agent_b",
    )

    # 写入记忆 (隔离验证)
    agent_a.memory.set("secret", "agent_a 的秘密数据")
    agent_b.memory.set("secret", "agent_b 的秘密数据")

    a_secret = agent_a.memory.get("secret")
    b_secret = agent_b.memory.get("secret")

    print(f"  Agent A 的秘密: {a_secret}")
    print(f"  Agent B 的秘密: {b_secret}")
    print(f"  记忆隔离 {'✅' if a_secret != b_secret else '❌'} (不同 Agent 记忆独立)")

    # 短期记忆
    agent_a.memory.append("user", "帮我翻译这段话", metadata={"importance": 0.9})
    print(f"  短期记忆条数: {agent_a.memory.short.count()}")
    search_results = agent_a.memory.search("翻译")
    print(f"  搜索 '翻译': {len(search_results.get('short', []))} 条结果")

    return True


# ============================================================
# Part 2: 消息总线演示
# ============================================================

def demo_message_bus():
    """演示消息总线 + 路由"""
    print("\n" + "=" * 60)
    print("2️⃣ 消息总线演示")
    print("=" * 60)

    bus = HoloMessageBus("demo-bus")
    received_messages = []

    def agent_a_handler(msg: HoloMessage) -> str:
        received_messages.append(("agent_a", msg.topic))
        return f"Agent A 收到: {msg.payload.get('text', '')[:50]}"

    def agent_b_handler(msg: HoloMessage) -> str:
        received_messages.append(("agent_b", msg.topic))
        return f"Agent B 收到: {msg.payload.get('text', '')[:50]}"

    bus.register("agent_a", agent_a_handler)
    bus.register("agent_b", agent_b_handler)
    bus.subscribe("agent_a", "task:*")
    bus.subscribe("agent_b", "task:*")

    # 广播
    responses = bus.publish("task:announce", {"text": "新任务到达！"})
    print(f"  广播响应数: {len(responses)}")
    print(f"  Agent A 收到: {'✅' if any(r[0]=='agent_a' for r in received_messages) else '❌'}")
    print(f"  Agent B 收到: {'✅' if any(r[0]=='agent_b' for r in received_messages) else '❌'}")

    # 直发
    response = bus.request("orchestrator", "agent_a", "direct", {"text": "单独任务"})
    print(f"  直发响应: {'✅' if response else '❌'}")

    # 统计
    stats = bus.get_stats()
    print(f"  消息统计: {stats['messages_sent']} sent, {stats['messages_delivered']} delivered")

    return bus


# ============================================================
# Part 3: collaborate() 协作演示
# ============================================================

def demo_collaborate():
    """演示 collaborate() 的多种协作模式"""
    print("\n" + "=" * 60)
    print("3️⃣ collaborate() 协作模式演示")
    print("=" * 60)

    bus = HoloMessageBus("collab-demo")
    collab = Collaborate(bus)

    # 注册处理函数
    def translate_handler(payload: dict) -> dict:
        return {"translation": f"翻译结果: {payload.get('text', '')[:30]}"}

    def proofread_handler(payload: dict) -> dict:
        return {"proofread": f"校对完成: {payload.get('translation', '')[:30]}"}

    def vote_handler(payload: dict) -> str:
        import random
        return random.choice(["同意", "不同意", "不确定"])

    collab.register("translator", translate_handler)
    collab.register("proofreader", proofread_handler)
    collab.register("judge_a", vote_handler)
    collab.register("judge_b", vote_handler)
    collab.register("judge_c", vote_handler)

    # 1) 一对一请求
    print("  [request] 一对一:")
    resp = collab._request("user", "translator", {"text": "Hello World"}, 10)
    print(f"    响应: {resp.data} (成功={resp.success})")

    # 2) 顺序链
    print("  [chain] 翻译→校对:")
    result = collab._chain("user", ["translator", "proofreader"],
                           {"text": "全息生物学是一门新学科"}, 10)
    print(f"    最终: {result.data} (成功={result.success})")

    # 3) 广播
    print("  [broadcast] 广播:")
    bresult = collab._broadcast("user", {"msg": "系统通知"}, 10)
    print(f"    广播到 {len(bresult.responses)} 个 Agent")

    # 4) 投票
    print("  [vote] 投票:")
    vresult = collab._vote("user", ["judge_a", "judge_b", "judge_c"],
                           {"question": "这个方案可接受吗？"}, 10)
    majority = vresult.majority
    print(f"    投票结果: {majority} (参与: {vresult.success_count})")

    return collab


# ============================================================
# Part 4: Workflow 引擎演示
# ============================================================

def demo_workflow():
    """演示 Workflow 引擎"""
    print("\n" + "=" * 60)
    print("4️⃣ Workflow 引擎演示")
    print("=" * 60)

    bus = HoloMessageBus("wf-demo")
    collab = Collaborate(bus)

    def translator(payload):
        return {"translation": f"[EN]: {payload.get('text', '')[:40]}"}
    def proofreader(payload):
        return {"proofread": f"[Reviewed]: {payload.get('translation', '')[:40]}"}
    def reviewer(payload):
        return {"approved": True, "score": 85}

    collab.register("translator", translator)
    collab.register("proofreader", proofreader)
    collab.register("reviewer", reviewer)

    # 定义工作流
    wf = Workflow("translate-review")
    wf.add_stage("translate", ["translator"], mode="sequential")
    wf.add_stage("proofread", ["proofreader"], mode="sequential")
    wf.add_stage("quality_check", ["reviewer"], mode="vote")

    # 执行
    result = wf.run(
        initial_payload={"text": "全息生物学认为局部包含整体信息"},
        collaborator=collab,
    )
    print(f"  工作流: {result['workflow']}")
    for stage_name, stage_data in result.get("stages", {}).items():
        print(f"    阶段 [{stage_name}]: 成功={stage_data.get('success', 'N/A')}")
    print(f"  最终 payload 键: {list(result['final_payload'].keys())}")

    return wf


# ============================================================
# Part 5: Orchestrator 演示
# ============================================================

def demo_orchestrator():
    """演示 Orchestrator 任务分解 + 执行"""
    print("\n" + "=" * 60)
    print("5️⃣ Orchestrator 演示")
    print("=" * 60)

    orch = Orchestrator("demo-orch")

    def translate_fn(input_data):
        return f"翻译: {str(input_data)[:50]}..."

    def proofread_fn(input_data):
        return f"校对: {str(input_data)[:50]}..."

    orch.register_agent("translator", translate_fn)
    orch.register_agent("proofreader", proofread_fn)

    # 自动分解
    plan = orch.decompose("翻译并校对这篇技术文档")
    print(f"  分解计划: {plan.name}")
    for st in plan.subtasks:
        print(f"    - {st.name} → {st.agent_id}")

    # 执行
    result = orch.execute(plan)
    print(f"  执行结果: {'✅ 全部成功' if result['success'] else '❌ 有失败'}")
    print(f"  耗时: {result['total_time_ms']:.0f}ms, {result['stages']} 个阶段")

    return orch


# ============================================================
# Part 6: HAIS 合规自检
# ============================================================

def demo_hais_check():
    """演示 HAIS v0.2 合规自检"""
    print("\n" + "=" * 60)
    print("6️⃣ HAIS v0.2 合规自检")
    print("=" * 60)

    agent = HoloAgent(
        name="TestAgent",
        seed=KnowledgeSeed(
            identity="我是测试 Agent。",
            capability=["测试"],
            boundary="不执行写操作",
            voice="简洁",
            escalation="失败时通知",
        ),
        agent_id="test",
    )

    check = agent.hais_check()
    for k, v in check.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for sk, sv in v.items():
                print(f"    {sk}: {'✅' if sv else '❌'} {sv}")
        else:
            icon = "✅" if (isinstance(v, bool) and v) or (isinstance(v, int) and v <= 7) else "❌"
            print(f"  {k}: {icon} {v}")


# ============================================================
# Part 7: 安全演示
# ============================================================

def demo_security():
    """演示消息签名 + ACL"""
    print("\n" + "=" * 60)
    print("7️⃣ 安全系统演示")
    print("=" * 60)

    security = SecurityContext()

    # 注册 Agent
    translator_secret = security.register_agent("translator", "翻译 Agent")
    proofreader_secret = security.register_agent("proofreader", "校对 Agent")

    print(f"  已注册: {len(security.list_agents())} 个 Agent")

    # 签名消息
    msg = {
        "from": "translator",
        "to": "proofreader",
        "payload": "请校对这段翻译",
        "timestamp": time.time(),
    }
    msg["signature"] = security.sign("translator", msg)
    print(f"  消息已签名: {msg['signature'][:20]}...")

    # 验证
    valid = security.verify("translator", msg, msg["signature"])
    print(f"  签名验证: {'✅ 通过' if valid else '❌ 失败'}")

    # 篡改检测
    msg["payload"] = "篡改后的内容"
    tampered = security.verify("translator", msg, msg["signature"])
    print(f"  篡改检测: {'✅ 检测到篡改' if not tampered else '❌ 未检测到'}")

    # ACL
    can_exec = security.can("translator", "exec", "act")
    can_write_global = security.can("translator", "write", "global:secret")
    print(f"  ACL translator.exec('act'): {'✅' if can_exec else '❌'}")
    print(f"  ACL translator.write('global:secret'): {'❌' if not can_write_global else '✅'} (应拒绝)")

    return security


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n")
    print("╔══════════════════════════════════════════════╗")
    print("║     HAIS v0.2  多 Agent 全系统演示          ║")
    print("╚══════════════════════════════════════════════╝")

    results = {}

    results["memory"] = demo_memory_system()
    results["bus"] = demo_message_bus()
    results["collaborate"] = demo_collaborate()
    results["workflow"] = demo_workflow()
    results["orchestrator"] = demo_orchestrator()
    results["security"] = demo_security()
    demo_hais_check()

    print("\n" + "=" * 60)
    print("HAIS v0.2 演示总结")
    print("=" * 60)
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"  {status} {name}")
    print(f"\nHAIS v0.2 核心模块文件:")
    print(f"  holoagent/__init__.py     — 包入口")
    print(f"  holoagent/seed.py         — 5 段知识种子")
    print(f"  holoagent/memory.py       — 3 层记忆系统")
    print(f"  holoagent/core.py         — HoloAgent 基类")
    print(f"  holoagent/collaborator.py — collaborate() API + Workflow")
    print(f"  holoagent/message_bus.py  — HoloMessage 消息总线")
    print(f"  holoagent/security.py     — 身份 + 签名 + ACL")
    print(f"  holoagent/orchestrator.py — 任务编排器")
    print(f"  holoagent/examples/       — 示例 Agent + 演示")
    print()
