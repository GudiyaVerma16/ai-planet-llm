from fastapi import APIRouter
from typing import Dict, List

router = APIRouter()

@router.get("")
@router.get("/types")
async def get_component_types():
    """Get available component types and their configurations"""
    return {
        "components": [
            {
                "type": "userQuery",
                "name": "User Query",
                "description": "Accepts user queries via a simple interface",
                "configurable": False,
                "inputs": [],
                "outputs": ["query"]
            },
            {
                "type": "knowledgeBase",
                "name": "Knowledge Base",
                "description": "Upload and process documents, retrieve relevant context",
                "configurable": True,
                "config_fields": [
                    {
                        "name": "document_ids",
                        "type": "array",
                        "label": "Select Documents",
                        "required": False
                    },
                    {
                        "name": "top_k",
                        "type": "number",
                        "label": "Top K Results",
                        "default": 5,
                        "required": False
                    }
                ],
                "inputs": ["query"],
                "outputs": ["context"]
            },
            {
                "type": "webSearch",
                "name": "Web Search",
                "description": "Search the web for relevant information",
                "configurable": False,
                "inputs": ["query"],
                "outputs": ["context"]
            },
            {
                "type": "llmEngine",
                "name": "LLM Engine",
                "description": "Generate responses using OpenAI GPT or Gemini",
                "configurable": True,
                "config_fields": [
                    {
                        "name": "provider",
                        "type": "select",
                        "label": "LLM Provider",
                        "options": ["openai", "gemini"],
                        "default": "openai",
                        "required": True
                    },
                    {
                        "name": "model",
                        "type": "select",
                        "label": "Model",
                        "options": {
                            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
                            "gemini": ["gemini-pro", "gemini-pro-vision"]
                        },
                        "default": "gpt-3.5-turbo",
                        "required": True
                    },
                    {
                        "name": "custom_prompt",
                        "type": "textarea",
                        "label": "Custom Prompt (Optional)",
                        "required": False
                    },
                    {
                        "name": "use_web_search",
                        "type": "checkbox",
                        "label": "Use Web Search",
                        "default": False,
                        "required": False
                    }
                ],
                "inputs": ["query", "context"],
                "outputs": ["response"]
            },
            {
                "type": "output",
                "name": "Output",
                "description": "Displays the final response to the user",
                "configurable": False,
                "inputs": ["response"],
                "outputs": []
            }
        ]
    }
