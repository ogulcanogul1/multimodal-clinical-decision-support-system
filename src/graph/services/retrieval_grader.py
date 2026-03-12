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
    literatür taramasını sonlandırıp elindeki boş listeyle Fusion'a geçer.
    """
    retry_count = state.get("retrieval_retry_count", 0)
    MAX_RETRIES = 2 # Toplam 3 deneme hakkı (0, 1, 2)
    
    logger.info(f"--- ⚖️ RETRIEVAL GRADER STARTING (Deneme: {retry_count + 1}/{MAX_RETRIES + 1}) ---")
    
    query = state.get("query")
    docs = state.get("retrieved_docs", [])
    
    # SONSUZ DÖNGÜ KORUMASI (Fail-Safe)
    if retry_count >= MAX_RETRIES:
        logger.warning(f"🚨 Maksimum RAG deneme sayısına ({MAX_RETRIES+1}) ulaşıldı. Geçerli döküman bulunamadı. RAG pas geçilerek Adaptive Fusion'a ilerleniyor.")
        return {
            "final_retrieved_docs": []
        }

    if not docs:
        logger.warning("Değerlendirilecek döküman yok. RAG döngüsüne (Retry) dönülüyor...")
        return {"retrieval_retry_count": retry_count + 1}

    llm = ActiveLLMFactory.retrieval_grader_llm() 
    
    system_prompt = """You are a highly strict medical quality grader. 
    Assess whether the following retrieved document is clinically relevant to the user query.
    If the document contains information that can help answer the query, score 'yes'.
    Otherwise, score 'no'.
    
    User Query: {query}
    Document: {context}
    
    Output ONLY JSON: {{"binary_score": "yes" or "no"}}
    """
    prompt = ChatPromptTemplate.from_template(system_prompt)
    chain = prompt | llm 

    relevant_docs = []

    # Normal for döngüsü ile tek tek dökümanları değerlendir
    for doc in docs:
        try:
            # ainvoke yerine invoke kullanıyoruz
            res: Grade = chain.invoke({"query": query, "context": doc.content})
            
            if res.binary_score.lower() == "yes":
                relevant_docs.append(doc)
        except Exception as e:
            citation = doc.metadata.citation_id if hasattr(doc, 'metadata') else 'Unknown'
            logger.error(f"Error grading doc {citation}: {e}")

    if len(relevant_docs) > 0:
        logger.info(f"✅ {len(relevant_docs)} documents passed the grade. Proceeding to Adaptive Fusion.")
        return {
            "final_retrieved_docs": relevant_docs
        }
    else:
        logger.warning(f"❌ Hiçbir döküman testi geçemedi. Sayaç {retry_count + 1} yapıldı ve Retry tetikleniyor.")
        return {
            "retrieval_retry_count": retry_count + 1
        }