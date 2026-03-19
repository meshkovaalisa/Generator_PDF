from pathlib import Path
from processing_files.modules import unpack, pack_odp, pack_pptx, replace_placeholders

data = {
        "name": "Иван Петров",
        "score": "95"
    }

def handler_file(file):

    source = Path(file)

    if not source.exists():
        print("Файл не найден")
        return

    with open(source, "rb") as f:
        odp_bytes = f.read()

    if source.suffix == ".svg":
        replace_placeholders(Path(file), data)

    if source.suffix == ".pptx":
        unpack_dir = unpack(odp_bytes, source.name)

        slide_dir = unpack_dir / 'ppt' / 'slides'
        if slide_dir.exists():
            for xml_file in slide_dir.glob('*.xml'):
                replace_placeholders(xml_file, data)

        output_pptx = unpack_dir.parent / f"{source.stem}_modified.pptx"
        pack_pptx(unpack_dir, output_pptx)

    if source.suffix == ".odp":

        unpack_dir = unpack(odp_bytes, source.name)
        print(f"Распаковано в: {unpack_dir}")

        content_xml = unpack_dir / "content.xml"
        replace_placeholders(content_xml, data)


        output_odp = unpack_dir.parent / f"{source.stem}_modified.odp"  # например, temp/testfile_modified.odp
        pack_odp(unpack_dir, output_odp)
        print(f"Создан ODP: {output_odp}")


handler_file("testfile.svg")