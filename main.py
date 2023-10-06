import argparse
import shutil
import os
from string import ascii_letters, digits
from pathlib import Path
from threading import Thread
import logging

import py7zr


parser = argparse.ArgumentParser(description="Sorting folder")
parser.add_argument("--source", "-s", help="Source folder", required=True)

args = vars(parser.parse_args())
BASE_FOLDER = args.get("source")

CATEGORIES = {'archives': ('zip', 'gz', 'tar', '7z'),
            'audio': ('mp3', 'ogg', 'wav', 'amr', 'flac'),
            'documents': ('doc', 'docx', 'txt', 'pdf', 'xlsx', 'pptx', 'odt'),
            'images': ('jpeg', 'png', 'jpg', 'svg', 'webp'),
            'video': ('avi', 'mp4', 'mov', 'mkv'),
            'other': ()
            }

TRANSLITERATION = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ж': 'zh', 'з': 'z', 'и': 'y',
                'і': 'i', 'ї': 'yi', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p',
                'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh',
                'щ': 'shch', 'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'є': 'ye', 'ё': 'yo', 'ю': 'yu', 'я': 'ya',
                'Ё': 'Yo', 'Є': 'Ye', 'Ї': 'Yi', 'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E',
                'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'І': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N',
                'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'Ts',
                'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
                }

folders = []


def grabs_folder(path: Path) -> None:

    for el in path.iterdir():
        if el.is_dir():
            folders.append(el)
            grabs_folder(el)


def create_categories() -> None:

    for folder_name in CATEGORIES:
        if folder_name in os.listdir(BASE_FOLDER):
            continue
        folder_path = os.path.join(BASE_FOLDER, folder_name)
        try:
            os.makedirs(folder_path)
        except FileExistsError:
            os.rename(folder_path, os.path.join(BASE_FOLDER, folder_name.lower()))



def normalize(file_name: str) -> str:

    correct_characters = ascii_letters + digits + '_'
    file_name, extension = os.path.splitext(file_name)
    file_name = ''.join([char if char in correct_characters else TRANSLITERATION[char]
                        if char in TRANSLITERATION else '_'
                        for char in file_name])

    return file_name + extension


def check_name_conflict(folder_path: str, name: str) -> str:

    files = os.listdir(folder_path)

    if name not in files:
        return name

    filename, extension = os.path.splitext(name)
    counter = 1
    new_filename = f"{filename}_{counter}{extension}"

    while new_filename in files:
        counter += 1
        new_filename = f"{filename}_{counter}{extension}"

    return new_filename


def rename_file(destination_folder: str, full_file_path: str) -> str:

    file_name = os.path.basename(full_file_path)
    file_path = os.path.dirname(full_file_path)

    new_file_name = normalize(file_name)

    if new_file_name != file_name:
        new_file_name = check_name_conflict(file_path, new_file_name)
    new_file_name = check_name_conflict(destination_folder, new_file_name)

    new_full_file_path = os.path.join(file_path, new_file_name)

    os.rename(full_file_path, new_full_file_path)

    return new_full_file_path


def get_category_path(file_name: str) -> str:

        extension = os.path.splitext(file_name)[1].lower()[1:]

        if extension:
            for category, extensions in CATEGORIES.items():
                if extension in extensions:
                    category_path = os.path.join(BASE_FOLDER, category)

                    return category_path

        return os.path.join(BASE_FOLDER, 'other')


def move_files(folder) -> None:

    for entry in os.scandir(folder):
        if entry.is_file():
            category_path = get_category_path(entry.name)
            if str(folder) == category_path:
                continue

            try:
                new_full_file_path = rename_file(category_path, entry.path)
                shutil.move(new_full_file_path, category_path)
            except OSError as err:
                logging.error(err)


def delete_empty_folders() -> None:

    for root, dirs, files in os.walk(BASE_FOLDER, topdown=False):

        for directory in dirs:
            path = os.path.join(root, directory)

            if not os.listdir(path):
                os.rmdir(path)

def unpack_archive(file, archives) -> None:

        if os.path.splitext(file)[1][1:] in CATEGORIES['archives']:

            file_path = os.path.join(archives, file)

            if os.path.splitext(file)[1][1:] == '7z':
                with py7zr.SevenZipFile(file_path, mode='r') as z:
                    z.extractall(path=archives)
            else:
                shutil.unpack_archive(file_path, archives)

            os.remove(file_path)



def disassemble_junk() -> None:

    grabs_folder(Path(BASE_FOLDER))
    folders.append(Path(BASE_FOLDER))
    create_categories()


    threads = []
    for folder in folders:
        th = Thread(target=move_files, args=(folder,))
        th.start()
        threads.append(th)
    [th.join() for th in threads]
    print("Files have been sorted")

    delete_empty_folders()

    if os.path.exists(os.path.join(BASE_FOLDER, 'archives')):
        threads.clear()
        archives = os.path.join(BASE_FOLDER, 'archives')
        for file in os.listdir(archives):
            th = Thread(target=unpack_archive, args=(file, archives))
            th.start()
            threads.append(th)
        [th.join() for th in threads]
        print("Archives have been unpacked")




if __name__ == '__main__':
    
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")

    disassemble_junk()

    print("Sorting folder", BASE_FOLDER, "completed.")