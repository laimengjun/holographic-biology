"""
memory.py - HAIS v0.2 三层记忆系统

全息胚类比：记忆 = 全息胚的"经验积累"，随 session 增长而丰富

三层架构:
  工作记忆 (Working)   — Redis, 7±2 项, 纳秒级, 当前上下文
  短期记忆 (Short)     — SQLite, 1MB/Agent, 毫秒级, 当前 session 对话
  长期记忆 (Long)      — PostgreSQL+pgvector, 无限, 秒级, 跨 session 经验

设计参考：8.8-hais-v0.2-design.md §3.2, §6

隔离原则：
  每个 Agent 有独立 namespace (agent:{agent_id}:*)
  跨 Agent 访问需显式授权 (shared_memory ACL)
"""

from __future__ import annotations
import json
import os
import sqlite3
import time
import threading
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Optional
from enum import Enum


# ============================================================
# 记忆项数据结构
# ============================================================

@dataclass
class MemoryItem:
    """单条记忆记录"""
    id: Optional[int] = None
    agent_id: str = ""
    namespace: str = "default"
    role: str = "system"       # user / assistant / system / reflection
    content: str = ""
    importance: float = 0.5    # 0.0 ~ 1.0
    metadata: dict = field(default_factory=dict)
    created_at: float = 0.0
    last_accessed_at: float = 0.0
    access_count: int = 0

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "MemoryItem":
        return cls(
            id=row["id"],
            agent_id=row["agent_id"],
            namespace=row["namespace"],
            role=row["role"],
            content=row["content"],
            importance=row["importance"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
            last_accessed_at=row["last_accessed_at"],
            access_count=row["access_count"],
        )

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================
# 重要性评分 (v0.2 核心机制)
# ============================================================

def calculate_importance(content: str, metadata: dict = None) -> float:
    """计算一条信息的重要性评分 (0.0 ~ 1.0)

    评分因子：
      - 长度因子: 过短或过长的内容通常不重要
      - 特殊标记: 用户明确标记为重要
      - 实体密度: 含人名/数字/术语的内容更重要
      - 指令性: 含"记住"/"重要"/"注意"等关键词

    Returns:
        0.0 ~ 1.0 的评分
    """
    score = 0.3  # 基础分

    if not content or not content.strip():
        return 0.0

    content_lower = content.lower()
    metadata = metadata or {}

    # 1. 用户标记为重要 (+0.4)
    if metadata.get("user_important"):
        score += 0.4

    # 2. 含指令性关键词 (+0.2)
    important_keywords = ["记住", "重要", "注意", "关键", "务必",
                          "remember", "important", "critical", "key"]
    if any(kw in content_lower for kw in important_keywords):
        score += 0.2

    # 3. 含实体信息: 数字/人名/术语 (+0.1 ~ +0.3)
    has_number = bool(set(content) & set("0123456789"))
    if has_number:
        score += 0.1
    # 长内容可能含更多信息
    if 50 <= len(content) <= 2000:
        score += 0.1

    # 4. 重复出现 (由调用者检测，通过 metadata 传入)
    if metadata.get("repetition_count", 0) >= 2:
        score += 0.2 * min(metadata["repetition_count"], 5)

    # 5. 反思结果 (由 reflect() 标记)
    if metadata.get("is_reflection"):
        score += 0.3

    return min(score, 1.0)


# ============================================================
# 记忆隔离命名空间
# ============================================================

def agent_namespace(agent_id: str, namespace: str = "default") -> str:
    """生成 Agent 的隔离命名空间

    Args:
        agent_id: Agent 唯一 ID
        namespace: 子命名空间 (default / cache / glossary / shared)

    Returns:
        如 "agent:translator:default"
    """
    return f"agent:{agent_id}:{namespace}"


# ============================================================
# Layer 1: 工作记忆 (内存 dict, 7±2 项限制)
# ============================================================

class WorkingMemory:
    """工作记忆 — 当前上下文的暂存区

    全息胚类比：工作记忆 ≈ 细胞当前感知的环境信号

    特性：
      - 纯内存存储 (纳秒级)
      - 容量限制 7±2 项 (Miller's Law for cognition)
      - TTL 自动过期
      - 按 Agent namespace 隔离

    注意：这是最小实现。生产环境应替换为 Redis。
    """

    def __init__(self, agent_id: str, max_items: int = 9):
        self.agent_id = agent_id
        self.max_items = max_items
        self._store: dict[str, tuple[Any, float]] = {}  # key -> (value, expiry_ts)
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """设置工作记忆项

        Args:
            key: 键名 (将在内部加上 agent namespace)
            value: 值
            ttl: 过期秒数 (None = 不过期)
        """
        ns_key = agent_namespace(self.agent_id, key)
        expiry = (time.time() + ttl) if ttl else 0.0
        with self._lock:
            # 容量检查: 超过限制时淘汰最旧的非锁定项
            if len(self._store) >= self.max_items and ns_key not in self._store:
                self._evict_one()
            self._store[ns_key] = (value, expiry)

    def get(self, key: str, default: Any = None) -> Any:
        """获取工作记忆项，自动处理过期"""
        ns_key = agent_namespace(self.agent_id, key)
        with self._lock:
            item = self._store.get(ns_key)
            if item is None:
                return default
            value, expiry = item
            if expiry and time.time() > expiry:
                del self._store[ns_key]
                return default
            return value

    def delete(self, key: str) -> bool:
        """删除工作记忆项"""
        ns_key = agent_namespace(self.agent_id, key)
        with self._lock:
            return self._store.pop(ns_key, None) is not None

    def clear(self) -> None:
        """清空工作记忆"""
        with self._lock:
            self._store.clear()

    def keys(self) -> list[str]:
        """返回当前所有 key (不含 namespace 前缀)"""
        prefix = f"agent:{self.agent_id}:"
        with self._lock:
            return [k[len(prefix):] for k in self._store if k.startswith(prefix)]

    def size(self) -> int:
        """当前项数"""
        with self._lock:
            return len(self._store)

    def _evict_one(self) -> None:
        """淘汰最旧的项 (LRU 近似)"""
        if not self._store:
            return
        oldest_key = min(self._store, key=lambda k: self._store[k][1])
        del self._store[oldest_key]


# ============================================================
# Layer 2: 短期记忆 (SQLite)
# ============================================================

_SHORT_MEMORY_LOCKS: dict[str, threading.Lock] = {}
_GLOBAL_SHORT_LOCK = threading.Lock()


class ShortTermMemory:
    """短期记忆 — 当前 session 的对话历史

    全息胚类比：短期记忆 ≈ 细胞最近几秒的信号捕获

    特性：
      - SQLite 存储 (轻量，零配置)
      - 按 agent_id + session_id 隔离
      - 全文搜索 (SQLite FTS5)
      - 自动裁剪：超过 max_records 时清理最低重要性的记录
      - 每个 agent 独立数据库文件 (可选: 共享数据库 + namespace)

    用法：
        memory = ShortTermMemory("translator", db_path="./data/short_term.db")
        memory.append("user", "帮我翻译这段话")
        results = memory.search("翻译", top_k=5)
    """

    def __init__(
        self,
        agent_id: str,
        db_path: Optional[str] = None,
        max_records: int = 500,
    ):
        """
        Args:
            agent_id: Agent 唯一 ID (用于 namespace 隔离)
            db_path: SQLite 文件路径 (默认: ./data/short_term_{agent_id}.db)
            max_records: 最大记录数，超过时自动裁剪
        """
        self.agent_id = agent_id
        self.max_records = max_records
        if db_path is None:
            data_dir = Path("./data")
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / f"short_term_{agent_id}.db")
        self._db_path = db_path
        # 每个 db 文件独立线程锁
        with _GLOBAL_SHORT_LOCK:
            if db_path not in _SHORT_MEMORY_LOCKS:
                _SHORT_MEMORY_LOCKS[db_path] = threading.Lock()
        self._lock = _SHORT_MEMORY_LOCKS[db_path]
        self._init_db()

    def _init_db(self) -> None:
        """初始化数据库表 + FTS"""
        with self._lock, sqlite3.connect(self._db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS short_term_memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    namespace TEXT NOT NULL DEFAULT 'default',
                    role TEXT NOT NULL DEFAULT 'user',
                    content TEXT NOT NULL,
                    importance REAL DEFAULT 0.5,
                    metadata TEXT DEFAULT '{}',
                    created_at REAL NOT NULL,
                    last_accessed_at REAL NOT NULL,
                    access_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_stm_agent_ns
                ON short_term_memory(agent_id, namespace)
            """)
            # FTS5 全文搜索
            try:
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS short_term_memory_fts
                    USING fts5(agent_id, namespace, content, content=short_term_memory)
                """)
            except Exception:
                pass  # FTS 不可用时可接受
            conn.commit()

    def append(
        self,
        role: str,
        content: str,
        metadata: dict = None,
        namespace: str = "default",
        importance: Optional[float] = None,
    ) -> int:
        """追加一条短期记忆

        Returns:
            新记录的 ID
        """
        now = time.time()
        imp = importance if importance is not None else calculate_importance(content, metadata)
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)
        with self._lock, sqlite3.connect(self._db_path) as conn:
            cur = conn.execute("""
                INSERT INTO short_term_memory
                    (agent_id, namespace, role, content, importance, metadata,
                     created_at, last_accessed_at, access_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """, (self.agent_id, namespace, role, content, imp, meta_json, now, now))
            record_id = cur.lastrowid
            # 更新 FTS 索引
            try:
                conn.execute("""
                    INSERT INTO short_term_memory_fts(rowid, agent_id, namespace, content)
                    VALUES (?, ?, ?, ?)
                """, (record_id, self.agent_id, namespace, content))
            except Exception:
                pass
            # 检查容量，超限时清理
            self._maybe_trim(conn)
            conn.commit()
        return record_id

    def search(
        self,
        query: str,
        top_k: int = 10,
        namespace: str = "default",
    ) -> list[MemoryItem]:
        """全文搜索短期记忆"""
        results = []
        try:
            with self._lock, sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT m.* FROM short_term_memory m
                    JOIN short_term_memory_fts fts ON m.id = fts.rowid
                    WHERE short_term_memory_fts MATCH ?
                      AND m.agent_id = ? AND m.namespace = ?
                    ORDER BY rank
                    LIMIT ?
                """, (query, self.agent_id, namespace, top_k)).fetchall()
                for row in rows:
                    results.append(MemoryItem.from_row(row))
        except Exception:
            # FTS 失败时 fallback 到 LIKE 搜索
            with self._lock, sqlite3.connect(self._db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("""
                    SELECT * FROM short_term_memory
                    WHERE agent_id = ? AND namespace = ?
                      AND (content LIKE ? OR content LIKE ?)
                    ORDER BY importance DESC, created_at DESC
                    LIMIT ?
                """, (self.agent_id, namespace, f"%{query}%", f"%{query}%", top_k)).fetchall()
                for row in rows:
                    results.append(MemoryItem.from_row(row))
        # 更新访问时间
        if results:
            ids = [r.id for r in results if r.id]
            with self._lock, sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    f"UPDATE short_term_memory SET last_accessed_at=?, access_count=access_count+1 "
                    f"WHERE id IN ({','.join('?' * len(ids))})",
                    [time.time()] + ids
                )
                conn.commit()
        return results

    def get_recent(self, n: int = 20, namespace: str = "default") -> list[MemoryItem]:
        """获取最近的 n 条记忆"""
        with self._lock, sqlite3.connect(self._db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM short_term_memory
                WHERE agent_id = ? AND namespace = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (self.agent_id, namespace, n)).fetchall()
            return [MemoryItem.from_row(r) for r in rows]

    def count(self, namespace: str = "default") -> int:
        """当前记忆条数"""
        with self._lock, sqlite3.connect(self._db_path) as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS cnt FROM short_term_memory WHERE agent_id=? AND namespace=?",
                (self.agent_id, namespace)
            ).fetchone()
            return row[0] if row else 0

    def clear(self, namespace: str = "default") -> None:
        """清空短期记忆"""
        with self._lock, sqlite3.connect(self._db_path) as conn:
            conn.execute(
                "DELETE FROM short_term_memory WHERE agent_id=? AND namespace=?",
                (self.agent_id, namespace)
            )
            conn.commit()

    def _maybe_trim(self, conn: sqlite3.Connection) -> None:
        """超限时清理最低重要性 + 最旧的记录"""
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM short_term_memory WHERE agent_id=?",
            (self.agent_id,)
        ).fetchone()
        if row and row[0] > self.max_records:
            excess = row[0] - self.max_records + 50  # 多清理一点
            conn.execute("""
                DELETE FROM short_term_memory
                WHERE id IN (
                    SELECT id FROM short_term_memory
                    WHERE agent_id = ?
                    ORDER BY importance ASC, last_accessed_at ASC
                    LIMIT ?
                )
            """, (self.agent_id, excess))
            try:
                conn.execute("INSERT INTO short_term_memory_fts(short_term_memory_fts) VALUES('rebuild')")
            except Exception:
                pass

    @property
    def db_path(self) -> str:
        return self._db_path


# ============================================================
# Layer 3: 长期记忆 (PostgreSQL + pgvector 适配器)
# ============================================================

class LongTermMemory:
    """长期记忆 — 跨 session 的经验积累

    全息胚类比：长期记忆 ≈ 细胞分化和"经验"的长期存储

    特性：
      - 基于向量相似度搜索 (需要 PG + pgvector)
      - 自动重要性评分
      - 跨 session 保留
      - 支持 embedding 的抽象接口

    注意：这是一个**适配器基类**，具体实现需要 pgvector 环境。
    如果 pgvector 不可用，可以：
      A. 使用本地向量搜索 (chromadb / faiss)
      B. 降级为关键词搜索 (沿用 SQLite FTS)
      C. 暂时关闭长期记忆 (不影响核心功能)

    当前实现提供：
      1. StubLongTermMemory - 内存向量搜索 (faiss-like, 纯 Python)
      2. PgvectorLongTermMemory - 生产级 (需 PostgreSQL + pgvector)
    """

    def store(self, agent_id: str, content: str, metadata: dict = None,
              importance: Optional[float] = None) -> int:
        """存储到长期记忆"""
        raise NotImplementedError

    def recall(self, query: str, agent_id: str, top_k: int = 5) -> list[MemoryItem]:
        """从长期记忆检索"""
        raise NotImplementedError

    def get_recent(self, agent_id: str, n: int = 20) -> list[MemoryItem]:
        """获取最近的记忆"""
        raise NotImplementedError


class StubLongTermMemory(LongTermMemory):
    """最小实现：内存向量搜索 (无外部依赖)

    适用于开发/测试环境。生产环境建议用 pgvector。

    注意：
      - 使用简单的 TF-IDF 近似，而非真实 embedding
      - 仅适合原型验证，不支持大规模检索
    """

    def __init__(self):
        self._store: dict[str, list[MemoryItem]] = {}  # agent_id -> [items]
        self._lock = threading.Lock()

    def store(self, agent_id: str, content: str, metadata: dict = None,
              importance: Optional[float] = None) -> int:
        imp = importance if importance is not None else calculate_importance(content, metadata)
        item = MemoryItem(
            agent_id=agent_id,
            namespace="long_term",
            role="reflection",
            content=content,
            importance=imp,
            metadata=metadata or {},
            created_at=time.time(),
            last_accessed_at=time.time(),
        )
        with self._lock:
            if agent_id not in self._store:
                self._store[agent_id] = []
            self._store[agent_id].append(item)
            item.id = len(self._store[agent_id])
            # 按重要性排序，只保留 top 1000
            self._store[agent_id].sort(key=lambda x: x.importance, reverse=True)
            self._store[agent_id] = self._store[agent_id][:1000]
        return item.id

    def recall(self, query: str, agent_id: str, top_k: int = 5) -> list[MemoryItem]:
        """使用关键词匹配 + 重要性排序的简易检索"""
        with self._lock:
            items = self._store.get(agent_id, [])
        query_lower = query.lower()
        query_words = set(query_lower.split())

        scored = []
        for item in items:
            # 关键词重叠度
            content_lower = item.content.lower()
            match_count = sum(1 for w in query_words if w in content_lower)
            match_ratio = match_count / max(len(query_words), 1)
            # 最终分 = 关键词匹配 * 0.4 + 重要性 * 0.4 + 新鲜度 * 0.2
            recency = 1.0 - min((time.time() - item.created_at) / (86400 * 30), 1.0)  # 30 天衰减
            score = match_ratio * 0.4 + item.importance * 0.4 + recency * 0.2
            if match_ratio > 0:
                scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:top_k]]

    def get_recent(self, agent_id: str, n: int = 20) -> list[MemoryItem]:
        with self._lock:
            items = self._store.get(agent_id, [])
        return sorted(items, key=lambda x: x.created_at, reverse=True)[:n]


# ============================================================
# 记忆系统总控
# ============================================================

class MemorySystem:
    """三层记忆系统的统一入口

    提供：
      - 统一 API (set / get / search / store / recall / append)
      - 自动路由到正确的记忆层
      - 记忆提升管道 (working → short → long)
      - 记忆隔离 (按 agent_id)

    用法：
        memory = MemorySystem("translator")
        memory.set("current_task", "翻译文档")        # 工作记忆
        memory.append("user", "帮我翻译这段话")        # 短期记忆
        memory.store("用户偏好正式风格", importance=0.8) # 长期记忆
        results = memory.search("翻译风格")            # 检索所有层
    """

    def __init__(
        self,
        agent_id: str,
        enable_long_term: bool = False,
        short_term_db: Optional[str] = None,
    ):
        """
        Args:
            agent_id: Agent 唯一 ID (用于隔离)
            enable_long_term: 是否启用长期记忆 (默认关闭，需显式开启)
            short_term_db: 短期记忆的 SQLite 路径
        """
        self.agent_id = agent_id
        self.working = WorkingMemory(agent_id)
        self.short = ShortTermMemory(agent_id, db_path=short_term_db)
        self.long: LongTermMemory = StubLongTermMemory() if enable_long_term else None
        self._enable_long = enable_long_term

    # ── 工作记忆 ──
    def set(self, key: str, value: Any, ttl: float = None) -> None:
        """写入工作记忆"""
        self.working.set(key, value, ttl)

    def get(self, key: str, default: Any = None) -> Any:
        """读取工作记忆"""
        return self.working.get(key, default)

    # ── 短期记忆 ──
    def append(self, role: str, content: str, metadata: dict = None,
               namespace: str = "default") -> int:
        """追加短期记忆 (自动评估重要性)"""
        return self.short.append(role, content, metadata, namespace)

    def search(self, query: str, top_k: int = 10,
               include_long: bool = True) -> dict[str, list[MemoryItem]]:
        """检索所有层记忆

        Returns:
            {"short": [...], "long": [...]}
        """
        result = {}
        result["short"] = self.short.search(query, top_k=top_k)
        if include_long and self._enable_long and self.long:
            result["long"] = self.long.recall(query, self.agent_id, top_k=top_k)
        return result

    def get_recent(self, n: int = 20) -> list[MemoryItem]:
        """获取最近的短期记忆"""
        return self.short.get_recent(n)

    # ── 长期记忆 ──
    def store(self, content: str, metadata: dict = None,
              importance: Optional[float] = None) -> Optional[int]:
        """写入长期记忆 (需 enable_long_term=True)"""
        if not self._enable_long or not self.long:
            return None
        return self.long.store(self.agent_id, content, metadata, importance)

    def recall(self, query: str, top_k: int = 5) -> list[MemoryItem]:
        """从长期记忆检索"""
        if not self._enable_long or not self.long:
            return []
        return self.long.recall(query, self.agent_id, top_k=top_k)

    # ── 记忆提升管道 ──
    def promote_to_long_term(self, min_importance: float = 0.7) -> int:
        """把短期记忆中重要性 > 阈值的项提升到长期记忆

        这是记忆管道的核心：工作记忆 → 短期记忆 → 长期记忆
        """
        if not self._enable_long or not self.long:
            return 0
        recent = self.short.get_recent(n=100)
        promoted = 0
        for item in recent:
            if item.importance >= min_importance:
                mid = self.long.store(
                    self.agent_id, item.content,
                    metadata={"source": "short_term_promotion", "original_id": item.id},
                    importance=item.importance,
                )
                if mid is not None:
                    promoted += 1
        return promoted

    # ── 清理 ──
    def clear_working(self) -> None:
        """清空工作记忆"""
        self.working.clear()

    def clear_short(self, namespace: str = "default") -> None:
        """清空短期记忆"""
        self.short.clear(namespace)

    # ── 状态 ──
    def stats(self) -> dict:
        """记忆系统统计"""
        return {
            "agent_id": self.agent_id,
            "working_items": self.working.size(),
            "short_term_count": self.short.count(),
            "long_term_enabled": self._enable_long,
            "long_term_count": "N/A" if not self._enable_long else "stub",
        }
