from langchain_core.prompts import ChatPromptTemplate
from src.graph.model.model_abstraction import ActiveLLMFactory
from src.graph.state import GraphState
from src.schemas.node_schemas.rag_schemas import OptimizedQueries
from src import logger
import json

def query_optimizer_service(state: GraphState):
    print('*' * 50)
    logger.info("--- 🔍 QUERY OPTIMIZER STARTING ---")
    
    # 1. State'ten Yeni Gelen Tüm Zengin Verileri Çekiyoruz
    user_query = state.get("message_content") or state.get("query") or "Analyze patient findings."
    fused_context = state.get("fused_clinical_context", {})
    chat_history = state.get("chat_history", [])
    
    # 2. Sohbet Geçmişini Formatla
    history_text = ""
    if chat_history:
        history_text = "PREVIOUS CONVERSATION HISTORY:\n"
        for msg in chat_history[-4:]: 
            role_name = "DOCTOR" if msg.get("role") in ["DOCTOR", "user"] else "AI ASSISTANT"
            history_text += f"[{role_name}]: {msg.get('content')}\n"

    # 3. Klinik Bağlamı JSON Formatına Çevir
    context_str = json.dumps(fused_context, indent=2, ensure_ascii=False)

    # Factory zaten structured_output gömülü model dönüyor
    llm = ActiveLLMFactory.query_optimizer_llm()
    
    # 4. SİSTEM PROMPTU
    system_prompt_content = """You are an Expert Medical Query Transformer. Your ONLY mission is to convert the User Input into a dual-search strategy for a Clinical Decision Support System. 

    You are provided with the patient's "CLINICAL CONTEXT" (demographics, laboratory/radiological anomalies) and "CONVERSATION HISTORY". 
    
    ### TRANSFORMATION OBJECTIVE:
    1. **vector_store_query**: Create ONE high-density clinical query using medical terminology for local clinical RAG retrieval.
    2. **web_search_queries**: Create EXACTLY THREE distinct queries for internet search focusing on 2025-2026 clinical guidelines, latest trials, and pharmaceutical/technology updates.

    ### CRITICAL RULES:
    - ALWAYS ENRICH the user's input with the anomalies found in the CLINICAL CONTEXT. 
      (e.g., If user says "What is the treatment?", and context shows "High Glucose and Pneumonia", your search must be about treating pneumonia in diabetic patients).
    - If the user's query is unrelated to the anomalies (e.g., "What is the capital of France?"), focus on the medical context anyway or return generic medical searches.
    - All output must be in professional medical English.
    - Return ONLY a valid JSON object matching the schema. No conversational text.
    - Prefer 2025–2026 guidelines.
    - Each web_search_query must be <= 15 words.

    {format_instructions}

    ### DATA INPUTS:
    
    CLINICAL CONTEXT (Anomalies & Patient Profile):
    {context_str}

    {history_text}
    
    USER INPUT (Doctor's Query):
    "{query}"
    """

    prompt = ChatPromptTemplate.from_template(system_prompt_content)
    
    # DÜZELTME: Factory hallettiği için sadece prompt ile llm'i bağlıyoruz
    chain = prompt | llm

    schema_dict = OptimizedQueries.model_json_schema()
    format_instructions = json.dumps(schema_dict, indent=2)
    
    try:
        # Zinciri çalıştır (Factory structured_output sağladığı için dönüş direkt Pydantic objesi olacak)
        optimized_data: OptimizedQueries = chain.invoke({
            "context_str": context_str,
            "history_text": history_text,
            "query": user_query,
            "format_instructions": format_instructions
        })
        
        logger.info("✅ Optimization successful. Context-aware queries generated.")
        
        print(f"""
vector_store_query : {optimized_data.vector_store_query}
web_search_queries : {optimized_data.web_search_queries}
""")

        return {
            "optimized_queries": {
                "vector_store_query": optimized_data.vector_store_query,
                "web_search_queries": optimized_data.web_search_queries
            }
        }
    except Exception as e:
        logger.error(f"❌ Query Optimization failed: {str(e)}")
        # Hata durumunda sistemin çökmemesi için güvenli (default) bir arama terimi dönüyoruz
        return {
            "optimized_queries": {
                "vector_store_query": "clinical guidelines and diagnosis protocols",
                "web_search_queries": ["2026 medical guidelines", "recent clinical trials 2025", "standard of care medical protocols"]
            }
        }