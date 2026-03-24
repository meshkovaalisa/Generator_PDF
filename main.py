import uvicorn, json
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from processing_files.handler import handler_file
from config import temp_dir, rendered_files_dir
from processing_files.clean_temp import clean_temp_dir
from processing_files.convert_to_pdf import convert_file_to_pdf

app = FastAPI()

@app.post("/render_files")
async def render(template: UploadFile, data: UploadFile):

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
        raise HTTPException(400, "Invalid JSON data")

    modificated_file_path = handler_file(filename_in_dir,json_data)

    complete_file_path = convert_file_to_pdf(modificated_file_path, rendered_files_dir)

    clean_temp_dir(temp_dir)

    return FileResponse(
        complete_file_path,
        media_type="application/pdf",
        filename=complete_file_path.name
    )

if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)