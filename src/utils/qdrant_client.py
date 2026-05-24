import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QdrantManager:
    def __init__(self):
        self.host = os.getenv("QDRANT_HOST", "localhost")
        self.port = int(os.getenv("QDRANT_PORT", "6333"))
        self.api_key = os.getenv("QDRANT_API_KEY")
        self.client = None
        self._connect()

    def _connect(self):
        try:
            self.client = QdrantClient(
                host=self.host,
                port=self.port,
                api_key=self.api_key if self.api_key else None
            )
            logger.info(f"Connected to Qdrant at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            raise

    def create_collection(
        self,
        collection_name: str,
        vector_size: int = 128,
        distance: Distance = Distance.COSINE
    ):
        try:
            collections = self.client.get_collections().collections
            existing_names = [c.name for c in collections]
            
            if collection_name in existing_names:
                logger.info(f"Collection {collection_name} already exists")
                return
            
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            logger.info(f"Created collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise

    def insert_points(
        self,
        collection_name: str,
        points: List[PointStruct]
    ):
        try:
            self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            logger.info(f"Inserted {len(points)} points into {collection_name}")
        except Exception as e:
            logger.error(f"Failed to insert points: {e}")
            raise

    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        try:
            search_result = self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = []
            for hit in search_result:
                results.append({
                    "id": hit.id,
                    "score": hit.score,
                    "payload": hit.payload
                })
            
            return results
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            raise

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        try:
            info = self.client.get_collection(collection_name)
            return {
                "name": collection_name,
                "points_count": info.points_count,
                "vector_size": info.config.params.vectors.size
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise
