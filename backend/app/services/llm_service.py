import json
import logging
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Type, TypeVar, Optional
import httpx
from pydantic import BaseModel, ValidationError

from app.config import settings

logger = logging.getLogger("cognito.llm")

T = TypeVar("T", bound=BaseModel)

class LLMProviderException(Exception):
    """Raised when an LLM provider encounters an unrecoverable failure."""
    pass

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Cleans and extracts JSON object from raw LLM output,
    stripping markdown backticks and preamble text.
    """
    cleaned = text.strip()
    
    # 1. Direct JSON parse
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Extract from markdown code fence ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        inner = match.group(1).strip()
        try:
            return json.loads(inner)
        except Exception:
            pass

    # 3. Find outer-most { ... } brackets
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = cleaned[start:end+1]
        try:
            return json.loads(snippet)
        except Exception:
            pass

    raise ValueError(f"Could not parse valid JSON from LLM response snippet: {text[:200]}...")


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], temperature: float) -> str:
        """Generates raw text response for chat messages."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is reachable and configured."""
        pass


class OllamaProvider(BaseLLMProvider):
    """
    Local LLM Provider running via Ollama (e.g. llama3, mistral, llama3.2).
    Communicates via REST on http://localhost:11434.
    """
    def __init__(self, base_url: str = settings.OLLAMA_BASE_URL, model: str = settings.OLLAMA_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = settings.LLM_TIMEOUT

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    def generate(self, messages: List[Dict[str, str]], temperature: float = settings.LLM_TEMPERATURE) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "format": "json",
            "keep_alive": settings.OLLAMA_KEEP_ALIVE,
            "options": {
                "temperature": temperature,
            }
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/api/chat", json=payload)
                if res.status_code != 200:
                    raise LLMProviderException(f"Ollama returned status {res.status_code}: {res.text}")
                data = res.json()
                return data.get("message", {}).get("content", "")
        except httpx.ConnectError:
            raise LLMProviderException(f"Cannot connect to local Ollama server at {self.base_url}. Is Ollama running?")
        except httpx.TimeoutException:
            raise LLMProviderException(
                f"Ollama inference timed out after {self.timeout}s for model '{self.model}'. "
                "Increase LLM_TIMEOUT or warm the model with an initial request."
            )
        except Exception as e:
            raise LLMProviderException(f"Ollama inference error: {str(e)}")


class OpenAIProvider(BaseLLMProvider):
    """
    Cloud / OpenAI-compatible LLM Provider (OpenAI, Groq, vLLM, DeepSeek, etc.).
    """
    def __init__(
        self,
        api_key: Optional[str] = settings.OPENAI_API_KEY,
        base_url: str = settings.OPENAI_BASE_URL,
        model: str = settings.OPENAI_MODEL
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = settings.LLM_TIMEOUT

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate(self, messages: List[Dict[str, str]], temperature: float = settings.LLM_TEMPERATURE) -> str:
        if not self.is_available():
            raise LLMProviderException("OpenAI API key is missing or not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {"type": "json_object"}
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
                if res.status_code != 200:
                    raise LLMProviderException(f"OpenAI error {res.status_code}: {res.text}")
                data = res.json()
                return data["choices"][0]["message"]["content"]
        except Exception as e:
            raise LLMProviderException(f"OpenAI API call failed: {str(e)}")


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini Provider using Google Generative Language REST API.
    """
    def __init__(
        self,
        api_key: Optional[str] = settings.GEMINI_API_KEY,
        model: str = settings.GEMINI_MODEL
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = settings.LLM_TIMEOUT

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate(self, messages: List[Dict[str, str]], temperature: float = settings.LLM_TEMPERATURE) -> str:
        if not self.is_available():
            raise LLMProviderException("Gemini API key is missing.")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        # Convert chat messages to Gemini content format
        system_instruction = ""
        contents = []
        for m in messages:
            if m["role"] == "system":
                system_instruction = m["content"]
            else:
                role = "user" if m["role"] == "user" else "model"
                contents.append({"role": role, "parts": [{"text": m["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "responseMimeType": "application/json"
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, json=payload)
                if res.status_code != 200:
                    raise LLMProviderException(f"Gemini error {res.status_code}: {res.text}")
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            raise LLMProviderException(f"Gemini API call failed: {str(e)}")


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic Claude Provider using Messages REST API.
    """
    def __init__(
        self,
        api_key: Optional[str] = settings.ANTHROPIC_API_KEY,
        model: str = settings.ANTHROPIC_MODEL
    ):
        self.api_key = api_key
        self.model = model
        self.timeout = settings.LLM_TIMEOUT

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 5)

    def generate(self, messages: List[Dict[str, str]], temperature: float = settings.LLM_TEMPERATURE) -> str:
        if not self.is_available():
            raise LLMProviderException("Anthropic API key is missing.")

        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        system_prompt = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system_prompt = m["content"]
            else:
                user_messages.append({"role": m["role"], "content": m["content"]})

        payload = {
            "model": self.model,
            "system": system_prompt + "\nYou must strictly respond with a valid JSON object only.",
            "messages": user_messages,
            "temperature": temperature,
            "max_tokens": 1500
        }
        try:
            with httpx.Client(timeout=self.timeout) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code != 200:
                    raise LLMProviderException(f"Anthropic error {res.status_code}: {res.text}")
                data = res.json()
                return data["content"][0]["text"]
        except Exception as e:
            raise LLMProviderException(f"Anthropic API call failed: {str(e)}")


class UnifiedLLMService:
    """
    High-level facade orchestrating LLM calls, provider selection,
    retry loops, Pydantic schema validation, and fallback mechanisms.
    """
    def __init__(self):
        self.ollama = OllamaProvider()
        self.openai = OpenAIProvider()
        self.gemini = GeminiProvider()
        self.anthropic = AnthropicProvider()
        self.active_provider: Optional[BaseLLMProvider] = None
        self._init_provider()

    def _init_provider(self):
        provider_name = settings.LLM_PROVIDER.lower().strip()
        
        if provider_name == "ollama":
            self.active_provider = self.ollama
        elif provider_name == "openai":
            self.active_provider = self.openai
        elif provider_name == "gemini":
            self.active_provider = self.gemini
        elif provider_name == "anthropic":
            self.active_provider = self.anthropic
        elif provider_name == "auto":
            # Auto-detection priority: Cloud API (if configured) -> Local Ollama (if running) -> None (fallback)
            if self.openai.is_available():
                self.active_provider = self.openai
                logger.info("[LLMService] Auto-selected OpenAI cloud provider.")
            elif self.gemini.is_available():
                self.active_provider = self.gemini
                logger.info("[LLMService] Auto-selected Google Gemini cloud provider.")
            elif self.anthropic.is_available():
                self.active_provider = self.anthropic
                logger.info("[LLMService] Auto-selected Anthropic Claude provider.")
            elif self.ollama.is_available():
                self.active_provider = self.ollama
                logger.info("[LLMService] Auto-selected local Ollama provider.")
            else:
                self.active_provider = None
                logger.info("[LLMService] No external LLM reachable. Operating with internal cognitive heuristic fallback.")
        else:
            self.active_provider = None

    def _provider_candidates(self) -> List[BaseLLMProvider]:
        """Return the active provider followed by configured providers for failover."""
        providers = [self.active_provider] if self.active_provider else []
        for provider in (self.openai, self.gemini, self.anthropic, self.ollama):
            if provider not in providers and provider.is_available():
                providers.append(provider)
        return providers

    def get_provider_status(self) -> Dict[str, Any]:
        """Returns the operational status of all configured providers."""
        return {
            "active_mode": settings.LLM_PROVIDER,
            "active_provider": self.active_provider.__class__.__name__ if self.active_provider else "InternalCognitiveEngine",
            "ollama_available": self.ollama.is_available(),
            "ollama_model": settings.OLLAMA_MODEL,
            "ollama_endpoint": settings.OLLAMA_BASE_URL,
            "openai_configured": self.openai.is_available(),
            "openai_model": settings.OPENAI_MODEL,
            "gemini_configured": self.gemini.is_available(),
            "gemini_model": settings.GEMINI_MODEL,
            "anthropic_configured": self.anthropic.is_available(),
            "anthropic_model": settings.ANTHROPIC_MODEL,
        }

    def generate_structured(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        temperature: float = settings.LLM_TEMPERATURE,
        fallback_fn: Optional[Any] = None
    ) -> T:
        """
        Generates structured data strictly validated against a Pydantic model.
        Features automatic retry with error feedback and resilient fallback.
        """
        # If no external provider is online, execute fallback immediately.
        providers = self._provider_candidates()
        if not providers:
            if fallback_fn:
                return fallback_fn()
            raise LLMProviderException("No LLM provider available and no fallback function provided.")

        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        
        # Inject schema instruction into system or user prompt
        prompt_with_schema = list(messages)
        schema_instruction = (
            f"\n\nCRITICAL OUTPUT REQUIREMENT:\n"
            f"You MUST return a strictly valid JSON object conforming to this schema:\n"
            f"{schema_json}\n"
            f"Do not include any Markdown text, explanations, or commentary outside the JSON."
        )
        
        # Append to last message
        prompt_with_schema[-1] = {
            "role": prompt_with_schema[-1]["role"],
            "content": prompt_with_schema[-1]["content"] + schema_instruction
        }

        last_error = "No provider attempt was made."
        for provider in providers:
            current_messages = list(prompt_with_schema)
            for attempt in range(settings.LLM_MAX_RETRIES + 1):
                raw_response = ""
                try:
                    raw_response = provider.generate(current_messages, temperature=temperature)
                    json_data = extract_json_from_text(raw_response)
                    validated = response_model.model_validate(json_data)
                    self.active_provider = provider
                    return validated
                except (ValueError, ValidationError, LLMProviderException) as err:
                    last_error = str(err)
                    logger.warning(
                        "[LLMService] %s attempt %s validation failed: %s",
                        provider.__class__.__name__,
                        attempt + 1,
                        err,
                    )
                    if attempt < settings.LLM_MAX_RETRIES:
                        current_messages.append({"role": "assistant", "content": raw_response or "{}"})
                        current_messages.append({
                            "role": "user",
                            "content": (
                                f"Your response did not match the required schema: {last_error}. "
                                "Correct it and output only the valid JSON object."
                            )
                        })

        # If LLM retries exhausted, fall back gracefully
        if fallback_fn:
            logger.warning(f"[LLMService] LLM retries exhausted ({last_error}). Triggering deterministic fallback.")
            return fallback_fn()

        raise LLMProviderException(f"Failed to generate structured data from LLM after retries: {last_error}")

# Global Singleton LLM Service
llm_service = UnifiedLLMService()
