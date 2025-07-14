"""
LLM client for text processing using OpenAI API and Ollama
"""
import logging
import requests
from typing import Dict, Any, Optional
import json
import config


class LLMClient:
    def __init__(self, providers_config: Dict[str, Dict], default_provider: str):
        self.providers_config = providers_config
        self.default_provider = default_provider
        self.logger = logging.getLogger(__name__)
        
    def _get_provider_config(self, provider: str = None) -> Dict[str, Any]:
        """Get configuration for specified provider"""
        provider = provider or self.default_provider
        
        if provider not in self.providers_config:
            raise ValueError(f"Unknown provider: {provider}")
            
        return self.providers_config[provider]
        
    async def process_text(self, text: str, mode: str, provider: str = None) -> str:
        """Process text using specified mode and provider"""
        try:
            provider = provider or self.default_provider
            provider_config = self._get_provider_config(provider)
            
            # Get the prompt for this mode
            if mode not in config.PROCESSING_MODES:
                raise ValueError(f"Unknown processing mode: {mode}")
                
            system_prompt = config.PROCESSING_MODES[mode]
            
            # Prepare the API request
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add authorization if API key is provided
            api_key = provider_config.get("api_key", "")
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
                
            # Prepare messages for chat completion
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]
            
            payload = {
                "model": provider_config["model"],
                "messages": messages,
                "temperature": 0.3,  # Slightly creative but focused
                "max_tokens": 1000,  # Reasonable limit
                "stream": False  # TODO: v2 - implement streaming
            }
            
            # Make the API request
            base_url = provider_config["base_url"].rstrip("/")
            url = f"{base_url}/chat/completions"
            
            self.logger.debug(f"Making LLM request to {provider} at {url}")
            
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30  # 30 second timeout
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                processed_text = result["choices"][0]["message"]["content"].strip()
                
                # Log token usage if available
                if "usage" in result:
                    usage = result["usage"]
                    self.logger.debug(f"Token usage - input: {usage.get('prompt_tokens', 'N/A')}, "
                                    f"output: {usage.get('completion_tokens', 'N/A')}, "
                                    f"total: {usage.get('total_tokens', 'N/A')}")
                
                return processed_text
            else:
                raise ValueError("No valid response from LLM")
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"LLM processing failed: {e}")
            raise
            
    def test_connection(self, provider: str = None) -> bool:
        """Test connection to the LLM provider"""
        try:
            provider = provider or self.default_provider
            provider_config = self._get_provider_config(provider)
            
            # Simple test with minimal input
            test_result = self.process_text(
                "Hello", 
                "transcribe", 
                provider
            )
            
            self.logger.info(f"LLM connection test successful for {provider}")
            return True
            
        except Exception as e:
            self.logger.error(f"LLM connection test failed for {provider}: {e}")
            return False
            
    def get_available_providers(self) -> list:
        """Get list of configured providers"""
        return list(self.providers_config.keys())
        
    def get_available_modes(self) -> list:
        """Get list of available processing modes"""
        return list(config.PROCESSING_MODES.keys())