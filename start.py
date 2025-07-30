import os
import glob
from pathlib import Path

def get_bat_files(folder):
    return glob.glob(os.path.join(folder, "*.bat"))

def create_vbs_script(bat_file):
    vbs_content = f"""
Set WShell = CreateObject("WScript.Shell")
WShell.Run Chr(34) & "{bat_file}" & Chr(34), 0
Set WShell = Nothing
"""
    vbs_file = os.path.splitext(bat_file)[0] + ".vbs"
    with open(vbs_file, "w") as f:
        f.write(vbs_content)
    return vbs_file

def main():
    folder = "pre-configs"
    if not os.path.exists(folder):
        print(f"Папка {folder} не найдена, дебил!")
        return

    bat_files = get_bat_files(folder)
    if not bat_files:
        print(f"В папке {folder} нет ни одного .bat файла, хуйня какая-то!")
        return

    print("Найдены следующие .bat файлы:")
    for i, bat in enumerate(bat_files, 1):
        print(f"{i}. {os.path.basename(bat)}")

    try:
        choice = int(input("Выбери номер батника, бери нормальный: ")) - 1
        if choice < 0 or choice >= len(bat_files):
            print("Ты чё, дебил? Номер не валидный!")
            return
    except ValueError:
        print("Введи число, дебил, а не хуйню какую-то!")
        return

    selected_bat = bat_files[choice]
    vbs_file = create_vbs_script(selected_bat)
    print(f"Создан VBS файл: {vbs_file}")
    os.startfile(vbs_file)

if __name__ == "__main__":
    main()