"""Dataset Manager - Storage and retrieval of research datasets and artifacts"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

class DatasetManager:
    """Manages dataset storage, retrieval, and versioning for agents"""

    def __init__(self):
        # Dataset storage locations
        self.datasets_dir = Path("/app/.agents/datasets")
        self.artifacts_dir = Path("/app/.agents/artifacts")
        self.cache_dir = Path("/app/.agents/cache")

        # Create directories if they don't exist
        for directory in [self.datasets_dir, self.artifacts_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        print(f"✅ Dataset Manager initialized")
        print(f"   Datasets: {self.datasets_dir}")
        print(f"   Artifacts: {self.artifacts_dir}")
        print(f"   Cache: {self.cache_dir}")

    def store_dataset(
        self,
        agent_id: str,
        task_id: str,
        dataset_name: str,
        data: Any,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store a dataset for future agent use

        Args:
            agent_id: Agent that created/owns this dataset
            task_id: Task that generated this dataset
            dataset_name: Name/identifier for the dataset
            data: The actual dataset (will be JSON serialized)
            metadata: Optional metadata about the dataset

        Returns:
            dataset_id: Unique identifier for the stored dataset
        """

        # Generate unique dataset ID
        timestamp = datetime.utcnow().isoformat()
        dataset_id = hashlib.md5(
            f"{agent_id}{task_id}{dataset_name}{timestamp}".encode()
        ).hexdigest()[:16]

        # Prepare dataset package
        dataset_package = {
            "dataset_id": dataset_id,
            "agent_id": agent_id,
            "task_id": task_id,
            "name": dataset_name,
            "created_at": timestamp,
            "metadata": metadata or {},
            "data": data
        }

        # Store to disk
        dataset_path = self.datasets_dir / f"{dataset_id}.json"
        with open(dataset_path, 'w') as f:
            json.dump(dataset_package, f, indent=2, default=str)

        print(f"📦 Dataset stored: {dataset_name} (ID: {dataset_id})")
        return dataset_id

    def retrieve_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Retrieve a dataset by ID"""

        dataset_path = self.datasets_dir / f"{dataset_id}.json"

        if not dataset_path.exists():
            print(f"⚠️  Dataset {dataset_id} not found")
            return None

        try:
            with open(dataset_path, 'r') as f:
                dataset = json.load(f)
                print(f"📦 Retrieved dataset: {dataset['name']}")
                return dataset
        except Exception as e:
            print(f"❌ Error loading dataset {dataset_id}: {e}")
            return None

    def list_datasets(
        self,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None
    ) -> List[Dict]:
        """
        List available datasets, optionally filtered by agent or task

        Returns list of dataset summaries (without full data)
        """

        datasets = []

        for dataset_file in self.datasets_dir.glob("*.json"):
            try:
                with open(dataset_file, 'r') as f:
                    dataset = json.load(f)

                    # Apply filters
                    if agent_id and dataset.get("agent_id") != agent_id:
                        continue
                    if task_id and dataset.get("task_id") != task_id:
                        continue

                    # Return summary without full data
                    datasets.append({
                        "dataset_id": dataset["dataset_id"],
                        "agent_id": dataset["agent_id"],
                        "task_id": dataset["task_id"],
                        "name": dataset["name"],
                        "created_at": dataset["created_at"],
                        "metadata": dataset.get("metadata", {})
                    })
            except Exception as e:
                print(f"⚠️  Error reading {dataset_file}: {e}")

        return datasets

    def store_artifact(
        self,
        agent_id: str,
        artifact_type: str,
        content: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Store a code artifact, visualization, or other agent output

        Args:
            agent_id: Agent that created this artifact
            artifact_type: Type (code, visualization, report, etc.)
            content: The actual content/code
            metadata: Optional metadata

        Returns:
            artifact_id: Unique identifier
        """

        timestamp = datetime.utcnow().isoformat()
        artifact_id = hashlib.md5(
            f"{agent_id}{artifact_type}{timestamp}".encode()
        ).hexdigest()[:16]

        artifact_package = {
            "artifact_id": artifact_id,
            "agent_id": agent_id,
            "type": artifact_type,
            "created_at": timestamp,
            "metadata": metadata or {},
            "content": content
        }

        artifact_path = self.artifacts_dir / f"{artifact_id}.json"
        with open(artifact_path, 'w') as f:
            json.dump(artifact_package, f, indent=2)

        print(f"📄 Artifact stored: {artifact_type} (ID: {artifact_id})")
        return artifact_id

    def cache_research_results(
        self,
        query: str,
        results: List[Dict],
        ttl_hours: int = 24
    ) -> None:
        """
        Cache research results to avoid duplicate searches

        Args:
            query: The search query
            results: Search results
            ttl_hours: Time to live in hours
        """

        query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
        cache_entry = {
            "query": query,
            "query_hash": query_hash,
            "results": results,
            "cached_at": datetime.utcnow().isoformat(),
            "ttl_hours": ttl_hours
        }

        cache_path = self.cache_dir / f"research_{query_hash}.json"
        with open(cache_path, 'w') as f:
            json.dump(cache_entry, f, indent=2)

    def get_cached_research(self, query: str) -> Optional[List[Dict]]:
        """Retrieve cached research results if available and not expired"""

        query_hash = hashlib.md5(query.encode()).hexdigest()[:16]
        cache_path = self.cache_dir / f"research_{query_hash}.json"

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'r') as f:
                cache_entry = json.load(f)

            # Check if expired
            cached_at = datetime.fromisoformat(cache_entry["cached_at"])
            ttl_hours = cache_entry.get("ttl_hours", 24)
            age_hours = (datetime.utcnow() - cached_at).total_seconds() / 3600

            if age_hours > ttl_hours:
                print(f"🗑️  Cache expired for query: {query[:50]}...")
                return None

            print(f"⚡ Cache hit for query: {query[:50]}...")
            return cache_entry["results"]

        except Exception as e:
            print(f"⚠️  Cache read error: {e}")
            return None

    def get_agent_datasets_summary(self, agent_id: str) -> Dict:
        """Get a summary of all datasets for an agent"""

        datasets = self.list_datasets(agent_id=agent_id)

        return {
            "agent_id": agent_id,
            "total_datasets": len(datasets),
            "datasets": datasets,
            "storage_location": str(self.datasets_dir)
        }

# Global instance
dataset_manager = DatasetManager()
