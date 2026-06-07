from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import sys
import tempfile
import os

app = FastAPI()

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define what the request body looks like
class CodeRequest(BaseModel):
    code: str

@app.get("/")
def root():
    return {"message": "Python Compiler API is running!"}

@app.post("/run")
def run_code(request: CodeRequest):
    try:
        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(request.code)
            temp_file = f.name

        # Run the file using Python
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Delete the temp file after running
        os.unlink(temp_file)

        return {
            "output": result.stdout,
            "error": result.stderr,
            "success": result.returncode == 0
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Code timed out after 10 seconds",
            "success": False
        }
    except Exception as e:
        return {
            "output": "",
            "error": str(e),
            "success": False
        }