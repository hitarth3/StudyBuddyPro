from __future__ import annotations

"""
StudyBuddy Pro — Vector Store Manager

Manages ChromaDB vector store with HuggingFace embeddings for semantic search.
"""

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config.settings import settings
from utils.logger import get_logger

log = get_logger(__name__)


class VectorStoreManager:
    """Manages ChromaDB operations: add, search, delete documents."""

    def __init__(self) -> None:
        settings.ensure_directories()
        self._embeddings: HuggingFaceEmbeddings | None = None
        self._vectorstore: Chroma | None = None

    def _get_embeddings(self) -> HuggingFaceEmbeddings:
        """Lazy-load the embedding model."""
        if self._embeddings is None:
            log.info("Loading embedding model: %s", settings.embedding_model)
            self._embeddings = HuggingFaceEmbeddings(
                model_name=settings.embedding_model,
                model_kwargs={"device": settings.embedding_device},
                encode_kwargs={"normalize_embeddings": True},
            )
            log.info("Embedding model loaded successfully")
        return self._embeddings

    def _get_vectorstore(self) -> Chroma:
        """Lazy-load the ChromaDB vector store."""
        if self._vectorstore is None:
            self._vectorstore = Chroma(
                collection_name="studybuddy_docs",
                embedding_function=self._get_embeddings(),
                persist_directory=str(settings.chroma_dir),
            )
            log.info("ChromaDB initialized at %s", settings.chroma_dir)
        return self._vectorstore

    def add_documents(self, documents: list[Document]) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of LangChain Document objects with metadata.

        Returns:
            Number of documents successfully added.
        """
        if not documents:
            return 0

        vs = self._get_vectorstore()

        # Generate unique IDs from metadata
        ids = [doc.metadata.get("chunk_id", f"chunk_{i}") for i, doc in enumerate(documents)]

        try:
            vs.add_documents(documents=documents, ids=ids)
            log.info("Added %d documents to vector store", len(documents))
            return len(documents)
        except Exception as e:
            log.error("Failed to add documents: %s", e)
            raise

    def search(self, query: str, k: int | None = None,
               search_type: str | None = None,
               filter_dict: dict | None = None) -> list[Document]:
        """
        Search the vector store.

        Args:
            query: Search query string.
            k: Number of results (default from settings).
            search_type: "mmr" or "similarity" (default from settings).
            filter_dict: Optional metadata filter.

        Returns:
            List of matching Documents.
        """
        k = k or settings.retrieval_k
        search_type = search_type or settings.retrieval_search_type

        vs = self._get_vectorstore()

        try:
            if search_type == "mmr":
                results = vs.max_marginal_relevance_search(
                    query, k=k, fetch_k=k * 3, filter=filter_dict
                )
            else:
                results = vs.similarity_search(
                    query, k=k, filter=filter_dict
                )

            log.debug("Search returned %d results for query: %s",
                      len(results), query[:80])
            return results
        except Exception as e:
            log.error("Search failed: %s", e)
            return []

    def search_with_scores(self, query: str, k: int | None = None,
                           filter_dict: dict | None = None) -> list[tuple[Document, float]]:
        """Search and return documents with relevance scores."""
        k = k or settings.retrieval_k
        vs = self._get_vectorstore()

        try:
            results = vs.similarity_search_with_relevance_scores(
                query, k=k, filter=filter_dict
            )
            return results
        except Exception as e:
            log.error("Search with scores failed: %s", e)
            return []

    def search_by_keyword(self, keyword: str, document: str | None = None,
                          k: int = 10) -> list[Document]:
        """Search with optional document name filter."""
        filter_dict = None
        if document:
            filter_dict = {"source": document}
        return self.search(keyword, k=k, filter_dict=filter_dict)

    def get_all_documents(self) -> list[str]:
        """Get list of all unique document names in the store."""
        vs = self._get_vectorstore()
        try:
            collection = vs._collection
            result = collection.get(include=["metadatas"])
            sources = set()
            for meta in result.get("metadatas", []):
                if meta and "source" in meta:
                    sources.add(meta["source"])
            return sorted(sources)
        except Exception as e:
            log.error("Failed to get document list: %s", e)
            return []

    def delete_document(self, source_name: str) -> int:
        """Delete all chunks belonging to a specific document."""
        vs = self._get_vectorstore()
        try:
            collection = vs._collection
            # Get IDs for this document
            result = collection.get(
                where={"source": source_name},
                include=["metadatas"]
            )
            ids = result.get("ids", [])
            if ids:
                collection.delete(ids=ids)
                log.info("Deleted %d chunks for document: %s", len(ids), source_name)
            return len(ids)
        except Exception as e:
            log.error("Failed to delete document %s: %s", source_name, e)
            return 0

    def get_stats(self) -> dict:
        """Get vector store statistics."""
        vs = self._get_vectorstore()
        try:
            collection = vs._collection
            count = collection.count()
            documents = self.get_all_documents()
            return {
                "total_chunks": count,
                "total_documents": len(documents),
                "documents": documents,
            }
        except Exception as e:
            log.error("Failed to get stats: %s", e)
            return {"total_chunks": 0, "total_documents": 0, "documents": []}

    def get_context_for_topic(self, topic: str, k: int = 15) -> str:
        """Get a large context block for a topic (used by quiz/summary generators)."""
        results = self.search(topic, k=k)
        if not results:
            return ""
        return "\n\n---\n\n".join(doc.page_content for doc in results)


# Singleton
vector_store = VectorStoreManager()
