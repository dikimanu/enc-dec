#python -m uvicorn app.main:app --reload

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import shutil, os, uuid
from app.security import encrypt_file, decrypt_file  # absolute import

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def process_files(
    request: Request,
    action: str = Form(...),
    files: list[UploadFile] = File(...)
):
    results = []

    for file in files:
        temp_input = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")
        temp_output = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{file.filename}")

        with open(temp_input, "wb") as f:
            shutil.copyfileobj(file.file, f)

        try:
            if action == "encrypt":
                encrypt_file(temp_input, temp_output)
            else:
                decrypt_file(temp_input, temp_output)

            results.append({
                "original_name": file.filename,
                "processed_filename": os.path.basename(temp_output)
            })

        except Exception as e:
            results.append({
                "original_name": file.filename,
                "error": str(e)
            })

        finally:
            os.remove(temp_input)

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "results": results}
    )

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
