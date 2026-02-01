from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union

class Document(BaseModel):
    """Sadece dosyanın ham halini temsil eder"""
    page_content: str = Field(..., description="Dosyanın tüm içeriği")
    source: str = Field(..., description="Dosya adı (makale.txt vb.)")
    file_type: str = Field(..., description="txt, pdf, image")
    document_size:int = Field(...,description="dökümanın karakter sayısı")
    