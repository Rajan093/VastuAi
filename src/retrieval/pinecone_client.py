import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec


class PineconeClient:

    
    def __init__(
        self, 
        api_key: str = None,
        index_name: str = None
    ):
        load_dotenv()
        
        self.api_key = api_key or os.getenv('PINECONE_API_KEY')
        self.index_name = index_name or os.getenv('PINECONE_INDEX_NAME', 'lal-kitab-rules')
        
        if not self.api_key:
            raise ValueError(
                "Pinecone API key not found. "
                "Set PINECONE_API_KEY in .env or pass as argument."
            )
        
        self.pc = Pinecone(api_key=self.api_key)
        self.index = None
    
    def create_index(
        self, 
        dimension: int = 768,
        metric: str = 'cosine',
        cloud: str = 'aws',
        region: str = 'us-east-1'
    ) -> None:
        """
        Create a new Pinecone serverless index.
        """
        existing_indexes = self.pc.list_indexes()
        
        if self.index_name in [idx.name for idx in existing_indexes]:
            print(f"   ℹ️  Index '{self.index_name}' already exists")
            self.index = self.pc.Index(self.index_name)
            return
        
        print(f"   Creating index '{self.index_name}'...")
        
        self.pc.create_index(
            name=self.index_name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )
        
        print(f"   ✓ Index '{self.index_name}' created successfully")
        self.index = self.pc.Index(self.index_name)
    
    def connect_to_index(self) -> None:

        try:
            self.index = self.pc.Index(self.index_name)
            stats = self.index.describe_index_stats()
            print(f"   ✓ Connected to index '{self.index_name}'")
            print(f"   Total vectors: {stats.total_vector_count}")
        except Exception as e:
            raise RuntimeError(
                f"Failed to connect to index '{self.index_name}': {str(e)}"
            )
    
    def upsert_chunks(
        self, 
        chunks: List[Dict[str, any]],
        batch_size: int = 100,
        show_progress: bool = True
    ) -> Dict[str, int]:
        
        if not self.index:
            raise RuntimeError("Not connected to any index. Call create_index() or connect_to_index() first.")
        
        if show_progress:
            print(f"\n📤 Uploading {len(chunks)} vectors to Pinecone...")
        
        vectors = []
        for i, chunk in enumerate(chunks):
            vector_id = f"{chunk['planet'].lower()}_house_{chunk['house']}"
            
            vector = {
                'id': vector_id,
                'values': chunk['embedding'],
                'metadata': {
                    'planet': chunk['planet'],
                    'house': chunk['house'],
                    'heading': chunk['heading'],
                    'content': chunk['content'],
                    'char_count': chunk['char_count']
                }
            }
            vectors.append(vector)
        
        total_uploaded = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            total_uploaded += len(batch)
            
            if show_progress:
                print(f"   Uploaded: {total_uploaded}/{len(vectors)}")
        
        if show_progress:
            print(f"   ✓ Successfully uploaded {total_uploaded} vectors")
        
        return {
            'total_uploaded': total_uploaded,
            'index_name': self.index_name
        }
    
    def get_index_stats(self) -> Dict:
        """Get statistics about the current index."""
        if not self.index:
            raise RuntimeError("Not connected to any index.")
        
        stats = self.index.describe_index_stats()
        return {
            'total_vectors': stats.total_vector_count,
            'dimension': stats.dimension,
            'index_name': self.index_name
        }
    
    def query_by_chart(
        self,
        chart: Dict[str, int],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Query Pinecone for rules matching the chart's planet-house combinations.
        
        """
        if not self.index:
            raise RuntimeError("Not connected to any index.")
        
        all_results = []
        
        for planet, house in chart.items():
            filter_dict = {
                "$and": [
                    {"planet": {"$eq": planet}},
                    {"house": {"$eq": house}}
                ]
            }
            
            try:
                query_result = self.index.query(
                    vector=[0.0] * 768,
                    filter=filter_dict,
                    top_k=top_k,
                    include_metadata=True
                )
                
                if query_result.matches:
                    for match in query_result.matches:
                        result = {
                            'planet': planet,
                            'house': house,
                            'id': match.id,
                            'score': match.score,
                            'content': match.metadata.get('content', ''),
                            'heading': match.metadata.get('heading', ''),
                            'metadata': match.metadata
                        }
                        all_results.append(result)
                        
            except Exception as e:
                print(f"Warning: Could not retrieve {planet} in House {house}: {e}")
                continue
        print("pinrcone_client.py: query_by_chart")
        print(all_results)
        return all_results
    
    def query_by_chart_and_question(
        self,
        chart: Dict[str, int],
        question_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict]:
        """
        Hybrid query: Combines metadata filtering with similarity search.
        """
        if not self.index:
            raise RuntimeError("Not connected to any index.")
        
        and_filters = []
        for planet, house in chart.items():
            and_filter = {
                "$and": [
                    {"planet": {"$eq": planet}},
                    {"house": {"$eq": house}}
                ]
            }
            and_filters.append(and_filter)
        
        metadata_filter = {"$or": and_filters}
        
        query_result = self.index.query(
            vector=question_embedding,
            filter=metadata_filter,
            top_k=top_k,
            include_metadata=True
        )
        
        results = []
        if query_result.matches:
            for match in query_result.matches:
                result = {
                    'planet': match.metadata.get('planet'),
                    'house': match.metadata.get('house'),
                    'id': match.id,
                    'score': match.score,
                    'content': match.metadata.get('content', ''),
                    'heading': match.metadata.get('heading', ''),
                    'metadata': match.metadata
                }
                results.append(result)
        
        return results
    
    def delete_all_vectors(self) -> None:

        if not self.index:
            raise RuntimeError("Not connected to any index.")
        
        print(f"   ⚠️  Deleting all vectors from '{self.index_name}'...")
        self.index.delete(delete_all=True)
        print(f"   ✓ All vectors deleted")
