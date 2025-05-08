import httpx

shared_http_client = httpx.Client(
    http2=True, 
    timeout=httpx.Timeout(
        connect=10.0,   # Time to establish TCP connection
        read=45.0,      # Allow EVO enough time to respond
        write=10.0,
        pool=60.0
    ),
    limits=httpx.Limits(
        max_connections=100,          # Total concurrent connections
        max_keepalive_connections=20  # Connections to keep in pool for reuse
    )
)