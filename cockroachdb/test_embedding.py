from cockroachdb.embeddings import generate_embedding


text = "User wants to become a Data Analyst"

embedding = generate_embedding(text)

print("Embedding generated successfully!")
print("Dimensions:", len(embedding))
print("First 5 values:", embedding[:5])
