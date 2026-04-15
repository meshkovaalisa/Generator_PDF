import uvicorn, json, httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from processing_files.handler import split_by_faculty, odp_handler
from config import temp_dir, rendered_files_dir, faculties_dir, templates_dir
from processing_files.clean_tempfiles import clean_dir, delete_file
from processing_files.convert_to_pdf import convert_file_to_pdf
from processing_files.modules import FacultyRequest
from contextlib import asynccontextmanager
from processing_files.filter_json import filter_data
from fastapi import HTTPException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения FastAPI.

    Выполняет инициализацию при запуске (создание необходимых директорий,
    загрузка данных с внешнего API, обработка и распределение данных по факультетам)
    и очистку временных файлов при остановке сервера.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI

    Raises:
        HTTPException: 504 - таймаут подключения к API
        HTTPException: 4xx/5xx - ошибки при запросе к API или внутренние ошибки

    Yields:
        None: Передаёт управление основному приложению после инициализации
    """
    temp_dir.mkdir(parents=True, exist_ok=True)
    rendered_files_dir.mkdir(parents=True, exist_ok=True)
    faculties_dir.mkdir(parents=True, exist_ok=True)

    print(f"✅ temp_dir: {temp_dir}")
    print(f"✅ rendered_files_dir: {rendered_files_dir}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get("https://mauniver.ru/api/get_programms.php")
            response.raise_for_status()
            data = response.json()


    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Таймаут запроса к API")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Ошибка API")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")

    split_by_faculty(data)

    yield

    clean_dir(temp_dir)
    clean_dir(rendered_files_dir)
    clean_dir(faculties_dir)


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
    file_path = "static/index.html"

    with open(file_path, 'r', encoding="utf-8") as file:
        html_content = file.read()

    return HTMLResponse(content=html_content)


@app.post("/render")
async def render_faculty(request: FacultyRequest):
    """
    Генерирует PDF-документ для указанного факультета.

    Загружает данные факультета из JSON-файла, фильтрует образовательные программы
    по уровням образования (бакалавриат/специалитет и магистратура/аспирантура),
    обрабатывает ODP-шаблон, конвертирует его в PDF и возвращает готовый файл.

    Args:
        request (FacultyRequest): Объект запроса, содержащий название факультета

    Returns:
        FileResponse: PDF-файл с заполненным шаблоном для указанного факультета

    Raises:
        HTTPException: 404 - если факультет с указанным именем не найден
    """
    faculty_name = request.faculty_name

    file_path = faculties_dir / f"{faculty_name}.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Факультет '{faculty_name}' не найден")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    undergraduate_education = [filter_data(item) for item in data if
                               item.get("education") == "Бакалавриат" or item.get("education") == "Специалитет"]
    postgraduate_education = [filter_data(item) for item in data if
                              item.get("education") == "Магистратура" or item.get("education") == "Аспирантура"]

    all_education = undergraduate_education + postgraduate_education

    temp_odp_path, temp_unpacked_path = odp_handler(templates_dir/ f"{faculty_name}.odp", all_education)

    complete_file_path = convert_file_to_pdf(temp_odp_path, rendered_files_dir)

    delete_file(temp_odp_path)
    clean_dir(temp_unpacked_path)

    return FileResponse(
        complete_file_path,
        media_type="application/pdf",
        filename=complete_file_path.name
    )


@app.get("/faculties")
async def get_faculties_list():
    """
    Возвращает список всех доступных факультетов.

    Сканирует директорию с JSON-файлами факультетов и извлекает названия
    из имён файлов (без расширения).

    Returns:
        dict: Словарь с ключом "faculties", содержащий отсортированный
              список названий факультетов
    """
    faculties = []

    for file_path in faculties_dir.glob("*.json"):
        faculties.append(file_path.stem)  # берём имя без расширения

    return {"faculties": sorted(faculties)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)