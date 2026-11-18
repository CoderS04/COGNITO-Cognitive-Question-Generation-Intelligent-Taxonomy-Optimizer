# LLM-powered analysis and generation

COGNITO uses the same validated LLM service for Bloom's classification, difficulty
estimation, question generation, and reframing. Responses are parsed as JSON and
validated with Pydantic; malformed responses are retried and then passed to the
configured fallback.

## Local Ollama

1. Install Ollama and download a model:

   ```powershell
   ollama pull llama3
   ollama serve
   ```

2. Copy `backend\.env.example` to `backend\.env` and set:

   ```dotenv
   LLM_PROVIDER=ollama
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=llama3
   OLLAMA_KEEP_ALIVE=10m
   LLM_TIMEOUT=180
   LLM_TEMPERATURE=0.15
   ```

The first request can be slow while Ollama loads a model into memory. The
180-second timeout prevents a cold-start request from falling back prematurely.
After changing `backend\.env`, restart the backend.

## Cloud provider

Set `LLM_PROVIDER` to `openai`, `gemini`, or `anthropic` and provide only that
provider's key in `backend\.env`. OpenAI-compatible endpoints can be selected with
`OPENAI_BASE_URL`. `LLM_PROVIDER=auto` tries configured cloud providers and then
Ollama.

## API examples

Classify a question and estimate its difficulty:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/questions/analyze `
  -H "Content-Type: application/json" `
  -d '{"text":"Design a fault-tolerant distributed system for the stated workload.","marks":10}'
```

Reframe a stored question using its syllabus and retrieved ChromaDB context:

```powershell
curl.exe -X POST http://localhost:8000/api/v1/questions/reframe `
  -H "Content-Type: application/json" `
  -d '{"question_id":12,"target_level":"L5"}'
```

The response includes the target Bloom level, validated question text, rubric
outline, and retrieved ChromaDB context IDs. New questions are indexed with the
stable `q_<PostgreSQL id>` ChromaDB ID and that ID is persisted in
`questions.embedding_id`.
