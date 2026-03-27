import uvicorn, json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from processing_files.handler import handler_file
from config import temp_dir, rendered_files_dir
from processing_files.clean_temp import clean_temp_dir
from processing_files.convert_to_pdf import convert_file_to_pdf
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Код ДО yield выполняется при запуске (startup).
    Код ПОСЛЕ yield выполняется при остановке (shutdown).
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    rendered_files_dir.mkdir(parents=True, exist_ok=True)

    print(f"✅ temp_dir: {temp_dir}")
    print(f"✅ rendered_files_dir: {rendered_files_dir}")

    yield

    clean_temp_dir(temp_dir)


app = FastAPI(title="Document Template Processor",
    description="Сервис для заполнения шаблонов документами и конвертации в PDF",
    version="1.0.0",
    lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index() -> HTMLResponse:
    """
    Рендер главной страницы

    Returns:
        HTMLResponse: экземпляр класса с наполненнием .html
    """
    file_path = "index.html"

    with open(file_path, 'r', encoding="utf-8") as file:
        html_content = file.read()

    return HTMLResponse(content=html_content)


@app.post("/render_files")
async def render(template: UploadFile, data: UploadFile) -> FileResponse:
    """
    Обработка шаблона форматов .odp, .pptx, .svg данными и заполнение данными из файла .json

    Args:
        template (UploadFile): шаблон формата .svg, .odp, .pptx
        data (UploadFile): шаблон формата .json

    Returns:
        FileResponse: экземпляр класса для отправки с сервера клиенту результирующего файла
    """
    if not template.filename.endswith(('.pptx', '.odp', '.svg')):
        raise HTTPException(400, "Неправильный формат файла. Используйте .pptx, .odp or .svg")

    if not data.filename.endswith('json'):
        raise HTTPException(400, "Неправильный формат файла. Используйте .json")

    filename_in_dir = "temp_" + template.filename

    with open(f"{temp_dir / filename_in_dir}", "wb") as f:
        f.write(template.file.read())

    content = await data.read()

    try:
        json_data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(400, "Невалидная JSON-дата")

    modificated_file_path = handler_file(filename_in_dir, json_data)

    complete_file_path = convert_file_to_pdf(modificated_file_path, rendered_files_dir)

    return FileResponse(
        complete_file_path,
        media_type="application/pdf",
        filename=complete_file_path.name
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
