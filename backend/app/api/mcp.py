from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict, List
from app.mcp.tools import execute_tool, list_tools
from app.core.deps import get_current_active_user
from app.models.user import User as UserModel
from app.services.llm_service import llm_service

router = APIRouter()


@router.get("/tools", response_model=List[Dict[str, str]])
async def list_mcp_tools(current_user: UserModel = Depends(get_current_active_user)):
    """List all available MCP tools."""
    return list_tools()


@router.post("/execute", response_model=Dict[str, Any])
async def execute_mcp_tool(
    tool_name: str,
    kwargs: Dict[str, Any] = None,
    current_user: UserModel = Depends(get_current_active_user)
):
    """Execute an MCP tool."""
    if kwargs is None:
        kwargs = {}
    
    result = execute_tool(tool_name, **kwargs)
    
    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return result


@router.get("/azure-ai-test", response_model=Dict[str, Any])
async def azure_ai_test(current_user: UserModel = Depends(get_current_active_user)):
    """Run a lightweight Azure OpenAI connectivity test."""
    try:
        result = llm_service.ping()
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
