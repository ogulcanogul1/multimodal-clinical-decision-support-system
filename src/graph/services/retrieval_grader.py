from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src import logger
from src.schemas.node_schemas.rag_schemas import Grade

import asyncio
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.graph.state import GraphState
from src.graph.enum.system_status import SystemStatus
from src.schemas.node_schemas.rag_schemas import Grade  
from src.schemas.chunk import Chunk
from src.graph.model.llm_factory_ollama import OllamaLLMFactory
from src import logger

async def retrieval_grader_service(state: GraphState):
    """
    Dökümanları paralel (async) olarak kontrol eder.
    Alakasızları eler, hiç kalmazsa state'i sıfırlayıp FAIL döner.
    """
    logger.info("--- ASYNC RETRIEVAL GRADER STARTING ---")
    
    query = state.get("query")
    docs = state.get("retrieved_docs", [])
    
    if not docs:
        logger.warning("No documents found to grade.")
        return {"status": SystemStatus.FAILED, "retrieved_docs": []}

    llm = OllamaLLMFactory.grader_llm() 
    parser = JsonOutputParser(pydantic_object=Grade)
    
    system_prompt = """You are a medical quality grader. 
    Assess whether the following retrieved document is relevant to the user query.
    If the document contains information that can help answer the query, score 'yes'.
    Otherwise, score 'no'.
    
    User Query: {query}
    Document: {context}
    
    Output ONLY JSON: {{"binary_score": "yes" or "no"}}
    """
    prompt = ChatPromptTemplate.from_template(system_prompt)

    async def grade_single_doc(doc: Chunk) -> Chunk:
        try:
            chain = prompt | llm | parser
           
            res:Grade = await chain.ainvoke({"query": query, "context": doc.content})
            if res.binary_score.lower() == "yes":
                return doc
            return None
        except Exception as e:
            logger.error(f"Error grading doc {doc.metadata.get('citation_id')}: {e}")
            return None

    tasks = [grade_single_doc(doc) for doc in docs]
    results = await asyncio.gather(*tasks)
    relevant_docs = [doc for doc in results if doc is not None]

    if len(relevant_docs) > 0:
        logger.info(f"{len(relevant_docs)} documents passed the grade.")
        # DÜZELTME: operator.add tuzağına düşmemek için temizlenmiş listeyi YENİ bir değişkene yazıyoruz.
        return {"final_retrieved_docs": relevant_docs}
    else:
        logger.warning("No relevant documents found. Resetting and Retrying.")
        # DÜZELTME: .value eklendi
        return {"final_retrieved_docs": [], "status": SystemStatus.FAILED.value}