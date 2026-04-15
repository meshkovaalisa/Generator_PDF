import subprocess
from pathlib import Path
from typing import Union
from config import soffice_path


def convert_file_to_pdf(file_path: Union[str, Path], output_dir: Union[str, Path]) -> Path:
    """
    Конвертация файла в PDF формат с помощью LibreOffice.

    Args:
        file_path (Union[str, Path]): Путь к исходному файлу для конвертации
        output_dir (Union[str, Path]): Путь к директории для сохранения PDF

    Returns:
        Path: Путь к созданному PDF-файлу

    Raises:
        subprocess.CalledProcessError: Если процесс конвертации завершился с ошибкой
                                      (например, если файл не существует или повреждён)
    """

    file_path = Path(file_path)
    output_dir = Path(output_dir)

    command = [
        soffice_path,
        '--headless',
        '--convert-to', 'pdf',
        '--outdir', output_dir,
        file_path
    ]

    subprocess.run(command, check=True)

    pdf_file_path = output_dir / f"{file_path.stem}.pdf"

    return pdf_file_path