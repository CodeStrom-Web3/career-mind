from cockroachdb.memory import store_memory

memory_id = store_memory(
    user_id="user_001",
    memory_type="career_goal",
    content="User wants to become a Data Analyst",
    metadata={"source": "conversation"},
)

print("Memory stored successfully!")
print("Memory ID:", memory_id)
