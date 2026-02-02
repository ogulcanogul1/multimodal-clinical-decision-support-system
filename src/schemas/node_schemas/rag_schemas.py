from pydantic import BaseModel, Field
from typing import List

class OptimizedQueries(BaseModel):
    vector_store_query: str = Field(description="Medical terminology enriched query for local vector database search.")
    web_search_queries: List[str] = Field(description="3 distinct search queries for web research, covering symptoms and clinical guidelines.")
    rationale: str = Field(description="Brief explanation of why these terms were chosen.")

class Grade(BaseModel):
    binary_score: str = Field(description="Döküman sorguyla alakalı mı? 'yes' veya 'no'")