from typing import Literal, Optional, List
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


# Alt Şema: Tek bir tahlil satırını (Örn: Sadece WBC) temsil eder
class LabParameter(BaseModel):
    """Tek bir laboratuvar test parametresinin detayları."""
    name: str = Field(description="Parametrenin kısa adı veya kodu (Örn: WBC, GLU, HGB, PLT)")
    value: float = Field(description="Hastanın tahlil sonucu (sayısal değer)")
    unit: Optional[str] = Field(None, description="Ölçüm birimi (Örn: mg/dL, 10^3/uL, g/dL)")
    ref_min: Optional[float] = Field(None, description="Hastanenin belirlediği referans aralığının ALT sınırı")
    ref_max: Optional[float] = Field(None, description="Hastanenin belirlediği referans aralığının ÜST sınırı")
    flag: Optional[str] = Field(None, description="Eğer sonuç normalin altındaysa 'L' (Low), üstündeyse 'H' (High), normalse 'N' veya boş bırak.")

# Üst Şema: Bütün tahlil kağıdını/PDF'ini temsil eder
class LabReport(BaseModel):
    """Tüm laboratuvar raporunun yapılandırılmış hali."""
    is_valid_report: bool = Field(description="Bu metin veya görsel gerçekten tıbbi bir kan/idrar tahlili raporu mu?")
    patient_age: Optional[int] = Field(None, description="Raporda yazıyorsa hastanın yaşı, yoksa null.")
    patient_gender: Optional[str] = Field(None, description="Raporda yazıyorsa hastanın cinsiyeti ('M' veya 'F'), yoksa null.")
    parameters: List[LabParameter] = Field(
        default_factory=list, 
        description="Rapordan başarıyla çıkarılan tüm tahlil parametrelerinin listesi."
    )