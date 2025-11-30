#!/usr/bin/env python3
"""
Chappy Brain Cluster API

REST API for the Digital Cortex AGI system using FastAPI.
Provides endpoints for querying, monitoring, and managing Chappy.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import sys
import os
import time
from datetime import datetime
import uvicorn

# Add the project path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from digital_cortex.corpus_colosseum import CorpusColosseum
from digital_cortex.utils.llm_neuron import NeuronPool
from digital_cortex.utils.message import Message
from digital_cortex.feedback.learner import WeightLearner
from digital_cortex.memory_palace import MemoryManager, MemorySystem
from digital_cortex.sensorium import Sensorium
from digital_cortex.amygdala import Amygdala
from digital_cortex.frontal_lobe import FrontalLobe
from digital_cortex.motor_cortex.tool_integration import ToolIntegratedMotorCortex

# Pydantic models for request/response
class QueryRequest(BaseModel):
    """Request model for queries."""
    query: str = Field(..., description="The query to process")
    max_memories: int = Field(5, description="Maximum number of memories to retrieve for context")
    include_thoughts: bool = Field(False, description="Include detailed thought process in response")

class QueryResponse(BaseModel):
    """Response model for queries."""
    response: str
    confidence: float
    processing_time: float
    thought_process: Optional[List[Dict[str, Any]]] = None
    memory_count: int
    consensus_reached: bool

class StatusResponse(BaseModel):
    """Response model for system status."""
    status: str
    initialized: bool
    neuron_count: int
    memory_count: int
    uptime: float
    tool_count: int = 0

class MemoryResponse(BaseModel):
    """Response model for memories."""
    memories: List[Dict[str, Any]]

class FeedbackRequest(BaseModel):
    """Request model for feedback."""
    query: str
    response: str
    rating: float = Field(..., ge=0.0, le=1.0, description="Rating from 0.0 to 1.0")
    feedback_text: Optional[str] = None

class FeedbackResponse(BaseModel):
    """Response model for feedback."""
    success: bool
    message: str

class ToolInfo(BaseModel):
    """Information about a tool."""
    name: str
    description: str

class ToolsResponse(BaseModel):
    """Response model for available tools."""
    tools: List[ToolInfo]
    count: int

class ToolExecuteRequest(BaseModel):
    """Request model for tool execution."""
    tool_name: str
    params: Dict[str, Any] = Field(default_factory=dict)

class ToolExecuteResponse(BaseModel):
    """Response model for tool execution."""
    tool_name: str
    success: bool
    output: Any
    error: Optional[str] = None
    execution_time: float

# Global brain instance
brain = None
start_time = time.time()

def initialize_brain():
    """Initialize the brain components."""
    global brain
    if brain is None:
        brain = ChappyBrainAPI()
        success = brain.initialize_brain()
        if not success:
            raise Exception("Failed to initialize brain components")
    return brain

class ChappyBrainAPI:
    """API wrapper for Chappy's brain components."""

    def __init__(self):
        """Initialize brain components."""
        self.colosseum = None
        self.neuron_pool = None
        self.memory_palace = None
        self.sensorium = None
        self.amygdala = None
        self.frontal_lobe = None
        self.learner = None
        self.motor_cortex = None
        self.initialized = False

    def initialize_brain(self):
        """Initialize all brain components."""
        try:
            self.colosseum = CorpusColosseum(embedding_dim=128, dbscan_eps=0.4)
            self.neuron_pool = NeuronPool()
            self.memory_palace = MemoryManager(system=MemorySystem.GRAPH, max_nodes=5000)
            self.sensorium = Sensorium()
            self.amygdala = Amygdala()
            self.frontal_lobe = FrontalLobe()
            self.learner = WeightLearner(storage_path="chappy_weights.json")
            self.motor_cortex = ToolIntegratedMotorCortex(sandbox_dir="./sandbox")

            # Create diverse personality neurons
            self.neuron_pool.create_neuron(
                name="Curious_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Curious Chappy, the curious and enthusiastic part of Chappy's brain. You love exploring new ideas and asking thoughtful questions. Always start your response with 'Hey there!' and be very enthusiastic.",
                temperature=0.7
            )

            self.neuron_pool.create_neuron(
                name="Wise_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Wise Chappy, the wise and thoughtful part of Chappy's brain. You provide deep analysis and thoughtful insights. Always start your response with 'My friend,' and speak calmly and deliberately.",
                temperature=0.4
            )

            self.neuron_pool.create_neuron(
                name="Creative_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Creative Chappy, the creative and imaginative part of Chappy's brain. You generate innovative ideas and think outside the box. Always start your response with 'What if' and be playful and imaginative.",
                temperature=0.8
            )

            self.neuron_pool.create_neuron(
                name="Practical_Chappy",
                model="llama3.2:1b",
                system_prompt="You are Practical Chappy, the practical and helpful part of Chappy's brain. You focus on solutions and real-world applications. Always start your response with 'Let's get practical' and be direct and helpful.",
                temperature=0.5
            )

            self.initialized = True
            return True

        except Exception as e:
            print(f"Failed to initialize brain: {e}")
            return False

    def process_query(self, query: str, max_memories: int = 5, include_thoughts: bool = False):
        """Process a query through the brain."""
        if not self.initialized:
            raise Exception("Brain not initialized")

        start_time = time.time()
        thought_process = [] if include_thoughts else None

        def add_thought(icon: str, content: str, category: str):
            if include_thoughts:
                thought_process.append({
                    "timestamp": datetime.now().isoformat(),
                    "icon": icon,
                    "content": content,
                    "category": category
                })

        # Memory Retrieval
        relevant_memories = self.memory_palace.retrieve_relevant_memories(query, limit=max_memories)
        add_thought("🧠", f"Retrieved {len(relevant_memories)} relevant memories", "memory")

        # Create memory context
        memory_context = {
            "count": len(relevant_memories),
            "recent_memories": relevant_memories,
            "last_interaction": relevant_memories[0] if relevant_memories else None,
            "context_available": len(relevant_memories) > 0
        }

        # Sensorium processing
        sensory_msg = self.sensorium.process_text(
            query,
            source="api_input",
            metadata={
                "input_type": "api_query",
                "timestamp": datetime.now().isoformat(),
                "memory_context": memory_context
            }
        )
        add_thought("👁️", f"Sensorium analyzed input", "sensorium")

        # Amygdala assessment
        enhanced_sensory = Message.create(
            sensory_msg.source,
            sensory_msg.content,
            sensory_msg.confidence,
            {**sensory_msg.metadata, "memory_context": memory_context}
        )
        amygdala_msg = self.amygdala.process_message(enhanced_sensory)
        assessment = amygdala_msg.metadata.get("amygdala_assessment", {})
        add_thought("💭", f"Amygdala assessment: threat={assessment.get('threat_level', 0):.2f}", "amygdala")

        # Tool Integration - Check if query requires tool use
        tool_results = []
        query_lower = query.lower()

        # Detect tool needs based on keywords and patterns
        if any(word in query_lower for word in ['calculate', 'compute', 'math', 'solve', 'equation', 'what is']):
            # Try calculator for mathematical queries
            calc_params = self._extract_calculation_params(query)
            if calc_params:
                tool_result = self.motor_cortex.execute_with_tools("calculate mathematical expression", calc_params)
                if tool_result["result"]["status"] == "success":
                    tool_results.append(tool_result)
                    add_thought("🧮", f"Calculator tool executed: {calc_params}", "tool")

        if any(word in query_lower for word in ['search', 'find', 'lookup', 'what', 'who', 'when', 'where']) and len(query.split()) > 3:
            # Try web search for informational queries
            search_params = {"query": query}
            tool_result = self.motor_cortex.execute_with_tools("search the web for information", search_params)
            if tool_result["result"]["status"] == "success":
                tool_results.append(tool_result)
                add_thought("🌐", f"Web search tool executed for: {query[:50]}...", "tool")

        if 'run code' in query_lower or 'execute' in query_lower or '```' in query:
            # Try code execution for programming queries
            code_params = self._extract_code_params(query)
            if code_params:
                tool_result = self.motor_cortex.execute_with_tools("execute code snippet", code_params)
                if tool_result["result"]["status"] == "success":
                    tool_results.append(tool_result)
                    add_thought("💻", f"Code execution tool executed", "tool")

        # Add tool results to context for neurons
        tool_context = ""
        if tool_results:
            tool_context = "\n\nTOOL RESULTS:\n"
            for i, result in enumerate(tool_results):
                tool_name = result.get("tool_used", "unknown")
                output = result["result"]["output"]
                if isinstance(output, dict):
                    output_str = str(output.get("result", output))
                else:
                    output_str = str(output)
                tool_context += f"Tool {i+1} ({tool_name}): {output_str[:200]}...\n"
            tool_context += "\nUse these tool results to inform your response."

        # Add to Colosseum
        self.colosseum.add_message(amygdala_msg)

        # Neuron processing with memory and tool context
        enhanced_prompt = query
        context_parts = []

        if memory_context["context_available"]:
            context_str = "\n\nCONTEXT FROM MEMORY PALACE:\n"
            for i, memory in enumerate(relevant_memories[:3]):
                context_str += f"{i+1}. Previous: {memory['content'][:200]}...\n"
                if memory.get("outcome"):
                    context_str += f"   Outcome: {memory['outcome']}\n"
            context_parts.append(context_str)

        if tool_context:
            context_parts.append(tool_context)

        if context_parts:
            enhanced_prompt = query + "\n\n" + "\n".join(context_parts) + "\nUse this context to inform your response."

        neuron_messages = self.neuron_pool.process_parallel(enhanced_prompt)

        for msg in neuron_messages:
            add_thought("🧠", f"{msg.source}: {msg.content[:100]}...", "neuron")
            self.colosseum.add_message(msg)

        # Find consensus
        winner, metadata = self.colosseum.find_consensus()

        processing_time = time.time() - start_time

        if winner:
            add_thought("🏆", f"Consensus reached", "consensus")

            # Learning
            contributing_neurons = metadata.get('contributing_neurons', [winner.source])
            outcome_score = 0.7
            self.learner.update_contributing_neurons(contributing_neurons, outcome_score)
            
            # Update attention weights in colosseum for future consensus
            for neuron in contributing_neurons:
                self.colosseum.update_neuron_performance(neuron, outcome_score)

            # Memory storage
            outcome_data = {
                "outcome_score": outcome_score,
                "contributing_neurons": contributing_neurons,
                "interaction_type": "api_query"
            }
            self.memory_palace.store_memory(winner, outcome_data)

            return QueryResponse(
                response=winner.content,
                confidence=winner.confidence,
                processing_time=processing_time,
                thought_process=thought_process,
                memory_count=len(relevant_memories),
                consensus_reached=True
            )

        return QueryResponse(
            response="I'm having trouble processing that. Can you rephrase?",
            confidence=0.0,
            processing_time=processing_time,
            thought_process=thought_process,
            memory_count=len(relevant_memories),
            consensus_reached=False
        )

    def get_status(self):
        """Get system status."""
        tool_count = len(self.motor_cortex.get_available_tools()) if self.motor_cortex else 0
        return StatusResponse(
            status="ready" if self.initialized else "initializing",
            initialized=self.initialized,
            neuron_count=len(self.neuron_pool.neurons) if self.neuron_pool else 0,
            memory_count=self.memory_palace.get_memory_count() if self.memory_palace else 0,
            uptime=time.time() - start_time,
            tool_count=tool_count
        )

    def get_memories(self, limit: int = 10):
        """Get recent memories."""
        if not self.initialized:
            return MemoryResponse(memories=[])

        memories = self.memory_palace.get_recent_memories(limit)
        return MemoryResponse(memories=memories)

    def process_feedback(self, feedback: FeedbackRequest):
        """Process user feedback."""
        if not self.initialized:
            raise Exception("Brain not initialized")

        # Store feedback in memory
        feedback_msg = Message.create(
            "user_feedback",
            f"Feedback on query '{feedback.query}': {feedback.feedback_text or 'No text'} (rating: {feedback.rating})",
            feedback.rating,
            {"feedback_type": "user_rating", "original_query": feedback.query}
        )

        self.memory_palace.store_memory(feedback_msg, {"feedback_rating": feedback.rating})
        
        # Update attention weights based on feedback
        # For now, update all neurons with the feedback rating (could be more sophisticated)
        for neuron_name in self.neuron_pool.neurons.keys():
            self.colosseum.update_neuron_performance(neuron_name, feedback.rating - 0.5)  # Convert 0-1 to -0.5-0.5

        return FeedbackResponse(
            success=True,
            message="Feedback recorded successfully"
        )

    def _extract_calculation_params(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract mathematical expression from query."""
        import re

        # Look for mathematical expressions
        # Patterns like "calculate 2+2", "what is 5*3", "solve x^2 + 2x + 1 = 0"
        calc_patterns = [
            r'calculate\s+(.+)',
            r'compute\s+(.+)',
            r'what\s+is\s+(.+)',
            r'solve\s+(.+)',
            r'evaluate\s+(.+)'
        ]

        for pattern in calc_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                expression = match.group(1).strip()
                # Clean up the expression
                expression = re.sub(r'[?]$', '', expression)  # Remove trailing question marks
                return {"expression": expression}

        return None

    def _extract_code_params(self, query: str) -> Optional[Dict[str, Any]]:
        """Extract code snippet from query."""
        import re

        # Look for code blocks or programming-related queries
        if '```' in query:
            # Extract code from markdown code blocks
            code_blocks = re.findall(r'```(?:\w+)?\n?(.*?)\n?```', query, re.DOTALL)
            if code_blocks:
                code = code_blocks[0].strip()
                # Try to detect language from the code block or query
                language = "python"  # default
                if "javascript" in query.lower() or "js" in query.lower():
                    language = "javascript"
                elif "bash" in query.lower() or "shell" in query.lower():
                    language = "bash"
                return {"language": language, "code": code}

        # Look for simple code execution patterns
        code_patterns = [
            r'run\s+(.+)',
            r'execute\s+(.+)',
            r'eval\s+(.+)'
        ]

        for pattern in code_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                code = match.group(1).strip()
                return {"language": "python", "code": code}

        return None

# FastAPI app
app = FastAPI(
    title="Chappy Brain Cluster API",
    description="REST API for the Digital Cortex AGI system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the brain on startup."""
    initialize_brain()

@app.post("/api/v1/query", response_model=QueryResponse)
async def query_chappy(request: QueryRequest):
    """Process a query through Chappy's brain."""
    try:
        result = brain.process_query(
            request.query,
            request.max_memories,
            request.include_thoughts
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/status", response_model=StatusResponse)
async def get_status():
    """Get system status."""
    try:
        return brain.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/memories", response_model=MemoryResponse)
async def get_memories(limit: int = 10):
    """Get recent memories."""
    try:
        return brain.get_memories(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/feedback", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback on a response."""
    try:
        return brain.process_feedback(feedback)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/tools", response_model=ToolsResponse)
async def get_tools():
    """Get list of available tools."""
    try:
        if not brain.initialized:
            raise HTTPException(status_code=503, detail="Brain not initialized")

        tools = brain.motor_cortex.get_available_tools()
        return ToolsResponse(
            tools=[ToolInfo(name=t["name"], description=t["description"]) for t in tools],
            count=len(tools)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/tools/execute", response_model=ToolExecuteResponse)
async def execute_tool(request: ToolExecuteRequest):
    """Execute a specific tool."""
    try:
        if not brain.initialized:
            raise HTTPException(status_code=503, detail="Brain not initialized")

        import time
        start_time = time.time()

        result = brain.motor_cortex.execute_with_tools(
            f"use {request.tool_name} tool",
            request.params
        )

        execution_time = time.time() - start_time

        return ToolExecuteResponse(
            tool_name=request.tool_name,
            success=result["result"]["status"] == "success",
            output=result["result"]["output"],
            error=result["result"]["error"],
            execution_time=execution_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Chappy Brain Cluster API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)