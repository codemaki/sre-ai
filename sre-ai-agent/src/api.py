"""FastAPI server for Jenkins AI Agent"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.agent import JenkinsAgent
from src.config import settings
from src.llm_client import LLMClient
from src.mcp_client import MCPClient

logger = logging.getLogger(__name__)

# Global agent instance
agent: Optional[JenkinsAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global agent

    # Startup
    logger.info("Initializing Jenkins AI Agent...")
    mcp_client = MCPClient(
        base_url=settings.jenkins_mcp_url,
        auth_token=settings.jenkins_mcp_token,
    )

    llm_client = LLMClient(
        api_key=settings.azure_openai_api_key,
        azure_endpoint=settings.azure_openai_endpoint,
        api_version=settings.azure_openai_api_version,
        deployment=settings.azure_openai_deployment,
    )

    agent = JenkinsAgent(mcp_client, llm_client)
    await agent.initialize()
    logger.info("Jenkins AI Agent initialized successfully")

    yield

    # Shutdown
    logger.info("Shutting down Jenkins AI Agent...")


# Create FastAPI app
app = FastAPI(
    title="Jenkins AI Agent API",
    description="API for controlling Jenkins via natural language using MCP and Azure OpenAI",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    """Chat request model"""

    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""

    response: str
    session_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model"""

    status: str
    agent_ready: bool


# API Endpoints
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        agent_ready=agent is not None,
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint for non-streaming responses

    Example:
    ```
    curl -X POST http://localhost:8000/api/chat \
      -H "Content-Type: application/json" \
      -d '{"message": "Jenkins 상태 알려줘"}'
    ```
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        response = await agent.process_message(request.message)
        return ChatResponse(
            response=response,
            session_id=request.session_id,
        )
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Chat endpoint with Server-Sent Events (SSE) streaming

    Example:
    ```
    curl -N -X POST http://localhost:8000/api/chat/stream \
      -H "Content-Type: application/json" \
      -d '{"message": "helloai 배포해줘"}'
    ```
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    async def event_generator():
        """Generate SSE events"""
        try:
            async for chunk in agent.process_message_with_streaming(request.message):
                # SSE format: data: <content>\n\n
                yield f"data: {chunk}\n\n"
        except Exception as e:
            logger.error(f"Error in streaming: {e}", exc_info=True)
            yield f"data: [오류: {str(e)}]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
        },
    )


@app.post("/api/reset")
async def reset_conversation(session_id: Optional[str] = None):
    """
    Reset conversation history

    Example:
    ```
    curl -X POST http://localhost:8000/api/reset
    ```
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        agent.llm_client.reset_conversation()
        return {"status": "success", "message": "Conversation history reset"}
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Jenkins AI Agent API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
