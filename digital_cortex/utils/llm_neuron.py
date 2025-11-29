"""
LLM-Neuron: Interface for connecting local LLMs as processing neurons.

This module provides the interface between the Corpus Colosseum and local LLMs
running via Ollama. Each neuron can process inputs and generate outputs with
confidence scores.
"""

import requests
import json
import logging
from typing import Dict, Any, Optional, List
from ..utils.message import Message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMNeuron:
    """
    A single LLM-neuron that processes inputs and generates outputs.
    
    Each neuron:
    1. Receives a prompt/task
    2. Processes it using a local LLM (via Ollama)
    3. Generates a response with confidence score
    4. Returns a Message object
    """
    
    def __init__(self, 
                 name: str,
                 model: str = "llama3.2:1b",
                 ollama_url: str = "http://localhost:11434",
                 system_prompt: Optional[str] = None,
                 temperature: float = 0.7):
        """
        Initialize an LLM-Neuron.
        
        Args:
            name: Unique identifier for this neuron
            model: Ollama model to use (e.g., "llama3.2:1b", "mistral")
            ollama_url: URL of Ollama API
            system_prompt: Optional system prompt to define neuron's role
            temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        """
        self.name = name
        self.model = model
        self.ollama_url = ollama_url
        self.system_prompt = system_prompt
        self.temperature = temperature
        
        logger.info(f"LLM-Neuron '{name}' initialized (model={model})")
    
    def process(self, prompt: str, extract_confidence: bool = True) -> Message:
        """
        Process a prompt and generate a response.
        
        Args:
            prompt: The input prompt/task
            extract_confidence: Whether to extract confidence from response
            
        Returns:
            Message object with response and confidence score
        """
        # Build the full prompt
        full_prompt = prompt
        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{prompt}"
        
        # Add confidence extraction instruction if needed
        if extract_confidence:
            full_prompt += "\n\nIMPORTANT: At the very end of your response, on a new line, include exactly: [CONFIDENCE: X.XX] where X.XX is your confidence level from 0.0 to 1.0."
        
        # Call Ollama API
        try:
            response = self._call_ollama(full_prompt)
            content = response.strip()
            
            # Extract confidence if present
            confidence = self._extract_confidence(content) if extract_confidence else 0.5
            
            # Remove confidence tag from content (only if it's at the end)
            if "[CONFIDENCE:" in content:
                # Only remove if it appears at the end of the response
                confidence_pos = content.rfind("[CONFIDENCE:")
                if confidence_pos > len(content) * 0.7:  # If it's in the last 30% of the content
                    content = content[:confidence_pos].strip()
            
            # Create message
            message = Message.create(
                source=self.name,
                content=content,
                confidence=confidence,
                metadata={
                    "model": self.model,
                    "temperature": self.temperature
                }
            )
            
            logger.debug(f"{self.name} generated response (confidence={confidence:.2f})")
            return message
            
        except Exception as e:
            logger.error(f"Error processing with {self.name}: {e}")
            # Return error message with low confidence
            return Message.create(
                source=self.name,
                content=f"Error: {str(e)}",
                confidence=0.0,
                metadata={"error": True}
            )
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API to generate response."""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result.get("response", "")
    
    def _extract_confidence(self, text: str) -> float:
        """Extract confidence score from response text."""
        import re
        
        patterns = [
            r'\[CONFIDENCE:\s*([0-9.]+)\]',
            r'[Cc]onfidence:\s*([0-9.]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    confidence = float(match.group(1))
                    return max(0.0, min(1.0, confidence))
                except ValueError:
                    continue
        
        return 0.5
    
    def __repr__(self) -> str:
        return f"LLMNeuron(name={self.name}, model={self.model})"


class NeuronPool:
    """Manages a pool of LLM-Neurons for parallel processing."""
    
    def __init__(self):
        self.neurons: Dict[str, LLMNeuron] = {}
        logger.info("NeuronPool initialized")
    
    def add_neuron(self, neuron: LLMNeuron):
        """Add a neuron to the pool."""
        self.neurons[neuron.name] = neuron
        logger.info(f"Added neuron '{neuron.name}' to pool")
    
    def create_neuron(self, name: str, **kwargs) -> LLMNeuron:
        """Create and add a neuron to the pool."""
        neuron = LLMNeuron(name=name, **kwargs)
        self.add_neuron(neuron)
        return neuron
    
    def process_parallel(self, prompt: str, neuron_names: Optional[List[str]] = None) -> List[Message]:
        """Process a prompt with multiple neurons."""
        if neuron_names:
            neurons = [self.neurons[name] for name in neuron_names if name in self.neurons]
        else:
            neurons = list(self.neurons.values())
        
        if not neurons:
            logger.warning("No neurons available")
            return []
        
        logger.info(f"Processing with {len(neurons)} neurons")
        
        messages = []
        for neuron in neurons:
            message = neuron.process(prompt)
            messages.append(message)
        
        return messages
    
    def list_neurons(self) -> List[str]:
        """List all neuron names."""
        return list(self.neurons.keys())
