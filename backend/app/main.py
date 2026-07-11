# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import router  # FIXED: Import from api.routes

app = FastAPI(
    title="SentinelOS API",
    version="1.0.0",
    description="AI Security Operating System with Chat, Analysis, and Analytics"
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router)

# Root endpoint
@app.get("/")
def root():
    return {
        "service": "SentinelOS",
        "version": "1.0.0",
        "endpoints": {
            "chat": {
                "POST": "/chat - General Q&A",
                "GET": "/chat/history - Get chat history",
                "DELETE": "/chat/history - Clear chat history"
            },
            "security": {
                "POST": "/analyze - Full security analysis"
            },
            "audit": {
                "GET": "/history - Get audit history",
                "GET": "/history/{id} - Get specific log",
                "DELETE": "/history - Clear history"
            },
            "analytics": {
                "GET": "/analytics - Comprehensive analytics",
                "GET": "/analytics/daily - Daily analytics",
                "GET": "/analytics/trends - Trend analysis"
            },
            "stats": {
                "GET": "/stats - Database statistics"
            },
            "search": {
                "GET": "/search?query= - Search logs"
            },
            "docs": {
                "GET": "/docs - API Documentation"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )