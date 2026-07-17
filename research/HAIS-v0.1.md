# HAIS v0.1 · HoloAgent Interface Standard
> **日期**: 2026-07-01

---

## 0. 一句话定义

**HAIS** = 一个让 AI Agent **像元DNA一样自包含**的接口标准。每个 Agent 内嵌 5 段"知识种子"，对外只暴露 3-7 个 API，可以独立部署、独立调试、独立协作。

---

## 1. 设计哲学（与张颖清生物全息律的映射）

| 张颖清概念 | HAIS 原则 |
|----------|----------|
| 元DNA（ECIWO） | 自包含 Agent |
| 部分包含整体信息 | Agent 内嵌系统种子 |
| 第二掌骨节肢系统 | 少量、规范、与能力对应的 API |
| 全息刮痧 | 局部刺激调节整体 |
| 泛胚论 | 通用 Agent 模板 |

---

## 2. 5 段知识种子（Knowledge Seed）

每个 HoloAgent **必须**包含 5 段文本，构成"包含整体信息的胚胎"：

```yaml
# HoloAgent Knowledge Seed v0.1

identity: |            # 段 1：我是谁（1-2 句）
  你是 [Agent Name]。
  你是 [父系统] 的子代理，专门负责 [职责范围]。

capability: |          # 段 2：我能做什么（3-5 项，列表）
  - 能力 1: ...
  - 能力 2: ...
  - 能力 3: ...
  - 能力 4: ...
  - 能力 5: ...

boundary: |            # 段 3：我不能做什么（1-2 项）
  我不应该：[超出职责的事情]。
  我应该转交给：[其他 Agent / 主人] 当 [触发条件]。

voice: |               # 段 4：我如何回应（风格/语气/格式）
  风格：[正式/轻松/技术/...]
  语气：[友好/简洁/...].
  格式：[Markdown/纯文本/JSON/...]
  长度：[短: <100 字 / 中: 100-500 字 / 长: >500 字]

escalation: |          # 段 5：何时升级（找其他 Agent / 主人）
  当用户询问 [类别 A] 时，转交 [其他 Agent X].
  当 [条件 B] 发生时，请求主人确认。
  当紧急时，直接呼叫 [紧急联系人].
```

### 2.1 种子模板（最小可工作示例）

```yaml
identity: |
  你是 "翻译 Agent"。
  你是 "OpenClaw" 系统的子代理，专门负责中英互译。

capability:
  - 能力 1: 把中文翻译成英文
  - 能力 2: 把英文翻译成中文
  - 能力 3: 处理技术术语，保持专业性
  - 能力 4: 保留原文的语气和风格
  - 能力 5: 一次最多处理 5000 字

boundary: |
  我不应该：翻译代码（应转给代码 Agent）。
  我不应该：翻译长文档 >5000 字（应分块或转给文档 Agent）。

voice: |
  风格：专业、准确。
  语气：简洁。
  格式：纯文本，不加 Markdown 装饰。
  长度：中（100-500 字）。

escalation: |
  当用户要求翻译涉及医疗/法律时，转交专业翻译 Agent。
  当原文有歧义时，询问用户澄清。
  当用户连续 3 次不满意时，请求主人介入。
```

---

## 3. 7 个核心 API（暴露原则）

每个 HoloAgent 对外**最多**暴露 7 个 API（**第二掌骨节肢系统**原则——少量、规范、与能力对应）。

### 3.1 必选 API（3 个）

```python
class HoloAgent:
    def act(self, input: str) -> str:
        """处理输入，返回响应。Agent 的核心调用入口。"""

    def observe(self, context: dict) -> None:
        """接收外部状态变化（如新消息、环境变量），更新内部状态。"""

    def reflect(self, feedback: str) -> None:
        """接收反馈（如用户评价、外部评估），用于内部学习/调整。"""
```

### 3.2 扩展 API（最多 4 个可选）

```python
class HoloAgent:
    def escalate(self, reason: str) -> bool:
        """请求升级到其他 Agent 或主人。返回是否成功转交。"""

    def remember(self, key: str, value: Any) -> None:
        """存储信息到 Agent 的私有记忆（跨调用保持）。"""

    def forget(self, key: str) -> bool:
        """删除记忆。"""

    def handoff(self, target: 'HoloAgent', payload: dict) -> None:
        """把当前任务转交给另一个 HoloAgent。"""
```

### 3.3 API 数量守恒

- **最少**: 1 个（仅 `act`）—— 用于纯响应型 Agent
- **推荐**: 3 个（act + observe + reflect）—— 通用 Agent
- **最多**: 7 个（3 必选 + 4 扩展）
- **超过 7 个**: ⚠️ 警告，可能违反"穴位图"原则，建议拆分 Agent

---

## 4. 文件结构（单文件优先）

```
my_holo_agent/
├── SKILL.md          # 知识种子（5 段 YAML）+ API 文档
├── agent.py          # HoloAgent 子类实现（< 200 行）
├── test.py           # 单测（可选）
└── README.md         # 部署说明（可选）
```

### 4.1 SKILL.md 模板

```markdown
# [Agent Name]

## Identity
[段 1]

## Capability
[段 2]

## Boundary
[段 3]

## Voice
[段 4]

## Escalation
[段 5]

## API
- act(input) -> str
- observe(context) -> None
- reflect(feedback) -> None
[可选扩展]

## Dependencies
- LLM: [默认模型]
- Memory: [可选后端]
- Tools: [可选工具]
```

---

## 5. 与现有框架的映射

| HAIS | OpenAI Function Calling | LangChain | AutoGen |
|------|------------------------|-----------|---------|
| `act()` | Function call | Tool invoke | Send message |
| `observe()` | Message role: user | Input variable | Receive message |
| `reflect()` | Feedback API | Memory update | User feedback |
| Knowledge Seed | System prompt | Prompt template | System message |
| API count | Many tools | Many chains | Many agents |

**HAIS 的差异**：
- 限制 API 数量（≤7）
- 强制 5 段种子结构
- 优先单文件部署
- 强调"自包含"和"独立调试"

---

## 6. 多 Agent 协作（**元DNA间通讯**）

```python
# 协作示例
agent_a = AgentA()  # 翻译 Agent
agent_b = AgentB()  # 校对 Agent

# Agent A 翻译后，转交 Agent B 校对
text_en = agent_a.act(zh_text)
agent_a.handoff(agent_b, {"text": text_en, "task": "proofread"})
final_text = agent_b.act(text_en)  # Agent B 处理校对
```

**协作原则**：
1. **每个 Agent 只知道自己的知识种子**，不知道其他 Agent 的内部状态
2. **协作通过 handoff() 和 escalate()** 完成，不共享内存
3. **协作链条应该短**（≤ 3 个 Agent 串联）—— 避免"元DNA间信号衰减"

---

## 7. 调试方法论（**全息刮痧式**）

```
调试流程：
1. 哪个 Agent 表现异常？ → 定位 "病灶"
2. 该 Agent 的哪个 skill / prompt 段是"穴位"？ → 找"穴"
3. 只调整 1-2 个变量 → "小刺激"
4. 观察整个系统行为 → "全身反应"
5. 必要时换另一个 Agent → "邻近穴位"
```

**反模式**：每次出问题都重写整个 prompt → 不可控、不可逆、不可学习。

---

## 8. 安全与边界

每个 HoloAgent **必须**在 `boundary` 段明确写出：
- 不能做什么
- 何时转交其他 Agent
- 何时请求主人确认
- 紧急情况的处理

**核心安全原则**：Agent **不知道**其他 Agent 的内部实现细节 → 即使一个 Agent 被攻破，影响也局限在该 Agent 内。

---

## 9. 版本与演进

- **v0.1**（当前）：5 段种子 + 3-7 个 API + 单文件部署
- **v0.2**（计划）：加入记忆隔离层 + 跨 Agent 消息总线
- **v1.0**（远期）：标准化注册中心 + 跨语言互操作

---

## 10. 一句话总结

> **HAIS = "每个 Agent 像元DNA一样自包含"。**
> **5 段种子 + 7 个 API + 单文件部署。**

---

## 附录 A：违反 HAIS 原则的反模式

❌ **"大 Agent"**（API > 7 个）
❌ **"空 Agent"**（无知识种子）
❌ **"耦合 Agent"**（Agent 间共享内部状态）
❌ **"无限递归"**（Agent 间转交 > 3 层）
❌ **"无边界 Agent"**（不写 boundary 段）

---

## 附录 B：参考实现

参见 `holo_agent_prototype.py` —— 最小可工作 HoloAgent 原型，约 80 行 Python。

---

_本草案是阶段 4.3 的实施起点。下一步：写最小原型 → 对比 LangChain → 集成 OpenClaw → 走通 wechat 通道。_