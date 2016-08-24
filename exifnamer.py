import os
import glob
import exifread

def process_directory(work_directory):
    """Принимает на вход каталог, возвращает список *.jpg файлов"""
    work_directory += "\\*.jpg"
    return glob.glob(work_directory)

def make_data_pattern(date_time):
    """Принимает на вход дату и меняет её под шаблон"""
    date_time = date_time.replace(":", "-")
    date_time = date_time.replace(" ", "_")
    return date_time

def process_photo(cur_photo):
    """Извлекает из фото exif-данные, на основе их переименовывает"""
    image = open(cur_photo, "rb")
    metadata = exifread.process_file(image)
    image.close()
    if 'EXIF DateTimeOriginal' in metadata:
        tag_value = metadata.get("EXIF DateTimeOriginal")
        dt_pattern = make_data_pattern(tag_value.printable)
        print(dt_pattern)
        os.rename(cur_photo, os.getcwd() + '\\photos\\' + dt_pattern + '.jpg')
        print(cur_photo + " -> " + tag_value.printable+'.jpg')
    else:
        print(cur_photo + " -> " + "не переименовано")

def main():
    folder = process_directory(os.getcwd()+'\\photos')
    for pic in folder:
        process_photo(pic)

if __name__ == "__main__":
    print("EXIF-namer v0.1")
    main()