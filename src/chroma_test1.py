import chromadb

client = chromadb.PersistentClient(path="./data")

collection = client.get_or_create_collection(
    name="knowledge_base"
)

collection.upsert(
    ids=[
        "python",
        "databases",
        "cooking",
        "fitness"
    ],
    documents=[
        "Python is a high level programming language commonly used for backend development, data analysis, automation, machine learning and artificial intelligence.",

        "A database is a system used to store, organize and retrieve structured information. SQL databases commonly use tables, rows and columns.",

        "Rice is commonly cooked by combining rice with water and heating it until the grains absorb the water and become soft.",

        "Running and walking are forms of cardiovascular exercise that can improve endurance and cardiovascular fitness when performed regularly."
    ]
)

print("Documents stored:", collection.count())

questions = [
    "What programming language is used for machine learning?",
    "How do I store structured information?",
    "How do I cook rice?",
    "What exercise improves cardiovascular fitness?"
]

for question in questions:

    results = collection.query(
        query_texts=[question],
        n_results=1
    )

    print("\nQuestion:")
    print(question)

    print("\nRetrieved document:")
    print(results["documents"][0][0])

    print("\nDistance:")
    print(results["distances"][0][0])