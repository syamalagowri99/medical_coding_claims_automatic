"""
MCP (Model Context Protocol) Tools for Medical Coding System
These tools can be used by LLMs to interact with the medical coding system.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.medical_code import MedicalCode, CodeSystem
from app.models.entity import ExtractedEntity, EntityType
from app.services.llm_service import llm_service


class CodeLookupTool:
    """Tool for looking up medical codes."""
    
    name = "code_lookup"
    description = "Look up ICD-10, CPT, or HCPCS codes by code number or description"
    
    def execute(self, code: str, code_system: str = "ICD-10") -> Dict[str, Any]:
        """
        Look up a medical code.
        
        Args:
            code: The medical code to look up
            code_system: The code system (ICD-10, CPT, HCPCS)
        
        Returns:
            Dictionary with code information
        """
        db: Session = SessionLocal()
        try:
            code_obj = db.query(MedicalCode).filter(
                MedicalCode.code == code,
                MedicalCode.code_system == CodeSystem(code_system)
            ).first()
            
            if code_obj:
                return {
                    "code": code_obj.code,
                    "description": code_obj.description,
                    "code_system": code_obj.code_system.value,
                    "status": code_obj.status.value
                }
            else:
                # Use LLM to get code information if not in database
                explanation = llm_service.explain_code(code, code_system)
                return {
                    "code": code,
                    "description": explanation,
                    "code_system": code_system,
                    "status": "external_lookup"
                }
        finally:
            db.close()


class ClaimValidationTool:
    """Tool for validating claims."""
    
    name = "claim_validation"
    description = "Validate a medical claim for errors and compliance issues"
    
    def execute(self, claim_id: int) -> Dict[str, Any]:
        """
        Validate a claim.
        
        Args:
            claim_id: The ID of the claim to validate
        
        Returns:
            Dictionary with validation results
        """
        db: Session = SessionLocal()
        try:
            from app.services.claim_service import validate_claim
            claim = validate_claim(db, claim_id)
            
            validations = []
            for v in claim.validations:
                validations.append({
                    "type": v.validation_type,
                    "is_valid": v.is_valid,
                    "error_message": v.error_message,
                    "severity": v.severity
                })
            
            return {
                "claim_id": claim.id,
                "claim_number": claim.claim_number,
                "status": claim.status.value,
                "validations": validations,
                "total_amount": claim.total_amount
            }
        finally:
            db.close()


class MedicalKnowledgeRetriever:
    """Tool for retrieving medical knowledge and coding guidelines."""
    
    name = "medical_knowledge_retriever"
    description = "Retrieve medical knowledge, coding guidelines, and best practices"
    
    def execute(self, query: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve medical knowledge.
        
        Args:
            query: The medical or coding query
            context: Optional clinical context for better results
        
        Returns:
            Dictionary with relevant medical knowledge
        """
        db: Session = SessionLocal()
        try:
            # Search for relevant entities in the database
            entities = db.query(ExtractedEntity).filter(
                ExtractedEntity.entity_text.ilike(f"%{query}%")
            ).limit(5).all()
            
            entity_info = []
            for entity in entities:
                entity_info.append({
                    "entity_type": entity.entity_type.value,
                    "entity_text": entity.entity_text,
                    "context": entity.context,
                    "confidence": entity.confidence_score
                })
            
            return {
                "query": query,
                "context": context,
                "found_entities": entity_info,
                "suggestion": f"Found {len(entity_info)} related entities in the database"
            }
        finally:
            db.close()


class EntityExtractionTool:
    """Tool for extracting medical entities from text."""
    
    name = "entity_extraction"
    description = "Extract medical entities (diagnoses, procedures, medications) from clinical text"
    
    def execute(self, text: str) -> Dict[str, Any]:
        """
        Extract entities from clinical text.
        
        Args:
            text: The clinical text to analyze
        
        Returns:
            Dictionary with extracted entities
        """
        try:
            entities = llm_service.extract_entities(text)
            return {
                "text_length": len(text),
                "entities": entities,
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class CodingSuggestionTool:
    """Tool for suggesting medical codes based on clinical text."""
    
    name = "coding_suggestion"
    description = "Suggest appropriate medical codes based on clinical documentation"
    
    def execute(self, text: str, code_system: str = "auto") -> Dict[str, Any]:
        """
        Suggest codes for clinical text.
        
        Args:
            text: The clinical text to analyze
            code_system: The code system to use (ICD-10, CPT, or auto-detect)
        
        Returns:
            Dictionary with suggested codes
        """
        try:
            # First extract entities
            entities = llm_service.extract_entities(text)
            
            suggestions = []
            
            # Suggest codes for each entity
            for diagnosis in entities.get("diagnoses", []):
                codes = llm_service.suggest_codes(diagnosis["text"], "diagnosis")
                for code in codes[:2]:  # Top 2 per diagnosis
                    suggestions.append({
                        "code": code["code"],
                        "description": code["description"],
                        "code_system": "ICD-10",
                        "confidence": code["confidence"],
                        "source_entity": diagnosis["text"]
                    })
            
            for procedure in entities.get("procedures", []):
                codes = llm_service.suggest_codes(procedure["text"], "procedure")
                for code in codes[:2]:  # Top 2 per procedure
                    suggestions.append({
                        "code": code["code"],
                        "description": code["description"],
                        "code_system": "CPT",
                        "confidence": code["confidence"],
                        "source_entity": procedure["text"]
                    })
            
            return {
                "text_length": len(text),
                "suggestions": suggestions,
                "total_suggestions": len(suggestions),
                "status": "success"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Registry of all MCP tools
MCP_TOOLS = {
    "code_lookup": CodeLookupTool(),
    "claim_validation": ClaimValidationTool(),
    "medical_knowledge_retriever": MedicalKnowledgeRetriever(),
    "entity_extraction": EntityExtractionTool(),
    "coding_suggestion": CodingSuggestionTool()
}


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """
    Execute an MCP tool by name.
    
    Args:
        tool_name: The name of the tool to execute
        **kwargs: Arguments to pass to the tool
    
    Returns:
        Dictionary with tool execution results
    """
    if tool_name not in MCP_TOOLS:
        return {
            "status": "error",
            "error": f"Tool '{tool_name}' not found. Available tools: {list(MCP_TOOLS.keys())}"
        }
    
    tool = MCP_TOOLS[tool_name]
    return tool.execute(**kwargs)


def list_tools() -> List[Dict[str, str]]:
    """List all available MCP tools."""
    return [
        {
            "name": tool.name,
            "description": tool.description
        }
        for tool in MCP_TOOLS.values()
    ]
