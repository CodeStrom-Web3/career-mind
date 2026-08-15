from cockroachdb.memory import get_user_memories


memories = get_user_memories(
    user_id="user_001",
    limit=10,
)

print("Retrieved memories:")

for memory in memories:
    print(memory)
