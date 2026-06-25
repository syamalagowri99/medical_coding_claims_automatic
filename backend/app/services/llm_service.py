import threading


def _apply_certifi_win32_patch_async():
    """Attempt to apply certifi_win32 patches in a background thread.

    This avoids blocking imports when the Win32 cert bundle generation
    takes time or holds OS-level locks.
    """
    try:
        import certifi
        from certifi_win32 import wrapt_certifi
        import shutil

        try:
            wrapt_certifi.apply_patches(certifi)
        except shutil.SameFileError:
            # Already applied / same file — nothing to do.
            pass
    except Exception:
        # Ignore any issues here; network calls will surface errors later.
        return


# Start patching asynchronously (daemon thread) so imports don't block.
try:
    _patch_thread = threading.Thread(target=_apply_certifi_win32_patch_async, daemon=True)
    _patch_thread.start()
except Exception:
    # If threading isn't available or fails, skip patching.
    pass

from openai import OpenAI, OpenAIError
from typing import List, Dict, Optional
from app.core.config import settings
import json


class LLMService:
    """Service for LLM-based medical coding and analysis."""
    
    def __init__(self):
        if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_API_KEY:
            azure_base_url = settings.AZURE_OPENAI_ENDPOINT
            azure_query = None
            if "/openai/v1" not in azure_base_url:
                azure_query = {"api-version": settings.AZURE_OPENAI_API_VERSION}

            self.client = OpenAI(
                api_key=settings.AZURE_OPENAI_API_KEY,
                base_url=azure_base_url,
                **({"default_query": azure_query} if azure_query else {}),
            )
            self.model = settings.AZURE_OPENAI_DEPLOYMENT_NAME or settings.OPENAI_MODEL
            self.embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME or settings.OPENAI_EMBEDDING_MODEL
            self.is_azure = True
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
            self.model = settings.OPENAI_MODEL
            self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
            self.is_azure = False
    
    def extract_entities(self, text: str) -> Dict:
        """Extract medical entities from clinical text."""
        prompt = f"""
You are a medical coding expert. Extract medical entities from the following clinical documentation.

Clinical Text:
{text}

Extract and return a JSON object with the following structure:
{{
    "diagnoses": [
        {{"text": "diagnosis name", "context": "relevant context", "confidence": 0.95}}
    ],
    "procedures": [
        {{"text": "procedure name", "context": "relevant context", "confidence": 0.90}}
    ],
    "medications": [
        {{"text": "medication name", "context": "relevant context", "confidence": 0.95}}
    ],
    "lab_tests": [
        {{"text": "lab test name", "context": "relevant context", "confidence": 0.90}}
    ]
}}

Only include entities that are clearly mentioned in the text. Provide confidence scores between 0.0 and 1.0.
"""
        
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        kwargs = {
            "model": self.model,
            "messages":[
                {"role": "system", "content": "You are a medical coding expert specializing in ICD-10, CPT, and HCPCS coding."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        response = self.client.chat.completions.create(**kwargs)
        
        return json.loads(response.choices[0].message.content)
    
    def suggest_codes(self, entity_text: str, entity_type: str) -> List[Dict]:
        """Suggest medical codes for an entity."""
        code_system = "ICD-10" if entity_type in ["diagnosis", "symptom"] else "CPT"
        
        prompt = f"""
You are a medical coding expert. Suggest appropriate {code_system} codes for the following medical entity.

Entity: {entity_text}
Type: {entity_type}

Return a JSON object with the following structure:
{{
    "suggested_codes": [
        {{
            "code": "code value",
            "description": "code description",
            "confidence": 0.95,
            "rationale": "brief explanation for why this code fits"
        }}
    ]
}}

Provide 3-5 most relevant codes with confidence scores between 0.0 and 1.0.
"""
        
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        kwargs = {
            "model": self.model,
            "messages":[
                {"role": "system", "content": "You are a medical coding expert specializing in ICD-10, CPT, and HCPCS coding."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "response_format": {"type": "json_object"}
        }
        response = self.client.chat.completions.create(**kwargs)
        
        result = json.loads(response.choices[0].message.content)
        return result.get("suggested_codes", [])
    
    def validate_claim(self, claim_data: Dict) -> Dict:
        """Validate a medical claim for errors and compliance issues."""
        prompt = f"""
You are a medical claims validation expert. Review the following claim data for errors, compliance issues, and potential denials.

Claim Data:
{json.dumps(claim_data, indent=2)}

Return a JSON object with the following structure:
{{
    "is_valid": true/false,
    "errors": [
        {{
            "type": "error type (e.g., coding, medical_necessity, documentation)",
            "severity": "error/warning/info",
            "message": "detailed error message",
            "suggestion": "how to fix the issue"
        }}
    ],
    "overall_score": 0.95,
    "summary": "brief summary of claim quality"
}}

Check for:
- Coding accuracy and specificity
- Medical necessity
- Documentation completeness
- Compliance with payer rules
- Common denial reasons
"""
        
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        kwargs = {
            "model": self.model,
            "messages":[
                {"role": "system", "content": "You are a medical claims validation expert."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"}
        }
        try:
            response = self.client.chat.completions.create(**kwargs)
        except OpenAIError as e:
            raise ValueError(f"LLM validation failed: {e}") from e
        
        return json.loads(response.choices[0].message.content)
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for text."""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        response = self.client.embeddings.create(
            model=self.embedding_model,
            input=text
        )
        
        return response.data[0].embedding
    
    def explain_code(self, code: str, code_system: str) -> str:
        """Get detailed explanation of a medical code."""
        prompt = f"""
Provide a detailed explanation of the following {code_system} code: {code}

Include:
- Code description
- When to use this code
- Documentation requirements
- Common errors or misuse
- Related codes
"""
        
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a medical coding expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        
        return response.choices[0].message.content

    def ping(self) -> Dict[str, str]:
        """Run a lightweight test call against the configured LLM."""
        if not self.client:
            raise ValueError("OpenAI API key not configured")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Reply with 'Azure OpenAI test successful.'"}
            ],
            temperature=0.0
        )

        return {
            "model": self.model,
            "azure_enabled": str(self.is_azure),
            "response": str(response.choices[0].message.content).strip()
        }


# Global LLM service instance
llm_service = LLMService()
