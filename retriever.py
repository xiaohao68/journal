from jsondata import get_json_data


def _query_score(query, text):
    query = query.lower()
    text = text.lower()
    if query in text:
        return len(query) + 100

    query_chars = [char for char in query if not char.isspace()]
    if not query_chars:
        return 0

    return sum(text.count(char) for char in query_chars)


class JournalRetriever:
    def __init__(self, documents):
        self.documents = documents

    def invoke(self, query):
        query = query.strip()
        if not query:
            return []

        scored_documents = [
            (_query_score(query, document.page_content), document)
            for document in self.documents
        ]
        scored_documents.sort(key=lambda item: item[0], reverse=True)
        return [document for score, document in scored_documents[:3] if score > 0]


def get_retriever():
    return JournalRetriever(get_json_data())
