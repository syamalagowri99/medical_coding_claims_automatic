from app.core.config import settings
print("AZURE_ENDPOINT_SET", bool(settings.AZURE_OPENAI_ENDPOINT))
print("AZURE_API_KEY_SET", bool(settings.AZURE_OPENAI_API_KEY))
print("AZURE_DEPLOYMENT", settings.AZURE_OPENAI_DEPLOYMENT_NAME)
from app.services.llm_service import llm_service
print("llm_is_azure", llm_service.is_azure)
print("model", getattr(llm_service, "model", None))
import json, traceback
try:
    r = llm_service.ping()
    print("PING_OK", bool(r.get("response")), r.get("model"), r.get("azure_enabled"))
    print("PING_RESP_PREVIEW", str(r.get("response"))[:200])
except Exception as e:
    print("PING_ERR", type(e).__name__, str(e)[:500])
    traceback.print_exc()
