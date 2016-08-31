import os, sys, glob
import exifread

def make_cwd(args):
    """Составляет из аргументов командной строки путь к желаемому каталогу"""
    path = ""
    for i in range(1, len(args), 1):
        path += args[i]
        if i != len(args)-1:
            path += ' '
    return path

def process_directory(work_directory, file_type):
    """Принимает на вход каталог, возвращает список *.file_type файлов"""
    os.chdir(work_directory)
    return glob.glob("*." + file_type)

def make_data_pattern(date_time):
    """Принимает на вход дату и меняет её под шаблон"""
    date_time = date_time.replace(":", "")
    date_time = date_time.replace(" ", "_")
    date_time = "IMG_" + date_time
    return date_time

def process_photo(cur_photo, cwd):
    """Извлекает из фото exif-данные, на основе их переименовывает"""
    image = open(cur_photo, "rb")
    metadata = exifread.process_file(image)
    image.close()
    renamed = 0
    if 'EXIF DateTimeOriginal' in metadata:
        tag_value = metadata.get("EXIF DateTimeOriginal")
        dt_pattern = make_data_pattern(tag_value.printable)
        try:
            os.rename(cur_photo, dt_pattern + '.jpg')
            print(cur_photo + " -> " + dt_pattern+'.jpg')
        except FileExistsError:
            os.rename(cur_photo, dt_pattern + " (1)" + '.jpg')
            print(cur_photo + " -> " + dt_pattern  + " (1)" +  '.jpg')
        renamed = 1
    else:
        print(cur_photo + " -> " + "не переименовано")
    return renamed

def main():
    cwd_name = make_cwd(sys.argv)
    photos = process_directory(cwd_name, "jpg")
    print("Рабочий каталог: ", cwd_name)
    pr_pics = 0
    for photo in photos:
        pr_pics += process_photo(photo, cwd_name)
    print("\nВсего изображений:\t", len(photos))
    print("Переименовано:\t\t", pr_pics)
    print("Не переименовано:\t", len(photos)-pr_pics)

if __name__ == "__main__":
    print("EXIF-namer")
    main()