import os
from llama_index import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
import openai

from app.core.config import settings


index = None
doc_dir = "./documents"
index_dir = "./vector_store"
openai.api_key = settings.OPENAI_API_KEY


def initialize_index():
    global index
    storage_context = StorageContext.from_defaults()
    # if os.path.exists(index_dir):
    #     index = load_index_from_storage(storage_context)
    # else:
    documents = SimpleDirectoryReader(doc_dir).load_data()
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    storage_context.persist(index_dir)


def add_documents(filename: str):
    documents = SimpleDirectoryReader(doc_dir).load_data()
    for doc in documents:
        global index
        index.insert(doc)
    # Delete the original file
    os.remove(f"{doc_dir}/{filename}")


def query_index(query_text):
    global index
    query_engine = index.as_query_engine()
    result = query_engine.query(query_text)
    return str(result)
