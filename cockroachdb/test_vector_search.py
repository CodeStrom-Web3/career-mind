from cockroachdb.memory import search_memories


user_id = "user_001"

query = "What career does the user want?"

results = search_memories(
    user_id=user_id,
    query_text=query,
    limit=5,
)

print("\nVector Search Results")
print("=" * 50)

for result in results:
    print(f"ID: {result['id']}")
    print(f"Content: {result['content']}")
    print(f"Distance: {result['distance']}")
    print("-" * 50)
