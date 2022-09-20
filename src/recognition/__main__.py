import uvicorn
from recognition.settings import settings

uvicorn.run(
    'recognition.app:app',
    host=settings.server_host,
    port=settings.server_port,
    reload=True,
)
