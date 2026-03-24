from pathlib import Path
import shutil

def clean_temp_dir(temp_path: Path):
    if temp_path.exists():
        for item in temp_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                # если внутри есть подпапки, их тоже удаляем рекурсивно
                shutil.rmtree(item)
