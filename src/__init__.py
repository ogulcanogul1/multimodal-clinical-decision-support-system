import logging
import os
from datetime import datetime

# Logs dizinini kontrol et ve oluştur
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Log dosyası ismi (Her gün için ayrı dosya veya tek bir system.log)
log_filename = f"system_{datetime.now().strftime('%Y-%m-%d')}.log"
log_filepath = os.path.join(LOG_DIR, log_filename)

# Logger'ı oluştur
logger = logging.getLogger("MedicalRAG")
logger.setLevel(logging.DEBUG)

# Formatlayıcı: Zaman - Log Seviyesi - Dosya/Satır - Mesaj
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# Dosyaya Yazma İşlemi (FileHandler)
file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Konsola Yazma İşlemi (StreamHandler)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)


logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("Sistem başlatıldı. Loglama mekanizması aktif.")