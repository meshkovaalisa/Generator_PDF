import subprocess
from pathlib import Path

from config import soffice_path
def convert_file_to_pdf(file_path, output_dir):

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
    print(pdf_file_path, pdf_file_path.name)
    return pdf_file_path



