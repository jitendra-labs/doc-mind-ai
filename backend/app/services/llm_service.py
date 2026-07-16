import json
from typing import AsyncGenerator
import httpx
from partial_json_parser import ensure_json

from app.config import config
from app.core.logging_config import logger


class LlmService:

    def __init__(self):
        # self.ollama_url = config.ollama_base_url
        self.ollama_url = "http://172.18.0.1:11434"
        self.model_name = config.ollama_model
        
        # Enforce deterministic constraints required for clinical data processing
        self.inference_options = {
            "temperature": 0.0,  # Zero variance outlaws creative guessing
            "top_p": 0.1,
            "seed": 42
        }

    async def generate_response(self, system_prompt: str, user_prompt: str) -> str:
        """
        Executes a standard non-streaming text generation block.
        Yields execution control cleanly to the FastAPI event loop during network transport.
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "options": self.inference_options,
            "stream": False
        }

        # Keep a generous timeout window since local token generation speeds 
        # depend directly on your local hardware constraints
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                logger.info(f"Dispatching inference request to Ollama using model: {self.model_name}")
                response = await client.post(f"{self.ollama_url}/api/chat", json=payload)
                response.raise_for_status()
                
                response_data = response.json()
                return response_data["message"]["content"]

            except httpx.HTTPError as http_err:
                logger.error(f"Upstream inference link failure: {str(http_err)}", exc_info=True)
                return "Error: Unable to synthesize response due to a connection issue with the local model engine."

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        """
        Streams generated text tokens chunk-by-chunk over a live network connection.
        Crucial for providing an interactive UI experience without waiting for full text compilation.
        """
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "options": self.inference_options,
            "stream": True,
            "format": "json"
        }

        raw_json_buffer = ""
        last_sent_answer_length = 0

        logger.info(f"Initializing real-time token stream using model: {self.model_name}")
        
        # Use a context manager to keep the network transport socket open for streaming
        async with httpx.AsyncClient(timeout=90.0) as client:
            async with client.stream("POST", f"{self.ollama_url}/api/chat", json=payload) as response:
                if response.status_code != 200:
                    logger.error(f"Ollama streaming initialization rejected with status: {response.status_code}")
                    yield "Error: Local model service rejected streaming transport request."
                    return

                # Read line-delimited JSON objects streamed back by Ollama
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    
                    try:
                        # 1. Parse Ollama's outer envelope to get the raw text token
                        envelope = json.loads(line)
                        token = envelope.get("message", {}).get("content", "")
                        raw_json_buffer += token

                        # 2. Use partial parser to complete the broken JSON string on the fly
                        completed_json_str = ensure_json(raw_json_buffer)
                        parsed_data = json.loads(completed_json_str)

                        # logger.info(f"llm parsed_data ---> {parsed_data}")

                        # 3. If the model has started generating the "answer" key
                        if isinstance(parsed_data, dict) and "answer" in parsed_data:
                            current_answer = parsed_data["answer"]
                            
                            # Determine only the new text characters generated since the last yield
                            if len(current_answer) > last_sent_answer_length:
                                new_text_delta = current_answer[last_sent_answer_length:]
                                last_sent_answer_length = len(current_answer)
                                
                                # Stream just the text chunk to your user
                                yield new_text_delta

                    except Exception as e:
                        # Swallowing partial parsing errors while keys are still drawing
                        continue
        
        # --- Stream Finished ---
        # 4. Now parse the finalized, full JSON completely to handle internally on the backend
        try:
            final_json = json.loads(raw_json_buffer)
            logger.info(f"--- Internal Backend Analytics ---")
            logger.info(f"Confidence Level: {final_json.get('confidence')}")
            logger.info(f"Retrieved Sources: {final_json.get('sources')}")
            
            # Save sources or metadata to SQL/NoSQL database here if needed!
            # database.save_chat_metadata(sources=final_json.get('sources'))
            
        except Exception as e:
            logger.error(f"Failed to parse final backend JSON payload: {e}")