from src.core.handler import global_exception_handler
from src.core.exceptions import RAGServiceError

@global_exception_handler
def test_func():
    # Artık parantez içi boş olsa bile (yukarıdaki default değer sayesinde) çalışır
    # Ve dekoratör bunu yakalayıp loga yazar.
    raise RAGServiceError("RAG servisi yanıt vermiyor!")

if __name__ == "__main__":
    test_func()
