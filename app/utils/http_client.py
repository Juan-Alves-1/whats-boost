import time
import httpx
from app.utils.logger import logger

def _on_request(request):
    request.extensions["start_time"] = time.time()
    logger.debug(f"→ {request.method} {request.url}")

def _on_response(response):
    elapsed = time.time() - response.request.extensions["start_time"]
    logger.info(f"← {response.status_code} {response.url} in {elapsed:.2f}s")

evo_client = httpx.Client(
    http2=False, 
    timeout=httpx.Timeout(
        connect=10.0,   
        read=60.0,      # Allow EVO enough time to respond
        write=10.0,
        pool=10.0
    ),
    limits=httpx.Limits(
        max_connections=25,          # Total concurrent connections
        max_keepalive_connections=10  # Connections to keep in pool for reuse
    ),
    event_hooks={"request": [_on_request], "response": [_on_response]},
    trust_env=False,
)

media_validation_client = httpx.Client(
    http2=True,  
    timeout=httpx.Timeout(
        connect=5.0,
        read=30.0,  
        write=30.0,
        pool=10.0
    ),
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=2
    ),
    event_hooks={"request": [_on_request], "response": [_on_response]},
    trust_env=False,
)

url_shortener_client = httpx.Client(
    http2=False,  
    timeout=httpx.Timeout(
        connect=5.0,
        read=30.0,  
        write=30.0,
        pool=10.0
    ),
    limits=httpx.Limits(
        max_connections=10,
        max_keepalive_connections=2
    ),
    event_hooks={"request": [_on_request], "response": [_on_response]},
    trust_env=False,
)
