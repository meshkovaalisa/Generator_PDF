# converter.py
import subprocess
import sys
from pathlib import Path


class PDFConverter:
    """Конвертер файлов в PDF через LibreOffice"""

    def __init__(self):
        self.soffice = self._find_libreoffice()
        print(f"✓ LibreOffice найден: {self.soffice}")

    def _find_libreoffice(self):
        """Поиск LibreOffice в системе"""

        # Стандартные пути для разных ОС
        if sys.platform == 'win32':
            paths = [
                r'C:\Program Files\LibreOffice\program\soffice.exe',
                r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
                r'C:\Program Files\LibreOffice 7\program\soffice.exe',
                r'C:\Program Files\LibreOffice 24\program\soffice.exe',
            ]
        elif sys.platform == 'darwin':  # macOS
            paths = [
                '/Applications/LibreOffice.app/Contents/MacOS/soffice',
                '/usr/local/bin/soffice',
            ]
        else:  # Linux
            paths = [
                '/usr/bin/soffice',
                '/usr/local/bin/soffice',
                '/snap/bin/libreoffice.soffice',
            ]

        # Проверка путей
        for path in paths:
            if Path(path).exists():
                return path

        # Проверка через PATH
        try:
            subprocess.run(['soffice', '--version'],
                           capture_output=True, check=True, timeout=5)
            return 'soffice'
        except:
            pass

        raise RuntimeError(
            "❌ LibreOffice не найден!\n\n"
            "Установите LibreOffice:\n"
            "• Windows: https://www.libreoffice.org/download/download/\n"
            "• Linux: sudo apt install libreoffice\n"
            "• macOS: brew install --cask libreoffice\n\n"
            "После установки перезапустите скрипт."
        )

    def convert(self, input_file, output_file=None):
        """
        Конвертация файла в PDF

        Args:
            input_file: Путь к файлу (.pptx, .odp, .svg, .docx, .xlsx и др.)
            output_file: Путь для PDF (необязательно)

        Returns:
            Path к созданному PDF файлу
        """

        input_file = Path(input_file).resolve()

        # Проверка существования файла
        if not input_file.exists():
            raise FileNotFoundError(f"❌ Файл не найден: {input_file}")

        # Проверка формата
        ext = input_file.suffix.lower()
        supported = ['.pptx', '.ppt', '.odp', '.ods', '.odt',
                     '.docx', '.doc', '.xlsx', '.xls', '.svg']
        if ext not in supported:
            raise ValueError(
                f"❌ Неподдерживаемый формат: {ext}\n"
                f"Поддерживаются: {', '.join(supported)}"
            )

        # Выходной файл
        if output_file is None:
            output_file = input_file.with_suffix('.pdf')
            output_dir = input_file.parent
        else:
            output_file = Path(output_file).resolve()
            output_dir = output_file.parent
            output_dir.mkdir(parents=True, exist_ok=True)

        print(f"🔄 Конвертация: {input_file.name} → {output_file.name}")

        # Команда LibreOffice
        cmd = [
            self.soffice,
            '--headless',  # Без GUI
            '--convert-to', 'pdf',  # Конвертация в PDF
            '--outdir', str(output_dir),  # Папка вывода
            str(input_file)  # Входной файл
        ]

        # Запуск конвертации
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 минут максимум
            )

            if result.returncode != 0:
                raise RuntimeError(f"Ошибка LibreOffice: {result.stderr}")

        except subprocess.TimeoutExpired:
            raise TimeoutError("⏱ Превышено время конвертации (5 минут)")

        # Поиск созданного файла
        default_pdf = input_file.with_suffix('.pdf')

        if default_pdf.exists():
            # Переименовываем если нужно
            if default_pdf != output_file:
                default_pdf.rename(output_file)
            print(f"✓ Готово: {output_file}")
            return output_file
        else:
            # Ищем PDF в папке вывода
            pdf_files = list(output_dir.glob(f"{input_file.stem}.pdf"))
            if pdf_files:
                pdf = pdf_files[0]
                if pdf != output_file:
                    pdf.rename(output_file)
                print(f"✓ Готово: {output_file}")
                return output_file
            else:
                raise RuntimeError("❌ PDF файл не создан")

    def convert_batch(self, files, output_dir=None):
        """Пакетная конвертация нескольких файлов"""

        if output_dir:
            output_dir = Path(output_dir).resolve()
            output_dir.mkdir(parents=True, exist_ok=True)

        results = []
        for file in files:
            try:
                out = output_dir / f"{Path(file).stem}.pdf" if output_dir else None
                pdf = self.convert(file, out)
                results.append({'file': file, 'pdf': str(pdf), 'status': 'success'})
                print()
            except Exception as e:
                results.append({'file': file, 'error': str(e), 'status': 'failed'})
                print(f"✗ {file}: {e}\n")

        # Статистика
        success = sum(1 for r in results if r['status'] == 'success')
        print(f"=" * 50)
        print(f"📊 Итого: {success}/{len(results)} успешно")

        return results


# ==================== ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ ====================

if __name__ == "__main__":
    # Инициализация конвертера
    converter = PDFConverter()

    print("=" * 50)
    print("📝 Конвертер файлов в PDF")
    print("Поддерживаются: .pptx, .odp, .svg, .docx, .xlsx")
    print("=" * 50)
    print()

    # Вариант 1: Конвертация одного файла
    converter.convert("data/test.odp", "res/res.pdf")

    # Вариант 2: Автоматическое имя выходного файла
    # converter.convert("templates/document.odp")

    # Вариант 3: Пакетная конвертация
    # files = [
    #     "templates/slide1.pptx",
    #     "templates/slide2.odp",
    #     "templates/image.svg"
    # ]
    # converter.convert_batch(files, output_dir="output/")

    # Вариант 4: Из командной строки
    # if len(sys.argv) > 1:
    #     input_file = sys.argv[1]
    #     output_file = sys.argv[2] if len(sys.argv) > 2 else None
    #     converter.convert(input_file, output_file)
    # else:
    #     print("\n💡 Использование:")
    #     print("  python converter.py файл.pptx [выход.pdf]")
    #     print("\n  Или отредактируйте этот файл для своих задач")