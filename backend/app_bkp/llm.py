"""
Thin wrapper around Ollama's HTTP API for local LLM generation.
No API keys, no external calls — everything stays on your machine.
"""
import requests
from app_bkp.config import settings


def generate(prompt: str, system: str = None, temperature: float = 0.1) -> str:
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system

    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data.get("response", "").strip()
