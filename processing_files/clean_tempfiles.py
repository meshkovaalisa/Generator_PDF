from pathlib import Path
import shutil


def clean_dir(dir_path: Path):
    """
    Полностью очищает указанную директорию и удаляет её саму.

    Функция удаляет все содержимое директории (как файлы, так и поддиректории),
    после чего удаляет саму директорию.

    Args:
        dir_path (Path): Путь к директории, которую необходимо очистить и удалить
    """
    if dir_path.exists():
        for item in dir_path.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                # если внутри есть подпапки, их тоже удаляем рекурсивно
                shutil.rmtree(item)
        dir_path.rmdir()


def delete_file(file_path: Path):
    """
    Удаляет указанный файл, если он существует.

    Args:
        file_path (Path): Путь к файлу, который необходимо удалить
    """
    if file_path.is_file():
        file_path.unlink()