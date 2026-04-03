import uvicorn, json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from processing_files.handler import handler_file
from config import temp_dir, rendered_files_dir
from processing_files.clean_temp import clean_temp_dir
from processing_files.convert_to_pdf import convert_file_to_pdf
from contextlib import asynccontextmanager
from config import *
import aiofiles
import hashlib

from processing_files.modules import zip_and_save


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

app.mount("/static", StaticFiles(directory="static"), name="static")


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

    template_bytes = template.file.read()
    template.file.seek(0)

    file_hash = hashlib.md5(template_bytes).hexdigest()
    (rendered_files_dir / file_hash).mkdir(exist_ok=True)
    new_folder = rendered_files_dir / file_hash

    for file in depart_info.iterdir():
        if file.is_file() and file.suffix == ".json":
            filename_in_dir = f"temp_{file.stem}_{template.filename}"
            temp_path = temp_dir / filename_in_dir

            async with aiofiles.open(temp_path, "wb") as f:
                await f.write(template_bytes)

            async with aiofiles.open(file, "r", encoding="utf-8") as f:
                content = await f.read()

            try:
                json_data = json.loads(content)
            except json.JSONDecodeError as e:
                raise HTTPException(400, f"Invalid JSON in {file.name}: {e}")

            modificated_file_path = handler_file(filename_in_dir, json_data)
            complete_file_path = convert_file_to_pdf(modificated_file_path, new_folder)
    zip_arh = zip_and_save(new_folder, rendered_files_dir)

    """filename_in_dir = "temp_" + template.filename

    with open(f"{temp_dir / filename_in_dir}", "wb") as f:
        f.write(template.file.read())

    content = await data.read()

    try:
        json_data = json.loads(content.decode('utf-8'))
    except json.JSONDecodeError:
        raise HTTPException(400, "Невалидная JSON-дата")

    modificated_file_path = handler_file(filename_in_dir, json_data)

    complete_file_path = convert_file_to_pdf(modificated_file_path, rendered_files_dir)
"""
    return FileResponse(
        zip_arh,
        media_type="application/zip",
        filename=zip_arh.name
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
