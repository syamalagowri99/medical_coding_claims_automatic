import inspect
from app.api.documents import upload_document

sig = inspect.signature(upload_document)
print('signature:', sig)
for name, param in sig.parameters.items():
    print(name, param.annotation, param.default, type(param.default))
