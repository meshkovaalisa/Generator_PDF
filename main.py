from modules_odp.modules import unpack_odp
from modules_odp.modules import pack_odp
from pathlib import Path



def main():
    odp_data = open("modules_odp/testfile.odp", "rb").read()
    folder = unpack_odp(odp_data, "testfile.odp")
    print(f"Распаковано в: {folder}")

    output_dir = Path("temp/newtestodp")
    output_dir.mkdir(exist_ok=True)


    output_odp = output_dir / "kiki.odp"

    pack_odp(folder,output_odp)



if __name__ == "__main__":
    main()




