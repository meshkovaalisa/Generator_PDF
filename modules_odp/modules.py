import zipfile
import io
import shutil
from pathlib import Path


def unpack_odp(odp_bytes: bytes, filename: str, temp_dir: str = "temp") -> Path:

    stem = Path(filename).stem  # "Извлекаем имя без расширения

    # Папка проекта / temp / имя_без_расширения
    base_path = Path(__file__).parent.parent / temp_dir
    base_path.mkdir(exist_ok=True)

    target_dir = base_path / stem


    # Если такая папка уже есть, удаляем её (чтобы не было мусора от предыдущих запусков)
    if target_dir.exists():
        shutil.rmtree(target_dir)

    # Создаём заново
    target_dir.mkdir()

    # Распаковываем архив
    with zipfile.ZipFile(io.BytesIO(odp_bytes), 'r') as zip_ref:
        zip_ref.extractall(target_dir)

    return target_dir

def pack_odp(unpack_dir: Path, output_odp_path: Path):

    with zipfile.ZipFile(output_odp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in unpack_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(unpack_dir)
                zipf.write(file_path, arcname)

