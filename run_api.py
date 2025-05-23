import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath("."))

import uvicorn

if __name__ == "__main__":
    # Run the FastAPI app
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000, reload=True) 