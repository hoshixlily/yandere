import os.path
import sys
from dataclasses import dataclass

from mizue.network.downloader import DownloaderTool
from mizue.printer import Printer

from parser import Parser, ParsedImageData


@dataclass
class ImageData:
    filename: str
    filepath: str
    url: str


if __name__ == '__main__':
    yandere_parser = Parser()
    image_data: list[ParsedImageData] = yandere_parser.parse(f"https://yande.re/post?tags={sys.argv[1]}", 1)
    Printer.success("\nParsed {} images\n".format(len(image_data)))
    output_dir = "output"

    png_data = [ImageData(filename=image_data_item.filename_png,
                          filepath=os.path.join(output_dir, image_data_item.filename_png),
                          url=image_data_item.url_png) for image_data_item in image_data if
                image_data_item.filename_png != ""]
    jpg_data = [ImageData(filename=image_data_item.filename_jpg,
                          filepath=os.path.join(output_dir, image_data_item.filename_jpg),
                          url=image_data_item.url_jpg) for image_data_item in image_data]

    # filter out images that already exist
    png_data = [image_data_item for image_data_item in png_data if not os.path.exists(image_data_item.filepath)]

    # filter out jpg images that already exist
    jpg_data = [image_data_item for image_data_item in jpg_data if not os.path.exists(image_data_item.filepath)]

    # download png images
    png_download_data = [(image_data_item.url, output_dir) for image_data_item in png_data]
    if len(png_download_data) > 0:
        Printer.info("Downloading PNG images...")
        downloader = DownloaderTool()
        downloader.download_tuple(png_download_data, 10)
        Printer.success(f"{os.linesep}PNG images downloaded")
    else:
        Printer.info("No PNG images to download")

    filtered_jpg_data = []
    for jpg_data_item in jpg_data:
        png_filepath = jpg_data_item.filepath.replace(".jpg", ".png")
        if os.path.exists(jpg_data_item.filepath) and os.path.exists(png_filepath):
            os.remove(jpg_data_item.filepath)
            continue
        if os.path.exists(png_filepath):
            continue
        filtered_jpg_data.append(jpg_data_item)

    jpg_download_data = [(image_data_item.url, output_dir) for image_data_item in filtered_jpg_data]

    # download jpg images
    if len(jpg_download_data) > 0:
        Printer.info("Downloading JPG images...")
        downloader = DownloaderTool()
        downloader.download_tuple(jpg_download_data, 10)
        Printer.success(f"{os.linesep}JPG images downloaded")
    else:
        Printer.info("No JPG images to download")

    Printer.success("Done!")
