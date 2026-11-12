import chromadb

chroma_client = chromadb.Client()

collection = chroma_client.get_or_create_collection("Test_Collection")

documents = [
    {
        "id": "doc1", "text": "This is the first document."
    },
    {
        "id": "doc2", "text": "This is the second document."
    },
     {
        "id": "doc3", "text": "This is the third document."
    },    
]

for doc in documents:
    collection.upsert(ids =[doc["id"]], documents = [doc["text"]])


query = "third document"

results = collection.query(query_texts = [query], n_results=1)

print(results)