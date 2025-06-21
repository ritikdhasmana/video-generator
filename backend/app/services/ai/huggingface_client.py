from huggingface_hub import InferenceClient
import logging
import asyncio
from typing import Optional

# Set up logging
logger = logging.getLogger(__name__)

class HuggingFaceClient:
    def __init__(self, api_key: str, model: str = "meta-llama/Llama-3.1-8B-Instruct"):
        self.api_key = api_key
        self.model = model
        self.client = InferenceClient(
            model=model,
            token=api_key
        )
        logger.info(f"HuggingFaceClient: InferenceClient initialized with model: {model}")
    
    async def generate_text(self, prompt: str, max_length: int = 200) -> Optional[str]:
        """Generate text using Hugging Face model"""
        try:
            logger.info(f"HuggingFaceClient: Sending request to Hugging Face model: {self.model}")
            
            # Create the full prompt for the model
            full_prompt = f"<|system|>You are a helpful AI assistant that creates engaging video advertisement scripts.</|system|><|user|>{prompt}</|user|><|assistant|>"
            
            # Generate text
            response = await asyncio.to_thread(
                self.client.text_generation,
                full_prompt,
                max_new_tokens=max_length,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                repetition_penalty=1.1,
                stop=["</|assistant|>", "<|user|>", "<|system|>"]
            )
            
            if response and response.strip():
                logger.info(f"HuggingFaceClient: Received response from Hugging Face: {len(response)} characters")
                return response.strip()
            else:
                logger.error("HuggingFaceClient: Hugging Face returned empty response")
                return None
                
        except Exception as e:
            logger.error(f"HuggingFaceClient: Failed to generate text with Hugging Face: {str(e)}")
            return None
    
    async def check_availability(self) -> bool:
        """Check if the model is available"""
        try:
            # Try a simple request to check availability
            test_response = await self.generate_text("Hello", max_length=10)
            return test_response is not None
        except Exception as e:
            logger.error(f"HuggingFaceClient: Failed to check Hugging Face availability: {str(e)}")
            return False 