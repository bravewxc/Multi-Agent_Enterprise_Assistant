"""MongoDBStore 单元测试（直连本机 MongoDB）。

运行方式（PowerShell，src 目录）:
    $env:PYTHONUTF8='1'; .venv\\Scripts\\python.exe -m test.test_mongo_store

测试范围（对应改动验收，见 文档/修改记录.md 2026-10-13 条目）:
    1. put/get 往返           2. 覆盖写 value 更新
    3. put(value=None) 删除    4. 命名空间隔离（/memories/ vs /persisted-skills/）
    5. search 前缀匹配 + 分页  6. search filter（精确 + 列表成员）
    7. abatch 异步路径        8. 跨进程持久化（子进程写 → 本进程读，重启不丢）
"""
from __future__ import annotations

import asyncio
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from pymongo import MongoClient  # noqa: E402
from langgraph.store.base import SearchOp  # noqa: E402

from agent.backends.mongo_store import MongoDBStore  # noqa: E402

TEST_DB = "langchain_store_test"
TEST_COL = "stores_test"


def _make_store() -> MongoDBStore:
    client = MongoClient("mongodb://root:123456@127.0.0.1:27017/?authSource=admin")
    client.drop_database(TEST_DB)  # 每次全新开始，避免历史数据干扰断言
    return MongoDBStore(client, TEST_DB, TEST_COL)


def test_1_put_get_roundtrip(store: MongoDBStore) -> None:
    store.put(("laoxiao",), "/laoxiao/preferences.md", {"content": ["# 偏好", "recent_suppliers: []"]})
    item = store.get(("laoxiao",), "/laoxiao/preferences.md")
    assert item is not None, "put 后应能 get 到"
    assert item.key == "/laoxiao/preferences.md"
    assert item.namespace == ("laoxiao",), f"namespace 应为 tuple，实为 {type(item.namespace)}"
    assert item.value["content"][0] == "# 偏好"
    assert item.created_at is not None and item.updated_at is not None
    print("[PASS] 1. put/get 往返：Item 字段完整（value/key/namespace tuple/时间戳）")


def test_2_overwrite(store: MongoDBStore) -> None:
    ns, key = ("laoxiao",), "/laoxiao/preferences.md"
    store.put(ns, key, {"content": "v1"})
    store.put(ns, key, {"content": "v2"})
    item = store.get(ns, key)
    assert item is not None and item.value["content"] == "v2", "覆盖写应取到新值"
    print("[PASS] 2. 覆盖写：value 更新为 v2")


def test_3_delete_via_none_value(store: MongoDBStore) -> None:
    ns, key = ("laoxiao",), "/laoxiao/tmp.md"
    store.put(ns, key, {"content": "x"})
    store.put(ns, key, None)  # BaseStore 契约：value=None 即删除
    assert store.get(ns, key) is None, "put(value=None) 后 get 应返回 None"
    print("[PASS] 3. put(value=None) 删除：get 返回 None")


def test_4_namespace_isolation(store: MongoDBStore) -> None:
    # 对应两条路由的真实 namespace：/memories/ 按 user 隔离，/persisted-skills/ 全局
    store.put(("laoxiao",), "/laoxiao/preferences.md", {"content": "user-mem"})
    store.put(("skills",), "/order/web-scraper/SKILL.md", {"content": "skill"})
    assert store.get(("laoxiao",), "/order/web-scraper/SKILL.md") is None, \
        "用户命名空间不应看到技能命名空间的数据"
    assert store.get(("skills",), "/laoxiao/preferences.md") is None, \
        "技能命名空间不应看到用户记忆的数据"
    print("[PASS] 4. 命名空间隔离：('laoxiao',) 与 ('skills',) 互不可见")


def test_5_search_prefix_and_pagination(store: MongoDBStore) -> None:
    # 用独立命名空间，避免与 test_4 写入的 ('skills',) 文档相互干扰
    store.put(("page",), "/a.md", {"content": "1"})
    store.put(("page", "sub"), "/nested.md", {"content": "2"})
    store.put(("pagefoo",), "/not-in-prefix.md", {"content": "3"})

    # 前缀命中：自身 + 子命名空间
    hits = store.search(("page",))
    keys = {i.key for i in hits}
    assert keys == {"/a.md", "/nested.md"}, f"前缀应命中自身与子命名空间且仅此两者: {keys}"

    # 分页语义（StoreBackend._search_store_paginated 的循环依赖此行为）
    p1 = store.search(("page",), limit=1, offset=0)
    p2 = store.search(("page",), limit=1, offset=1)
    assert len(p1) == 1 and len(p2) == 1 and p1[0].key != p2[0].key, "limit/offset 应正确切片"
    assert len(store.search(("page",), limit=100, offset=2)) == 0, "越界 offset 应返回空"
    print("[PASS] 5. search 前缀匹配：命中自身/子命名空间、隔离 pagefoo，分页正确")


def test_6_search_filter(store: MongoDBStore) -> None:
    store.put(("filter-demo",), "a", {"status": "active", "tags": ["x"]})
    store.put(("filter-demo",), "b", {"status": "archived", "tags": ["y"]})

    exact = {i.key for i in store.search(("filter-demo",), filter={"status": "active"})}
    assert exact == {"a"}, f"精确匹配应只命中 a: {exact}"

    member = {i.key for i in store.search(("filter-demo",), filter={"tags": ["y", "z"]})}
    assert member == {"b"}, f"列表成员匹配应只命中 b: {member}"
    print("[PASS] 6. search filter：精确相等 + 列表成员匹配")


def test_7_abatch_async(store: MongoDBStore) -> None:
    async def _run() -> None:
        await store.aput(("async",), "k", {"content": "hello"})
        item = await store.aget(("async",), "k")
        assert item is not None and item.value["content"] == "hello"
        hits = await store.asearch(("async",))  # UserSkillsRestoreMiddleware 的调用方式
        assert any(i.key == "k" for i in hits)

    asyncio.run(_run())
    print("[PASS] 7. abatch 异步路径：aput/aget/asearch 正常")


def test_8_cross_process_persistence() -> None:
    """核心验收：子进程写入 → 本进程读取（模拟后端重启后记忆仍在）。

    子进程独立创建 MongoDBStore 并 put；本进程新起 store 实例 get——
    InMemoryStore 下这必然失败（进程内存），MongoDB 下必须成功。
    """
    child_code = (
        "import sys; sys.path.insert(0, r'{src}');\n"
        "from pymongo import MongoClient\n"
        "from agent.backends.mongo_store import MongoDBStore\n"
        "s = MongoDBStore(MongoClient('mongodb://root:123456@127.0.0.1:27017/?authSource=admin'), "
        f"'{{db}}', '{{col}}');\n"
        "s.put(('laoxiao',), '/laoxiao/restart-proof.md', {{'content': 'survived-restart'}})\n"
    ).format(src=str(((__import__('pathlib').Path(__file__)).parent.parent)).replace("\\", "/"),
             db=TEST_DB, col=TEST_COL)
    subprocess.run([sys.executable, "-c", child_code], check=True, timeout=60)

    # 新建第二个实例（不 drop 库），模拟"重启后的新进程"
    client = MongoClient("mongodb://root:123456@127.0.0.1:27017/?authSource=admin")
    fresh = MongoDBStore(client, TEST_DB, TEST_COL)
    item = fresh.get(("laoxiao",), "/laoxiao/restart-proof.md")
    assert item is not None and item.value["content"] == "survived-restart", \
        "跨进程读取失败——持久化未生效"
    print("[PASS] 8. 跨进程持久化：子进程写 → 新实例读（重启不丢）")


def main() -> None:
    store = _make_store()
    test_1_put_get_roundtrip(store)
    test_2_overwrite(store)
    test_3_delete_via_none_value(store)
    test_4_namespace_isolation(store)
    test_5_search_prefix_and_pagination(store)
    test_6_search_filter(store)
    test_7_abatch_async(store)
    test_8_cross_process_persistence()
    print("\n全部 8 项测试通过")


if __name__ == "__main__":
    main()
