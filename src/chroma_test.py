import chromadb
client=chromadb.PersistentClient(path="./data")
collection=client.get_or_create_collection(name="knowledge_base")
collection.add(ids=["python-1"], documents=["Python is a high level language commonly used for backend developement, data analysis, automation, machine learning and artificial intelligence "])
print("Document stored:", collection.count())

results=collection.query(query_texts=["What is Python?"], n_results=1)
print("\nRetrieved Document:")
print (results['documents'][0][0])