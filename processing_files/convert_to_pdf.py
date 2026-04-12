from unoserver.client import UnoClient
from pathlib import Path

def convert_file_to_pdf(file_path, output_dir):
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    pdf_file_path = output_dir / f"{file_path.stem}.pdf"
    
    # Подключаемся к серверу
    client = UnoClient(server='127.0.0.1', port=2003)
    
    # Правильные имена параметров: inpath и outpath
    client.convert(
        inpath=str(file_path),   # ← inpath, не infile!
        outpath=str(pdf_file_path)  # ← outpath, не outfile!
    )
    
    print(pdf_file_path, pdf_file_path.name)
    return pdf_file_path
