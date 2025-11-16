"""
RAG Vector Store for Multi-Agent Knowledge Management

This module implements a production-ready RAG system with:
- Multi-tenancy (isolated agent memory + shared organizational knowledge)
- Automatic knowledge ingestion from research reports
- Semantic search for agent memory retrieval
- ChromaDB for local vector storage with persistence

Based on research: "RAG Integration Architecture for Multi-Agent Platform"
"""

import os
import logging
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

logger = logging.getLogger(__name__)


class AgentVectorStore:
    """
    Multi-tenant vector store for agent memory and organizational knowledge.

    Uses ChromaDB with separate collections for:
    - Agent private memory (per agent)
    - Shared organizational knowledge (accessible to all agents)
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_data",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize the vector store with persistence.

        Args:
            persist_directory: Directory for persisting Chroma data
            embedding_model: SentenceTransformer model for embeddings
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)

        logger.info(f"Initializing AgentVectorStore with persist_directory: {persist_directory}")
        logger.info(f"Using embedding model: {embedding_model}")

        # Initialize embedding model
        self.embeddings = SentenceTransformerEmbeddings(model_name=embedding_model)

        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        # Cache for Chroma collections to avoid re-initialization
        self._collection_cache: Dict[str, Chroma] = {}

        logger.info("✅ AgentVectorStore initialized successfully")

    def _get_collection_name(self, agent_id: Optional[str], is_shared: bool = False) -> str:
        """
        Get collection name based on multi-tenancy strategy.

        Args:
            agent_id: Agent identifier for private memory
            is_shared: Whether this is shared organizational knowledge

        Returns:
            Collection name string
        """
        if is_shared:
            return "shared_organizational_knowledge"
        elif agent_id:
            return f"agent_private_memory_{agent_id}"
        else:
            raise ValueError("Must provide agent_id for private memory or set is_shared=True")

    def _get_or_create_collection(self, collection_name: str) -> Chroma:
        """
        Get existing collection from cache or create new one.

        Args:
            collection_name: Name of the collection

        Returns:
            Chroma vectorstore instance
        """
        if collection_name in self._collection_cache:
            logger.debug(f"Using cached collection: {collection_name}")
            return self._collection_cache[collection_name]

        logger.info(f"Creating new collection: {collection_name}")

        # Create new Chroma collection with persistence
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

        self._collection_cache[collection_name] = vectorstore
        return vectorstore

    async def ingest_report(
        self,
        agent_id: str,
        report_id: str,
        report_title: str,
        report_content: str,
        is_shared_knowledge: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest a research report into the vector store.

        Splits the report into chunks, generates embeddings, and stores
        with metadata for retrieval. Supports multi-tenancy via agent_id.

        Args:
            agent_id: Agent that created the report
            report_id: Unique identifier for the report
            report_title: Title of the report
            report_content: Full markdown content of the report
            is_shared_knowledge: Whether to store in shared collection
            metadata: Additional metadata to store with chunks

        Returns:
            Dict with ingestion status and details
        """
        logger.info(f"📥 Ingesting report '{report_title}' (ID: {report_id}) from agent '{agent_id}'")
        logger.info(f"   Content length: {len(report_content)} chars, Shared: {is_shared_knowledge}")

        try:
            # Split report into chunks
            chunks = self.text_splitter.split_text(report_content)
            logger.info(f"   Split into {len(chunks)} chunks")

            # Build documents with metadata
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = {
                    "agent_id": agent_id,
                    "report_id": report_id,
                    "report_title": report_title,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "source": "agent_report",
                    "is_shared_knowledge": is_shared_knowledge,
                    "ingested_at": datetime.utcnow().isoformat(),
                    **(metadata or {})
                }
                documents.append(Document(page_content=chunk, metadata=doc_metadata))

            # Get or create appropriate collection
            collection_name = self._get_collection_name(agent_id, is_shared_knowledge)
            vectorstore = self._get_or_create_collection(collection_name)

            # Add documents to collection
            doc_ids = [str(uuid4()) for _ in documents]
            vectorstore.add_documents(documents=documents, ids=doc_ids)

            # Persist changes
            vectorstore.persist()

            logger.info(f"✅ Successfully ingested {len(documents)} chunks to '{collection_name}'")

            return {
                "status": "success",
                "report_id": report_id,
                "collection": collection_name,
                "chunks_ingested": len(documents),
                "document_ids": doc_ids
            }

        except Exception as e:
            logger.error(f"❌ Error ingesting report '{report_id}': {str(e)}", exc_info=True)
            return {
                "status": "error",
                "report_id": report_id,
                "error": str(e)
            }

    async def query_agent_memory(
        self,
        agent_id: str,
        query: str,
        k: int = 4,
        access_shared_knowledge: bool = True,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Query agent's private memory and optionally shared knowledge.

        Performs semantic search across agent's private vector collection
        and shared organizational knowledge, merging and ranking results.

        Args:
            agent_id: Agent performing the query
            query: Natural language query string
            k: Number of results to retrieve per collection
            access_shared_knowledge: Whether to query shared collection
            filter_metadata: Additional metadata filters

        Returns:
            Dict with query results and context for LLM
        """
        logger.info(f"🔍 Agent '{agent_id}' querying: '{query[:100]}...'")
        logger.info(f"   Retrieving top-{k}, Shared access: {access_shared_knowledge}")

        try:
            all_results = []

            # Query agent's private memory
            private_collection_name = self._get_collection_name(agent_id, is_shared=False)
            try:
                private_vectorstore = self._get_or_create_collection(private_collection_name)
                private_docs = private_vectorstore.similarity_search_with_score(
                    query=query,
                    k=k,
                    filter=filter_metadata
                )
                all_results.extend([
                    {
                        "content": doc.page_content,
                        "metadata": doc.metadata,
                        "score": score,
                        "source": "private_memory"
                    }
                    for doc, score in private_docs
                ])
                logger.info(f"   Found {len(private_docs)} results in private memory")
            except Exception as e:
                logger.warning(f"   No private memory found for agent '{agent_id}': {e}")

            # Query shared organizational knowledge if requested
            if access_shared_knowledge:
                shared_collection_name = self._get_collection_name(None, is_shared=True)
                try:
                    shared_vectorstore = self._get_or_create_collection(shared_collection_name)
                    shared_docs = shared_vectorstore.similarity_search_with_score(
                        query=query,
                        k=k,
                        filter=filter_metadata
                    )
                    all_results.extend([
                        {
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "score": score,
                            "source": "shared_knowledge"
                        }
                        for doc, score in shared_docs
                    ])
                    logger.info(f"   Found {len(shared_docs)} results in shared knowledge")
                except Exception as e:
                    logger.warning(f"   No shared knowledge found: {e}")

            # Sort by score (lower is better for Chroma's distance metric)
            all_results.sort(key=lambda x: x["score"])

            # Deduplicate by content
            unique_results = []
            seen_content = set()
            for result in all_results:
                content_hash = hash(result["content"])
                if content_hash not in seen_content:
                    unique_results.append(result)
                    seen_content.add(content_hash)

            # Take top k unique results
            top_results = unique_results[:k]

            # Build context string for LLM
            context = "\n\n".join([
                f"[Source: {r['source']}]\n{r['content']}"
                for r in top_results
            ])

            logger.info(f"✅ Retrieved {len(top_results)} unique results for agent '{agent_id}'")

            return {
                "status": "success",
                "query": query,
                "agent_id": agent_id,
                "retrieved_documents": top_results,
                "context": context,
                "total_results": len(all_results),
                "unique_results": len(unique_results)
            }

        except Exception as e:
            logger.error(f"❌ Error querying memory for agent '{agent_id}': {str(e)}", exc_info=True)
            return {
                "status": "error",
                "query": query,
                "agent_id": agent_id,
                "error": str(e),
                "context": ""
            }

    async def delete_agent_memory(self, agent_id: str) -> Dict[str, Any]:
        """
        Delete all private memory for a specific agent.

        Args:
            agent_id: Agent whose memory should be deleted

        Returns:
            Dict with deletion status
        """
        logger.info(f"🗑️  Deleting private memory for agent '{agent_id}'")

        try:
            collection_name = self._get_collection_name(agent_id, is_shared=False)

            # Remove from cache
            if collection_name in self._collection_cache:
                del self._collection_cache[collection_name]

            # Delete collection directory
            collection_path = os.path.join(self.persist_directory, collection_name)
            if os.path.exists(collection_path):
                import shutil
                shutil.rmtree(collection_path)
                logger.info(f"✅ Deleted collection directory: {collection_path}")

            return {
                "status": "success",
                "agent_id": agent_id,
                "collection_deleted": collection_name
            }

        except Exception as e:
            logger.error(f"❌ Error deleting memory for agent '{agent_id}': {str(e)}", exc_info=True)
            return {
                "status": "error",
                "agent_id": agent_id,
                "error": str(e)
            }


# Global singleton instance
_vector_store: Optional[AgentVectorStore] = None


def get_vector_store() -> AgentVectorStore:
    """
    Get or create the global vector store instance.

    Returns:
        AgentVectorStore singleton instance
    """
    global _vector_store

    if _vector_store is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_data")
        embedding_model = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        _vector_store = AgentVectorStore(
            persist_directory=persist_dir,
            embedding_model=embedding_model
        )

    return _vector_store
