from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Dict
import concurrent.futures
import sys

from exif import Image


EXIF_DATETIME_ORIGINAL_TAG = "EXIF DateTimeOriginal"


def get_args():
    parser = ArgumentParser(description="EXIF namer script")
    parser.add_argument("input_path", type=str,
                        help="Path to image or directory with images")
    parser.add_argument("output_dir", type=str,
                        help="Path to output directory")
    return parser.parse_args()


def process_image(in_img_path: Path, out_img_dir: Path) -> Dict[Path, Path]:
    """ Extract EXIF data from image and return path mapping """
    with open(in_img_path, "rb") as image_file_stream:
        image = Image(image_file_stream)
        if image.has_exif:
            out_img_name = make_name(image.datetime_original)
            out_img_path = out_img_dir.joinpath(out_img_name)
        else:
            # if no EXIF datetime, not change initial name
            out_img_path = out_img_dir.joinpath(in_img_path.name)
    return {in_img_path: out_img_path}


def make_name(datetime_: str) -> str:
    datetime_ = datetime_.replace(":", "")
    datetime_ = datetime_.replace(" ", "_")
    return f"IMG_{datetime_}.jpg"


def rename_images(mappings: Dict[Path, Path]):
    print("Mapping images...")
    repeats = defaultdict(int)
    for in_img_path, out_img_path in mappings.items():
        if out_img_path.exists():
            repeats[out_img_path] += 1
            out_img_name = f"{out_img_path.stem}_" \
                           f"({repeats[out_img_path]})" \
                           f"{out_img_path.suffix}"
            out_img_path = out_img_path.parent.joinpath(out_img_name)
        print(f"{in_img_path} -> {out_img_path}")
        out_img_path.write_bytes(in_img_path.read_bytes())


if __name__ == "__main__":
    args = get_args()

    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"Path '{input_path}' not exists. Exit")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)

    if input_path.is_file():
        mappings = process_image(input_path, output_dir)
    elif input_path.is_dir():
        mappings = {}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            exif_futures = [executor.submit(process_image, img, output_dir) for img in input_path.iterdir()]
            for future in concurrent.futures.as_completed(exif_futures):
                mappings.update(future.result())

    rename_images(mappings)
