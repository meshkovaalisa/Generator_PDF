from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from config import settings
from services import file_service

app = FastAPI(title="File Upload")
templates = Jinja2Templates(directory=str(settings.TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    files = file_service.get_all_files()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "files": files,
        "allowed_formats": ", ".join(settings.ALLOWED_EXTENSIONS)
    })

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(request: Request, file: UploadFile = File(...)):
    try:
        await file_service.save_file(file)
        return templates.TemplateResponse("index.html", {
            "request": request,
            "files": file_service.get_all_files(),
            "allowed_formats": ", ".join(settings.ALLOWED_EXTENSIONS),
            "message": f"Файл '{file.filename}' загружен",
            "message_type": "success"
        })
    except HTTPException as e:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "files": file_service.get_all_files(),
            "allowed_formats": ", ".join(settings.ALLOWED_EXTENSIONS),
            "message": e.detail,
            "message_type": "error"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)