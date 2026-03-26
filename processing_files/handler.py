import shutil
from pathlib import Path
from processing_files.modules import unpack, pack_odp, pack_pptx, replace_placeholders, svg
from config import temp_dir

def handler_file(file,data, output_file = None):

    source = Path(temp_dir/file)

    if not source.exists():
        print("Файл не найден")
        return

    with open(source, "rb") as f:
        odp_bytes = f.read()

    if source.suffix == ".svg":
        svg(source, data)
        output_file = source.parent / f"{source.stem}.svg"
        print(output_file)


    if source.suffix == ".pptx":
        unpack_dir = unpack(odp_bytes, source.name)

        slide_dir = unpack_dir / 'ppt' / 'slides'
        if slide_dir.exists():
            for xml_file in slide_dir.glob('*.xml'):
                replace_placeholders(xml_file, data)

        output_file = unpack_dir.parent / f"{source.stem}.pptx"
        pack_pptx(unpack_dir, output_file)

    if source.suffix == ".odp":

        unpack_dir = unpack(odp_bytes, source.name)

        content_xml = unpack_dir / "content.xml"
        replace_placeholders(content_xml, data)


        output_file = unpack_dir.parent / f"{source.stem}.odp"
        pack_odp(unpack_dir, output_file)

    print(output_file)
    return output_file
