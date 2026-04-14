import subprocess
from pathlib import Path

def convert_file_to_pdf(file_path, output_dir):
    file_path = Path(file_path)
    output_dir = Path(output_dir)
    pdf_file_path = output_dir / f"{file_path.stem}.pdf"
    
    # Исправленная команда (без --interface)
    command = [
        'unoconvert',
        '--host-location', 'remote',
        '--port', '2003',
        '--host', '127.0.0.1',  # вместо --interface
        str(file_path),
        str(pdf_file_path)
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"STDERR: {result.stderr}")
        print(f"STDOUT: {result.stdout}")
        raise subprocess.CalledProcessError(result.returncode, command)
    
    return pdf_file_path
