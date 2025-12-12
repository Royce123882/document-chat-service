"""
Development server entry point.

This script provides a convenient way to run the FastAPI application during
development with auto-reload enabled. For production deployments, use a
production ASGI server like Gunicorn with Uvicorn workers.

Usage:
    python3 server.py

Note:
    The server configuration (host, port, reload) can be customized in
    app/config.py via environment variables.
"""

import uvicorn

if __name__ == "__main__":
    # Run with auto-reload for development
    # In production, use: gunicorn app.main:app -k uvicorn.workers.UvicornWorker
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,        # Default development port
        reload=True       # Auto-reload on code changes (dev only)
    )
