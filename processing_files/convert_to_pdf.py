import subprocess
from pathlib import Path
import os

def convert_file_to_pdf(file_path, output_dir):
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    pdf_file_path = output_dir / f"{file_path.stem}.pdf"
    
    UNOSERVER_HOST = os.getenv("UNOSERVER_HOST", "unoserver-container")  
    UNOSERVER_PORT = os.getenv("UNOSERVER_PORT", "2003")

    command = [
        'unoconvert',
        '--host', UNOSERVER_HOST,  
        '--port', UNOSERVER_PORT,
        str(file_path),
        str(pdf_file_path)
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise subprocess.CalledProcessError(result.returncode, command)
    
    return pdf_file_path
