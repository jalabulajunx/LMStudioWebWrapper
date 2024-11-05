# server/llm.py

import requests
from typing import Generator, Optional
import json

class LMStudioClient:
    """Client for interacting with LM Studio Server"""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        """
        Initialize the LM Studio client.
        
        Args:
            base_url (str): Base URL for the LM Studio Server
        """
        self.base_url = base_url
        self.completion_url = f"{base_url}/chat/completions"
    
    def generate_stream(self, prompt: str, **kwargs) -> Generator[str, None, None]:
        """
        Generate streaming response from LM Studio.
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional parameters for the API
            
        Yields:
            str: Text chunks from the response
            
        Raises:
            Exception: If the API request fails
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "top_p": kwargs.get("top_p", 0.95),
        }
        
        try:
            response = requests.post(
                self.completion_url,
                headers=headers,
                json=data,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        json_str = line.decode('utf-8').removeprefix('data: ')
                        if json_str.strip() == '[DONE]':
                            break
                        
                        json_data = json.loads(json_str)
                        chunk = json_data['choices'][0].get('delta', {}).get('content', '')
                        if chunk:
                            yield chunk
                    except json.JSONDecodeError:
                        continue
                        
        except requests.exceptions.RequestException as e:
            raise Exception(f"LM Studio API error: {str(e)}")
    
    def generate(self, prompt: str, **kwargs) -> Optional[str]:
        """
        Generate a complete response from LM Studio.
        
        Args:
            prompt (str): The input prompt
            **kwargs: Additional parameters for the API
            
        Returns:
            Optional[str]: The complete response text
            
        Raises:
            Exception: If the API request fails
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
            "top_p": kwargs.get("top_p", 0.95),
        }
        
        try:
            response = requests.post(
                self.completion_url,
                headers=headers,
                json=data
            )
            response.raise_for_status()
            
            json_response = response.json()
            return json_response['choices'][0]['message']['content']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"LM Studio API error: {str(e)}")
