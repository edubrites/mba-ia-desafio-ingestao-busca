import os
import sys
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def format_docs(documents):
    """Format retrieved documents into context string"""
    return "\n\n".join(doc.page_content for doc in documents)

def search_prompt(question=None):
    """
    Create RAG chain for question answering.
    - If `question` is provided: returns the answer string.
    - If `question` is None: returns the chain ready to be invoked later.
    """
    try:
        # Use helpers that already validate env vars

        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        if not embeddings:
            print("❌ Erro ao inicializar embeddings.")
            sys.exit(1)

        collection_name = os.getenv("PG_VECTOR_COLLECTION_NAME", "gemini_collection")
        database_url = os.getenv("DATABASE_URL")

        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=database_url
        )

        if not vector_store:
            print("❌ Erro ao conectar ao banco de dados vetorial.")
            sys.exit(1)

        llm = ChatOpenAI(
            model="gpt-5-nano",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0
        )

        if not llm:
            print("❌ Erro ao inicializar modelo de linguagem.")
            sys.exit(1)

        # Proper retriever that can be composed in a Runnable chain
        retriever = vector_store.as_retriever(search_kwargs={"k": 10})

        # Prompt template
        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

        # Pipeline: retriever -> format -> prompt -> llm -> string
        chain = (
            {
                "contexto": retriever | format_docs,
                "pergunta": RunnablePassthrough(),
            }
            | prompt | llm | StrOutputParser()
        )

        # If we already received a question, run immediately; else, return the chain
        if question is not None:
            return chain.invoke(question)
        return chain

    except Exception as e:
        print(f"❌ Erro ao inicializar busca: {e}")
        return None
