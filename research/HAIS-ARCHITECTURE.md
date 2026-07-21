# HAIS 架构白皮书

> **HAIS** = Holographic Agent Interaction Standard  
> 版本: v0.2 | 状态: Draft  
> 用途: 本文件描述 HAIS 的完整技术栈和架构设计，**同时作为新 GitHub 仓库 `laimengjun/hais` 的根 README 和架构说明书**

---

## 一、为什么叫 HAIS

每个 Agent = 一个数字全息胚：
- **5 段种子** = 全息胚的 5 个功能区（identity, capability, boundary, voice, escalation）
- **7 API** = 全息胚的 7 个接口穴位（act, observe, reflect, escalate, remember, forget, collaborate）
- **API 数量守恒** ≤ 7

这不是比喻——这是**架构约束**。Agent 之间通过标准协议通信，数据被分层存储，交互轨迹形成图结构，而"发现潜在规律"就是在这个图结构上用图算法挖掘。

---

## 二、技术栈

| 层 | 技术 | 选型理由 |
|---|---|---|
| **Web 框架** | Flask 3.x | 轻量、稳定、生态成熟；后续可加 Flask-RESTx 自动文档 |
| **关系数据库** | MySQL 8.x | Agent 元数据、任务记录、审计日志、用户配置 |
| **图数据库** | Neo4j 5.x | Agent 交互图、知识图谱、模式发现、社区检测 |
| **API 协议** | REST + JSON | 简洁、通用、调试友好 |
| **Python 包** | `holoagent` | HAIS 协议的标准 Python 实现，pip install 可用 |
| **部署** | Docker Compose | API + MySQL + Neo4j 一键启动 |

### 为什么同时用 MySQL + Neo4j

| 场景 | MySQL | Neo4j |
|---|---|---|
| Agent 注册信息 | ✅ 主键/索引快查 | ❌ |
| 工作记忆（键值对） | ✅ 简单高效 | ❌ |
| 短期记忆历史 | ✅ 时序SQL查询 | ❌ |
| **Agent 协作网络** | ❌ JOIN 多层爆炸 | ✅ 纳秒级图遍历 |
| **知识关系发现** | ❌ 无法表达"多跳" | ✅ Cypher 原生 |
| **社区检测** | ❌ 无图算法 | ✅ Louvain/PageRank |
| **模式挖掘** | ❌ 无路径模式 | ✅ 子图匹配/频繁路径 |

**核心结论**：MySQL 存"物"，Neo4j 存"关系"。规律藏在关系里。

---

## 三、新仓库结构

```
laimengjun/hais/
├── README.md                    ← 本文件 + 快速开始
├── ARCHITECTURE.md              ← 详细架构说明（这份）
├── CHANGELOG.md
├── LICENSE                      ← Apache 2.0
│
├── hais/                        ← Python 包 (pip install hais)
│   ├── __init__.py
│   ├── protocol/                ← HAIS 协议标准
│   │   ├── message.py           ← HoloMessage Protocol v1.0
│   │   ├── seed.py              ← 5 段知识种子
│   │   └── api.py               ← 7 API 接口定义
│   │
│   ├── agent/                   ← Agent 运行时
│   │   ├── core.py              ← HoloAgent 基类
│   │   ├── memory.py            ← 三层记忆系统
│   │   └── lifecycle.py         ← Agent 生命周期管理
│   │
│   ├── bus/                     ← 消息总线
│   │   ├── protocol.py          ← 消息格式 + 序列化
│   │   ├── memory_bus.py        ← 内存总线（零依赖）
│   │   └── redis_bus.py         ← Redis 总线（生产）
│   │
│   ├── patterns/                ← 模式发现引擎 ⭐
│   │   ├── graph.py             ← Neo4j 客户端
│   │   ├── detectors.py         ← 模式检测器（协作模式/趋势/异常）
│   │   ├── community.py         ← 社区发现（Louvain/LPA）
│   │   └── forecaster.py        ← 趋势预测
│   │
│   ├── collaborator.py          ← collaborate() API
│   ├── orchestrator.py          ← 任务编排器
│   └── security.py              ← 身份 + 签名 + ACL
│
├── server/                      ← Flask REST API 服务
│   ├── app.py                   ← Flask app 工厂
│   ├── config.py                ← 配置（MySQL/Neo4j/Redis 连接）
│   ├── models/                  ← SQLAlchemy 模型 (MySQL)
│   │   ├── agent.py             ← Agent 元数据
│   │   ├── memory.py            ← 记忆记录
│   │   ├── task.py              ← 任务记录
│   │   └── audit.py             ← 审计日志
│   │
│   ├── routes/                  ← Flask 蓝图
│   │   ├── agents.py            ← /api/v1/agents CRUD
│   │   ├── memory.py            ← /api/v1/memory 读写
│   │   ├── tasks.py             ← /api/v1/tasks 编排
│   │   ├── graph.py             ← /api/v1/graph 图查询
│   │   └── patterns.py          ← /api/v1/patterns 模式发现 ⭐
│   │
│   ├── neo4j/                   ← Neo4j 集成
│   │   ├── client.py            ← 连接池 + Cypher 执行
│   │   ├── models.py            ← 图模型定义 (Node/Relation)
│   │   └── queries.py           ← 常用 Cypher 查询
│   │
│   └── tasks/                   ← 后台定时任务
│       ├── graph_builder.py     ← 从 MySQL 同步构建图
│       └── pattern_miner.py     ← 定时模式挖掘
│
├── neo4j/                       ← Neo4j 初始化
│   ├── schema.cypher            ← 图模型 DDL
│   └── seed.cypher              ← 示例数据
│
├── migrations/                  ← MySQL 迁移 (Flask-Migrate)
│   └── ...
│
├── docker-compose.yml           ← API + MySQL + Neo4j 一键启动
├── Dockerfile
├── requirements.txt
└── setup.py
```

---

## 四、MySQL 表结构

### 4.1 核心表一览

```sql
-- Agent 注册表
CREATE TABLE agents (
    id VARCHAR(64) PRIMARY KEY,         -- agent_id
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    seed_json JSON,                      -- 5段种子完整序列化
    status ENUM('active','paused','disabled') DEFAULT 'active',
    public_key TEXT,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_agents_status (status)
);

-- 工作记忆表 (键值对)
CREATE TABLE working_memory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    mem_key VARCHAR(255) NOT NULL,
    mem_value JSON NOT NULL,
    ttl_seconds INT DEFAULT NULL,       -- NULL = 不过期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP AS (IF(ttl_seconds IS NULL, NULL, created_at + INTERVAL ttl_seconds SECOND)),
    UNIQUE KEY uk_agent_key (agent_id, mem_key),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- 短期记忆 (对话/事件历史)
CREATE TABLE short_term_memory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    namespace VARCHAR(64) DEFAULT 'default',
    role ENUM('user','assistant','system','reflection','event') NOT NULL,
    content TEXT NOT NULL,
    importance FLOAT DEFAULT 0.5,
    metadata JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_stm_agent_ns (agent_id, namespace),
    INDEX idx_stm_created (created_at),
    FULLTEXT INDEX ftx_stm_content (content),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);

-- 任务执行记录
CREATE TABLE tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    plan_name VARCHAR(255),
    workflow_name VARCHAR(255),
    status ENUM('pending','running','success','failed') DEFAULT 'pending',
    stages_json JSON,                   -- 阶段执行详情
    total_time_ms INT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_created (created_at)
);

-- 审计日志
CREATE TABLE audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64),
    action VARCHAR(64) NOT NULL,         -- act/observe/collaborate/bus_send/etc
    target VARCHAR(255),
    detail JSON,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_audit_agent (agent_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at)
);
```

### 4.2 表关系图

```
agents ──┬─→ working_memory    (1:N 工作记忆)
         ├─→ short_term_memory (1:N 短期记忆)
         ├─→ audit_log         (1:N 审计)
         └─→ tasks             (N:M 参与的任务)
```

---

## 五、Neo4j 图模型

### 5.1 节点

```cypher
// Agent 节点
(:Agent {
    id: "translator",
    name: "翻译 Agent",
    capabilities: ["translation", "localization"],
    created_at: 1720000000,
    status: "active"
})

// 知识节点
(:Knowledge {
    id: "k-001",
    content: "全息生物学认为局部包含整体信息",
    type: "concept",         // concept / technique / fact / rule
    source: "reflection",    // reflection / observation / external
    confidence: 0.85,
    created_at: 1720000000
})

// 协作任务节点
(:Task {
    id: "t-001",
    name: "translate-doc",
    workflow: "translate-proofread",
    status: "success",
    total_time_ms: 35000,
    created_at: 1720000000
})

// 模式节点 (挖掘结果)
(:Pattern {
    id: "p-001",
    type: "collaboration_pattern",  // collaboration / knowledge / anomaly / trend
    description: "翻译→校对→摘要 三元组协作模式出现32次",
    frequency: 32,
    confidence: 0.91,
    detected_at: 1720000000
})
```

### 5.2 关系

```cypher
// Agent 之间的协作
(a1:Agent)-[:COLLABORATED_WITH {
    count: 128,
    avg_latency_ms: 35000,
    last_at: 1720000000,
    mode: "sequential"
}]->(a2:Agent)

// Agent 参与任务
(a:Agent)-[:PARTICIPATED_IN {
    role: "translator",
    latency_ms: 30950
}]->(t:Task)

// 知识归属
(k:Knowledge)-[:OWNED_BY]->(a:Agent)

// 知识间关联
(k1:Knowledge)-[:RELATES_TO {
    strength: 0.75,
    type: "supports"      // supports / contradicts / extends / refines
}]->(k2:Knowledge)

// 任务包含步骤
(t:Task)-[:HAS_STEP {
    order: 1,
    agent_id: "translator",
    latency_ms: 30950
}]->(:Step {name: "translate"})

// 模式基于证据
(p:Pattern)-[:EVIDENCED_BY {
    weight: 0.85
}]->(:Evidence {source: "task", task_id: "t-001"})
```

### 5.3 图模型总览

```
┌─────────┐     COLLABORATED_WITH     ┌─────────┐
│ Agent A │──────────────────────────→│ Agent B │
└────┬────┘                           └────┬────┘
     │                                     │
     │ OWNED_BY                            │ OWNED_BY
     ▼                                     ▼
┌─────────┐     RELATES_TO           ┌─────────┐
│ Knowl.1 │←─────────────────────────│ Knowl.2 │
└─────────┘                          └─────────┘
     │
     │ PARTICIPATED_IN
     ▼
┌─────────┐     HAS_STEP            ┌─────────┐
│ Task 1  │────────────────────────→│ Step 1  │
└─────────┘                         └─────────┘
     ▲
     │ EVIDENCED_BY
┌─────────┐
│ Pattern │
└─────────┘
```

---

## 六、模式发现引擎（🏆 核心亮点）

### 6.1 可发现的模式类型

| 模式类型 | 描述 | 图算法 | 业务价值 |
|---|---|---|---|
| **协作模式** | Agent 间的"最佳搭档"组合 | 频繁子图 / APRIORI | 优化任务分配 |
| **知识社区** | 哪些知识经常一起出现 | Louvain 社区检测 | 自动知识聚类 |
| **异常检测** | 异常的协作路径 / 延迟 | 路径异常分 | 报警/干预 |
| **趋势预测** | 哪些 Agent 协作变频繁 | 时序图分析 | 扩容/缩容决策 |
| **瓶颈发现** | 哪个 Agent 或步骤最慢 | 路径中位数 / P95 | 性能优化 |
| **全息规律** | 输入-输出模式映射 | 图嵌入 + 聚类 | 发现新的全息规律 |

### 6.2 模式 API 设计

```
GET  /api/v1/patterns                        ← 所有已发现的模式
GET  /api/v1/patterns/collaboration          ← 协作模式
GET  /api/v1/patterns/knowledge              ← 知识模式
GET  /api/v1/patterns/anomalies              ← 异常
GET  /api/v1/patterns/trends                 ← 趋势
POST /api/v1/patterns/mine                   ← 手动触发模式挖掘

GET  /api/v1/graph/agents/{id}/neighbors     ← Agent 的邻居（协作对象）
GET  /api/v1/graph/agents/{id}/path?to=xxx   ← 两个 Agent 间的协作路径
GET  /api/v1/graph/knowledge/search?q=xxx    ← 知识图谱搜索
```

### 6.3 核心 Cypher 查询示例

```cypher
-- 查"翻译→校对"的黄金搭档
MATCH (a:Agent)-[c:COLLABORATED_WITH]->(b:Agent)
WHERE a.id = "translator" AND b.id = "proofreader"
RETURN a.id, b.id, c.count, c.avg_latency_ms, c.last_at

-- 找最常用的协作三元组（频繁子图）
MATCH (a:Agent)-[:COLLABORATED_WITH]->(b:Agent)-[:COLLABORATED_WITH]->(c:Agent)
WHERE a.id < b.id AND b.id < c.id
RETURN a.id, b.id, c.id, count(*) AS frequency
ORDER BY frequency DESC
LIMIT 10

-- 找知识社区（Louvain 社区检测）
CALL gds.louvain.stream('knowledge-graph')
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).id AS knowledge, communityId
ORDER BY communityId

-- 检测异常协作（延迟远高于平均）
MATCH (a:Agent)-[c:COLLABORATED_WITH]->(b:Agent)
WITH a, b, c, c.avg_latency_ms AS latency,
     percentileCont(c.avg_latency_ms, 0.95) OVER() AS p95
WHERE latency > p95 * 1.5
RETURN a.id, b.id, latency, p95, "异常" AS label

-- 推荐"可能也应该协作"的 Agent（基于共同协作伙伴）
MATCH (a:Agent)-[:COLLABORATED_WITH]->(shared:Agent)<-[:COLLABORATED_WITH]-(b:Agent)
WHERE a.id = "translator" AND NOT (a)-[:COLLABORATED_WITH]->(b)
RETURN b.id, count(shared) AS common_partners
ORDER BY common_partners DESC
LIMIT 5
```

---

## 七、数据流

```
LLM Call (Agent 执行)
    │
    ▼
┌──────────────────────────────────────────────────────┐
│  Flask API Server                                    │
│  ├─ 记录 Agent 响应到 MySQL short_term_memory       │
│  ├─ 记录协作关系到 Neo4j COLLABORATED_WITH          │
│  └─ 记录审计日志                                     │
└──────────────────────────────────────────────────────┘
    │                            │
    ▼                            ▼
┌──────────┐            ┌──────────────┐
│  MySQL   │            │   Neo4j      │
│  (实体)  │            │  (关系)      │
└────┬─────┘            └──────┬───────┘
     │                          │
     ▼                          ▼
┌──────────────────────────────────────┐
│  后台定时任务                          │
│  ├─ graph_builder.py (5min)          │
│  │  → 从 MySQL 同步新数据到 Neo4j    │
│  └─ pattern_miner.py (1h)            │
│     → 在 Neo4j 上运行图算法          │
│     → 发现新模式 → 写入 Pattern 节点 │
└──────────────────────────────────────┘
```

---

## 八、快速开始（预览）

```bash
# 1. 克隆
git clone https://github.com/laimengjun/hais.git
cd hais

# 2. 启动基础设施
docker-compose up -d mysql neo4j

# 3. 初始化图模型
cat neo4j/schema.cypher | cypher-shell -u neo4j -p password

# 4. 安装 Python 包
pip install -e .

# 5. 启动 API
flask run --port 8000

# 6. 创建一个 Agent
curl -X POST http://localhost:8000/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "translator", "name": "翻译 Agent"}'

# 7. 发现模式
curl http://localhost:8000/api/v1/patterns

# 8. 查 Neo4j 协作图
curl http://localhost:8000/api/v1/graph/agents/translator/neighbors
```

---

## 九、v0.2 实现状态

| 模块 | 状态 | 位置 |
|---|---|---|
| HAIS 协议 (HoloMessage) | ✅ 完成 | `hais/protocol/` |
| 5段知识种子 | ✅ 完成 | `hais/protocol/seed.py` |
| HoloAgent 基类 | ✅ 完成 | `hais/agent/core.py` |
| 三层记忆系统 | ✅ 完成 | `hais/agent/memory.py` |
| 消息总线 (内存) | ✅ 完成 | `hais/bus/memory_bus.py` |
| collaborate() 协作 | ✅ 完成 | `hais/collaborator.py` |
| Workflow 引擎 | ✅ 完成 | `hais/collaborator.py` |
| 消息签名 + ACL | ✅ 完成 | `hais/security.py` |
| Orchestrator | ✅ 完成 | `hais/orchestrator.py` |
| Flask REST API | 📝 待编码 | `server/` |
| MySQL 模型 | 📝 待编码 | `server/models/` |
| Neo4j 集成 | 📝 待编码 | `server/neo4j/` |
| 模式发现引擎 | 📝 待编码 | `hais/patterns/` |
| Docker 化 | 📝 待编码 | `docker-compose.yml` |
| PyPI 发布 | 📝 待编码 | `setup.py` |

---

## 十、与全息生物学仓库的关系

```
laimengjun/holographic-biology     laimengjun/hais
──────────────────────────────     ─────────────────
理论 / 研究 / 专著                  工程 / 协议 / 框架
1.x ~ 9.x 理论文档                  Python 包 (pip install hais)
8.8 设计文档 (来源)                  docs/ 下的实现指南
医学验证 / 传感器标定                生产部署 / API 服务
GitHub Pages 静态站                  PyPI 包 + Docker
```

> HAIS 是全息生物学理论的 **工程实现标准**。  
> 理论在另一个仓库讲"为什么"，HAIS 在这个仓库讲"怎么做"。

---

© laimengjun@amoy 2026 — CC BY 4.0
