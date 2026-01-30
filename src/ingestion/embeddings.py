import os
from typing import List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import types


class EmbeddingsGenerator:
    
    # Gemini embedding model (768 dimensions)
    MODEL_NAME = "text-embedding-004"
    EMBEDDING_DIMENSION = 768
    
    def __init__(self, api_key: str = None):
        load_dotenv()
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. "
                "Set GEMINI_API_KEY in .env or pass as argument."
            )
        
        self.client = genai.Client(api_key=self.api_key)
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector (768 dimensions)
        """
        try:
            result = self.client.models.embed_content(
                model=self.MODEL_NAME,
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(
        self, 
        texts: List[str],
        show_progress: bool = True
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            show_progress: Whether to print progress
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        total = len(texts)
        
        for i, text in enumerate(texts, 1):
            if show_progress and i % 5 == 0:
                print(f"   Generating embeddings: {i}/{total}")
            
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        
        if show_progress:
            print(f"   ✓ Generated {total} embeddings")
        
        return embeddings
    
    def embed_chunks(
        self, 
        chunks: List[Dict[str, any]],
        show_progress: bool = True
    ) -> List[Dict[str, any]]:
        """
        Generate embeddings for chunks and attach to metadata.
        
        Args:
            chunks: List of chunk dictionaries from chunker
            show_progress: Whether to print progress
            
        Returns:
            List of chunks with 'embedding' field added
        """
        if show_progress:
            print(f"\n🔮 Generating embeddings for {len(chunks)} chunks...")
        
        texts = [chunk['content'] for chunk in chunks]
        embeddings = self.generate_embeddings_batch(texts, show_progress)
        
        embedded_chunks = []
        for chunk, embedding in zip(chunks, embeddings):
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding['embedding'] = embedding
            embedded_chunks.append(chunk_with_embedding)
        
        return embedded_chunks

