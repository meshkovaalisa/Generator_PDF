from pathlib import Path
import shutil

def clean_dir(dir_path: Path):
    if dir_path.exists():
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                # если внутри есть подпапки, их тоже удаляем рекурсивно
                shutil.rmtree(item)
        dir_path.rmdir()

def delete_file(file_path: Path):
    if file_path.is_file():
        file_path.unlink()

