
from jsondata import get_json_data


def _cosine_similarity(left, right):
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = sum(a * a for a in left) ** 0.5
    right_norm = sum(b * b for b in right) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0
    return dot / (left_norm * right_norm)


class SimpleVectorStore:
    def __init__(self, documents, embeddings):
        self.documents = documents
        self.embeddings = embeddings
        self.document_vectors = embeddings.embed_documents(
            [doc.page_content for doc in documents]
        )

    def similarity_search(self, query, k=3):
        query_vector = self.embeddings.embed_query(query)
        scored_documents = [
            (_cosine_similarity(query_vector, vector), document)
            for document, vector in zip(self.documents, self.document_vectors)
        ]
        scored_documents.sort(key=lambda item: item[0], reverse=True)
        return [document for _, document in scored_documents[:k]]


class JournalRetriever:
    def __init__(self, documents, vectorstore):
        self.documents = documents
        self.vectorstore = vectorstore

    def invoke(self, query):
        query = query.strip()
        if not query:
            return []

        keyword_matches = [
            doc for doc in self.documents if query.lower() in doc.page_content.lower()
        ]
        if keyword_matches:
            return keyword_matches[:3]

        return self.vectorstore.similarity_search(query, k=3)


def get_retriever():
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ModuleNotFoundError:
        from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(
        model_name=r'D:\Python_virtualenv\Ceceliachenen\bge-large-zh-v1___5',
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True})
    json_data=get_json_data()

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    text_split=RecursiveCharacterTextSplitter(separators=["）","\n"],chunk_size=250,chunk_overlap=100)
    text_data=text_split.split_documents(json_data)
    retriever_vectore = SimpleVectorStore(text_data, embeddings)
    return JournalRetriever(json_data, retriever_vectore)
