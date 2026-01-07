import numpy as np
from typing import Any, Dict, List

from kimera.store.Store import Store

class VectorRepo:
    def __init__(self,store: Store,collection):
        self.use_store = store
        self.collection = self.use_store.use(collection)

    def save(self,data,vector):
        self.collection.insert_one({"text":data,"vector":vector.tolist()})

    def load(self):
        return self.collection.find({}, {"_id": 0, "text": 1, "vector": 1})

    def clear(self):
        self.collection.delete_many({})

    def drop(self):
        self.collection.drop()



class VectorStore:
    def     __init__(self, store, collection_name, **kwargs):
        """
        Backend-agnostic vector store. Only manages persistence via VectorRepo and carries
        configuration kwargs for higher-level embedding handlers. No embedder initialization
        or vectorization is performed here.

        Known kwargs (optional and not enforced here):
        - embedder: backend identifier (e.g., 'faiss', 'openai', 'pinecone')
        - model: model identifier meaningful to the chosen embedder
        - api_key: backend API key if applicable
        - dimension: embedding dimension if known
        Any other kwargs are preserved and available via getters.
        """

        # Persistence repo
        self.repo = VectorRepo(store=store, collection=collection_name)

        # Store raw kwargs privately
        self._kwargs: Dict[str, Any] = kwargs or {}
        self._embedder: str | None = self._kwargs.get("embedder")
        self._model: str | None = self._kwargs.get("model")
        dim_val = self._kwargs.get("dimension")
        try:
            self._dimension: int | None = int(dim_val) if dim_val is not None else None
        except (TypeError, ValueError):
            self._dimension = None
        

    # === Public API ===
    def add_vector(self, text: str, vector: np.ndarray | List[float]):
        """
        Persist a precomputed vector for the given text. The caller is responsible for
        producing the embedding vector using the desired backend.
        """
        if isinstance(vector, np.ndarray):
            if vector.ndim == 1:
                vector = vector.reshape(1, -1)
        self.repo.save(text, vector)

    def load(self):
        """Return an iterator of stored documents with text and vector."""
        return self.repo.load()

    def clear(self):
        self.repo.clear()

    def drop(self):
        self.repo.drop()

    def clone_store(self, target_name: str, copy_indexes: bool = True):
        """
        Clone this collection into another collection with name `target_name`.

        Args:
            target_name (str): Name of the new target collection.
            copy_indexes (bool): Whether to also duplicate indexes (default False).
        Returns:
            VectorStore: a new VectorStore instance bound to the target collection.
        """
        src = self.repo.collection
        db = src.database

        # Server-side copy of all documents
        src.aggregate([{"$match": {}}, {"$out": target_name}])

        if copy_indexes:
            indexes = src.index_information()
            dst = db[target_name]
            for name, spec in indexes.items():
                if name == "_id_":
                    continue  # skip default index
                dst.create_index(spec["key"],
                                 **{k: v for k, v in spec.items() if k not in {"key"}})

        return VectorStore(store=self.repo.use_store, collection_name=target_name, **self._kwargs)

    # === Getters for private config ===
    @property
    def embedder(self) -> str | None:
        return self._embedder

    @property
    def model(self) -> str | None:
        return self._model

    @property
    def dimension(self) -> int | None:
        return self._dimension

    @property
    def kwargs(self) -> Dict[str, Any]:
        return dict(self._kwargs)


