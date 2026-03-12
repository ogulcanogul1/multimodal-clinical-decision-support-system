from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from src.graph.model.model_abstraction import ActiveLLMFactory
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src.schemas.node_schemas.rag_schemas import OptimizedQueries
from src import logger
import json

def query_optimizer_service(state: GraphState):
    logger.info("--- 🔍 QUERY OPTIMIZER STARTING ---")
    
    user_query = state.get("query")
    llm = ActiveLLMFactory.query_optimizer_llm()
    
    system_prompt_content = """You are a Medical Query Transformer. Your ONLY mission is to convert the User Input into a dual-search strategy. You do not answer questions; you only generate search keys.

    ### TRANSFORMATION OBJECTIVE:
    1. **vector_store_query**: Create ONE high-density clinical query using medical terminology for local clinical RAG retrieval.
    2. **web_search_queries**: Create EXACTLY THREE distinct queries for internet search focusing on 2025-2026 clinical guidelines, latest trials, and pharmaceutical/technology updates.

    ### RULES:
    - All output must be in professional medical English.
    - Do not provide medical advice.
    - Do not include conversational text.
    - Return ONLY a valid JSON object.
    - JSON must contain exactly these keys: "vector_store_query", "web_search_queries", "rationale". No additional keys.
    - web_search_queries must contain exactly 3 strings.
    - Prefer 2025–2026. If results are limited, broaden to 2024–2026, then 2020–2026, and finally to the most recent available years.
    - Do NOT output ICD-10 codes or SNOMED concept IDs (terminology only).
    - Do not invent age, gender, duration, lab values, or diagnoses not implied by the input.
    - Each web_search_query must be <= 12 words.

    {format_instructions}

    ### EXAMPLES:

    Example 1:
    User Input: "My child has a whistling sound when breathing at night."
    Output: {{
    "vector_store_query": "Pediatric nocturnal wheezing and cough; differential diagnosis of asthma vs bronchiolitis; airway hyperresponsiveness pathophysiology; consider red flags and diagnostic workup.",
    "web_search_queries": [
        "GINA 2026 pediatric asthma guideline diagnosis management",
        "nocturnal wheezing in children diagnostic workup 2025",
        "new pediatric inhaled bronchodilators approvals 2025 2026"
    ],
    "rationale": "Mapped lay description 'whistling breathing' to clinical term 'wheezing' for targeted retrieval."
    }}

    The User Input can be in any language. Always translate and normalize it into professional medical English. Output must contain only English text inside the JSON values.

    Example 2:
    User Input: "Şiddetli karın ağrısı ve gözlerde sararma var."
    Output: {{
    "vector_store_query": "Acute abdominal pain with icterus: obstructive jaundice differential diagnosis including choledocholithiasis, cholangitis, and pancreatic head mass; biliary anatomy and imaging workup.",
    "web_search_queries": [
        "2026 guideline obstructive jaundice evaluation management",
        "acute biliary obstruction imaging protocol 2025",
        "pancreatic cancer early detection advances 2025 2026"
    ],
    "rationale": "Mapped 'yellow eyes' to 'icterus' and focused on biliary obstruction differentials."
    }}

    

    ### TASK:
    Transform this User Input: "{query}"
    """

    prompt = ChatPromptTemplate.from_template(system_prompt_content)
    chain = prompt | llm 

    schema_dict = OptimizedQueries.model_json_schema()
    format_instructions = json.dumps(schema_dict, indent=2)
    # Zinciri çalıştır
    optimized_data:OptimizedQueries = chain.invoke({
        "query": user_query,
        "format_instructions": format_instructions
    })

    logger.info("✅ Optimization successful. Queries generated.")

    return {
        "optimized_queries": {
            "vector_store_query": optimized_data.vector_store_query,
            "web_search_queries": optimized_data.web_search_queries
        }
    }