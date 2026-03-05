# Desafio MBA Engenharia de Software com IA - Full Cycle

RAG (Retrieval-Augmented Generation) simples com LangChain, OpenAI e Postgres + pgvector. O projeto permite:
- Ingerir um PDF para um banco vetorial (Postgres/pgvector).
- Fazer perguntas em um chat que busca trechos relevantes do PDF para responder.

Este README traz instruções completas de instalação, configuração e execução, além de dicas de troubleshooting.

---

## Visão geral da arquitetura
- `src/ingest.py`: carrega o PDF, faz split em chunks, gera embeddings e salva no Postgres (extensão `vector`).
- `src/search.py`: monta a cadeia RAG (retriever + prompt + LLM) e expõe a função `search_prompt`.
- `src/chat.py`: CLI interativa que usa a cadeia RAG para responder perguntas.
- `docker-compose.yml`: sobe Postgres já compatível com pgvector e cria a extensão.
- `pdfs/document.pdf`: PDF de exemplo para ingestão.

---

## Pré-requisitos
- Python 3.12+ (recomendado)
- Docker e Docker Compose
- Chave da API OpenAI válida

---

## Configuração do ambiente

1) Crie e ative um ambiente virtual Python:
```
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

2) Instale as dependências:
```
pip install -r requirements.txt
```

3) Crie um arquivo `.env` na raiz do projeto com as variáveis necessárias. Exemplo mínimo (para uso com o Docker Compose deste projeto):
```
OPENAI_API_KEY=coloque_sua_chave_aqui

# Banco local via docker-compose
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/rag

# Coleção no pgvector (tabela lógica usada pelo LangChain)
PG_VECTOR_COLLECTION_NAME=gemini_collection

# Caminho da pasta onde está o PDF de entrada
PDF_PATH=./pdfs

# Modelos (opcionais; valores default são mostrados nos respectivos scripts)
# Em search.py (busca):
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
# Em ingest.py (geração de embedding):
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
```

---

## Subindo o Postgres com pgvector

Execute na raiz do projeto:
```
docker compose up -d
```
O serviço `postgres` subirá e, em seguida, o job `bootstrap_vector_ext` criará a extensão `vector` automaticamente. Aguarde alguns segundos para que o `healthcheck` fique verde.

Para verificar:
```
docker compose ps
```

---

## Ingestão do PDF no banco vetorial

Garanta que:
- O arquivo `pdfs/document.pdf` existe (ou ajuste `PDF_PATH` e o nome do arquivo no código, se desejar).
- As variáveis do `.env` estão corretas.
- O Postgres (via Docker) está em execução.

Rode a ingestão:
```
python src/ingest.py
```
O script irá:
- Ler o PDF.
- Fazer o split em chunks.
- Gerar embeddings com OpenAI.
- Persistir os vetores na coleção/tabela informada.

---

## Executando o chat RAG

Com o banco populado, rode:
```
python src/chat.py
```
Você verá uma mensagem de inicialização bem-sucedida. Em seguida, digite suas perguntas. Para encerrar, digite `sair`.

Como funciona:
- O `search.py` cria um retriever a partir do PGVector (`as_retriever(k=10)`).
- O contexto recuperado é passado para o prompt, e o LLM (`gpt-5-nano`, via OpenAI) gera uma resposta.
- Se a informação não estiver no contexto, o sistema responde que não possui dados suficientes, evitando alucinações.

---

## Variáveis de ambiente (resumo)
- `OPENAI_API_KEY` (obrigatória): sua chave da OpenAI.
- `DATABASE_URL` (obrigatória): string de conexão SQLAlchemy/psycopg com o Postgres.
  - Exemplo Docker local: `postgresql+psycopg://postgres:postgres@localhost:5432/rag`.
- `PG_VECTOR_COLLECTION_NAME` (obrigatória na ingestão): nome lógico da coleção/tabela de vetores. Ex.: `gemini_collection`.
- `PDF_PATH` (obrigatória na ingestão): pasta onde está o PDF. Ex.: `./pdfs`.
- `OPENAI_EMBEDDING_MODEL` (opcional no search e no ingest; default: `text-embedding-3-small`).

Observação: o modelo do chat (`ChatOpenAI`) está definido no código como `gpt-5-nano`. Para alterar, edite `src/search.py` (parâmetro `model` do `ChatOpenAI`).

---

## Dicas de troubleshooting
- Erro "Não foi possível iniciar o chat" ao rodar `src/chat.py`:
  - Verifique `OPENAI_API_KEY`, `DATABASE_URL` e se o Postgres está de pé.
  - Confirme que a extensão `vector` foi criada (o job `bootstrap_vector_ext` faz isso automaticamente).
- Erros de autenticação OpenAI: cheque se a chave é válida e se não há proxies/bloqueios de rede.
- Erro de conversão de tipos/`NoneType` na busca:
  - Corrigido na implementação atual: o pipeline só executa a busca quando há pergunta, e usa `as_retriever(k=10)`.
- Ingestão não encontra PDF:
  - Confirme `PDF_PATH` e a existência de `document.pdf` no caminho configurado.
- Conexão recusada ao Postgres:
  - Aguarde alguns segundos após `docker compose up -d` ou rode `docker compose logs -f postgres`.

---

## Comandos úteis
- Subir serviços: `docker compose up -d`
- Parar serviços: `docker compose down`
- Acompanhar logs do Postgres: `docker compose logs -f postgres`

---

## Estrutura do projeto
```
README.md
docker-compose.yml
pdfs/document.pdf
requirements.txt
src/chat.py
src/ingest.py
src/search.py
```

---

## Licença
Projeto criado para fins educacionais no contexto do desafio MBA Full Cycle. Ajuste conforme suas necessidades.