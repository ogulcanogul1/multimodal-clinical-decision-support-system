from langchain_core.prompts import ChatPromptTemplate
from src.graph.state import GraphState
from src.schemas.node_schemas.rag_schemas import Grade  
from src.schemas.chunk import Chunk
from src.graph.model.model_abstraction import ActiveLLMFactory 
from src import logger

def retrieval_grader_service(state: GraphState):
    """
    Dökümanları sırayla değerlendirir. 
    Eğer geçerli döküman yoksa sayacı artırır. Maksimum denemeye ulaşılırsa 
    literatür taramasını sonlandırıp elindeki boş listeyle Başhekime (Diagnostic Agent) geçer.
    """
    print('*' * 50)
    retry_count = state.get("retrieval_retry_count", 0)
    MAX_RETRIES = 2 # Toplam 3 deneme hakkı (0, 1, 2)
    
    logger.info(f"--- ⚖️ RETRIEVAL GRADER STARTING (Deneme: {retry_count + 1}/{MAX_RETRIES + 1}) ---")
    
    # 1. ARAMANIN ASIL AMACINI ÇEK (Kör Notlandırmayı Engelliyoruz)
    user_query = state.get("message_content") or state.get("query")
    opt_queries = state.get("optimized_queries", {})
    # Optimizer'ın ürettiği zenginleştirilmiş sorguyu kullanıyoruz
    clinical_query = opt_queries.get("vector_store_query", user_query)
    
    # 2. ÖNCEKİ DÜĞÜMDEN GELEN LİSTEYİ AL
    docs = state.get("knowledge_retrieved_docs", [])
    
    # SONSUZ DÖNGÜ KORUMASI (Fail-Safe)
    if retry_count >= MAX_RETRIES:
        # MİMARİ DÜZELTME: Artık Fusion'a değil Diagnostic Agent'a gidiyor!
        logger.warning(f"🚨 Maksimum RAG deneme sayısına ({MAX_RETRIES+1}) ulaşıldı. Geçerli döküman bulunamadı. RAG pas geçilerek Diagnostic Agent'a ilerleniyor.")
        return {
            "final_retrieved_docs": []
        }

    if not docs:
        logger.warning("Değerlendirilecek döküman yok. RAG döngüsüne (Retry) dönülüyor...")
        return {"retrieval_retry_count": retry_count + 1}

    # Factory zaten structured_output gömülü model dönüyor
    llm = ActiveLLMFactory.retrieval_grader_llm() 
    
    # 3. PROMPT GÜNCELLEMESİ (Clinical Query kullanılıyor)
    system_prompt = """You are a highly strict medical quality grader. 
    Assess whether the following retrieved document is clinically relevant to the patient's condition and the query.
    
    If the document contains information that can help answer the query or address the clinical condition, score 'yes'.
    Otherwise, score 'no'.
    
    Clinical Context & Query: 
    {clinical_query}
    
    Document Content:
    {context}
    """
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm 

    relevant_docs = []

    # Normal for döngüsü ile tek tek dökümanları değerlendir
    for doc in docs:
        try:
            # Sadece clinical_query ve context yolluyoruz
            res: Grade = chain.invoke({"clinical_query": clinical_query, "context": doc.content})
            
            if res.binary_score.lower() == "yes":
                relevant_docs.append(doc)
        except Exception as e:
            # Güvenli loglama
            citation = doc.metadata.citation_id if hasattr(doc, 'metadata') and hasattr(doc.metadata, 'citation_id') else 'Unknown'
            logger.error(f"Error grading doc {citation}: {e}")

    if len(relevant_docs) > 0:
        logger.info(f"✅ {len(relevant_docs)} documents passed the grade. Proceeding to Diagnostic Agent.")
        return {
            # 4. ASIL TEMİZ LİSTEYİ OLUŞTURUYORUZ (Başhekim buna bakacak)
            "final_retrieved_docs": relevant_docs
        }
    else:
        logger.warning(f"❌ Hiçbir döküman testi geçemedi. Sayaç {retry_count + 1} yapıldı ve Retry tetikleniyor.")
        return {
            "retrieval_retry_count": retry_count + 1
        }