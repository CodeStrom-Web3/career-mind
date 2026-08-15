from cockroachdb.memory import (
    store_memory,
    get_user_memories,
    search_memories,
)
def test_memory_store_and_retrieve():
    user_id = "test_user_001"
    memory_id = store_memory(
        user_id=user_id,
        memory_type="test",
        content="User wants to become a Data Analyst",
        metadata={"source": "pytest"},
    )
    assert memory_id is not None
    memories = get_user_memories(
        user_id=user_id,
        limit=10,
    )
    assert len(memories) > 0
    assert any(
        "Data Analyst" in memory["content"]
        for memory in memories
    )
def test_memory_vector_search():
    results = search_memories(
        user_id="user_001",
        query_text="What career does the user want?",
        limit=5,
    )
    assert len(results) > 0
    assert any(
        "Data Analyst" in result["content"]
        for result in results
    )
