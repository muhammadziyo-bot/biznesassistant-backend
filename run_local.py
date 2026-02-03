import os
import sys
import uvicorn
from app.config import settings

# Force local database settings
os.environ["DATABASE_URL"] = "postgresql://postgres:rakhmonov@localhost:5432/biznes_assistant"

# Remove any Render environment variables that might override
render_vars = [var for var in os.environ.keys() if var.startswith('RENDER_') or 'DATABASE' in var.upper()]
for var in render_vars:
    del os.environ[var]
    print(f"Removed environment variable: {var}")

print(f"Using database URL: {os.environ.get('DATABASE_URL')}")
print("Starting local server...")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
