from typing import List
from src.schemas.document import Document
from src.schemas.chunk import Chunk, ChunkMetadata
from src.core.config import Config
from src.preprocess.base_splitter import BaseSplitter

class FixedSizeSplitter(BaseSplitter):
    def __init__(self):
        self.chunk_size = Config.CHUNK_SIZE
        self.overlap = Config.CHUNK_OVERLAP
    
    def split_documents(self, docs: List[Document]) -> List[Chunk]:
        all_chunks: List[Chunk] = []
        
        for doc in docs:
            content = doc.page_content
            content_len = len(content)
            start_index = 0
            
            while start_index < content_len:
                
                end_index = start_index + self.chunk_size
                
                if end_index >= content_len:
                    end_index = content_len
                else:
                    
                    last_space = content.rfind(' ', start_index, end_index)
                    
                    
                    if last_space != -1 and last_space > start_index:
                        end_index = last_space
                
                chunk_page_content = content[start_index:end_index].strip()
                
                if chunk_page_content:  
                    chunk_metadata = ChunkMetadata(
                        source=doc.source,
                        file_type=doc.file_type,
                        start_index=start_index,
                        end_index=end_index,
                        total_doc_size=doc.document_size
                    )
                    
                    chunk = Chunk(
                        content=chunk_page_content,
                        metadata=chunk_metadata
                    )
                    all_chunks.append(chunk)
                
                
                next_start = end_index - self.overlap
                
                
                if end_index == content_len:
                    break
                
                
                if next_start <= start_index:
                    start_index = end_index 
                else:
                    
                    actual_next_start = content.find(' ', next_start)
                    if actual_next_start != -1 and actual_next_start < end_index:
                        start_index = actual_next_start + 1 
                    else:
                        start_index = next_start
                        
        return all_chunks