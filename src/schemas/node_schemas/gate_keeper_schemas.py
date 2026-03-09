from typing import Literal
from pydantic import BaseModel, Field

class ImageAnalysis(BaseModel):
    """Görüntünün tıbbi türünü ve kalitesini belirleyen kesin şema."""
    
    modality: Literal["BRAIN", "LUNG", "EYE", "OTHER"] = Field(
        description="Görüntünün tıbbi kategorisi. Beyin MR için BRAIN, Akciğer Röntgeni için LUNG, Göz Fundus için EYE, aksi halde OTHER."
    )
    is_high_quality: bool = Field(
        description="Görüntü analiz edilebilir netlikte mi? Evet ise True, bulanık veya bozuk ise False."
    )
    brief_description: str = Field(
        description="Görüntüdeki ana görsel bulgunun 1 cümlelik teknik açıklaması."
    )