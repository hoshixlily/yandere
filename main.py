import argparse
import os.path
from dataclasses import dataclass

from mizue.network.downloader import DownloaderTool
from mizue.printer import Printer

from parser import Parser, ParsedImageData


@dataclass
class _ImageData:
    filename: str
    filepath: str
    url: str


def _filter_existing_images(data: list[_ImageData]) -> list[_ImageData]:
    return [image_data_item for image_data_item in data if not os.path.exists(image_data_item.filepath)]


def _skip_or_overwrite_warning(data: list[_ImageData], force: bool, type: str) -> None:
    previous = len(data)
    download_data = _filter_existing_images(data)
    existing = previous - len(download_data)
    if previous != len(download_data):
        if force:
            Printer.warning(
                f"{existing} of {previous} {type} images already exist. They will be overwritten.")
        else:
            Printer.warning(f"{existing} of {previous} {type} images already exist. They will be "
                            f"skipped.")


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Download images from yande.re",
                                        formatter_class=argparse.RawTextHelpFormatter)
    argparser.add_argument("-t", "--tags", help="Tags to search for", required=True)
    argparser.add_argument("-o", "--output", help="Output directory", type=str,
                           default=os.path.join(os.getcwd(), "output"))
    argparser.add_argument("-s", "--start-page", help="Start page", type=int, default=1)
    argparser.add_argument("-e", "--end-page", help="End page", type=int, default=None)
    argparser.add_argument("-png", "--prefer-png", help="Prefer PNG images over JPG", action="store_true")
    argparser.add_argument("-p", "--parallel-downloads", help="Number of parallel downloads", type=int, default=4)
    argparser.add_argument("-r", "--report", help="Generate a report after download is completed", action="store_false")
    argparser.add_argument("-f", "--force", help="Force download even if the file already exists", action="store_true")
    args = argparser.parse_args()
    tags = args.tags
    output_dir = args.output
    prefer_png = args.prefer_png
    parallel_downloads = args.parallel_downloads
    start_page = args.start_page
    end_page = args.end_page
    display_report = args.report
    force_download = args.force

    parser = Parser()
    parser.prefer_png = prefer_png
    Printer.info("Parsing pages...")
    if prefer_png:
        Printer.warning("Prefer PNG images over JPG. This will increase the parsing time.")

    image_data: list[ParsedImageData] = parser.parse(f"https://yande.re/post?tags={tags}", start_page, end_page)
    Printer.success("\nParsed {} images\n".format(len(image_data)))

    png_data = [_ImageData(filename=image_data_item.filename_png,
                           filepath=os.path.join(output_dir, image_data_item.filename_png),
                           url=image_data_item.url_png) for image_data_item in image_data if
                image_data_item.filename_png != ""]
    jpg_data = [_ImageData(filename=image_data_item.filename_jpg,
                           filepath=os.path.join(output_dir, image_data_item.filename_jpg),
                           url=image_data_item.url_jpg) for image_data_item in image_data]

    _skip_or_overwrite_warning(png_data, force_download, "PNG")
    if not force_download:
        png_data = _filter_existing_images(png_data)

    # download png images
    png_download_data = []
    if prefer_png:
        png_download_data = [(image_data_item.url, output_dir) for image_data_item in png_data]
        if len(png_download_data) > 0:
            Printer.info("Downloading PNG images...")
            downloader = DownloaderTool()
            downloader.display_report = display_report
            downloader.download_tuple(png_download_data, parallel_downloads)
            Printer.success(f"{os.linesep}PNG images downloaded.")
        else:
            Printer.info("No PNG images to download")
    else:
        Printer.info("The -png argument was not supplied. All images will be downloaded as JPG.")

    filtered_jpg_data = []
    if prefer_png:
        for jpg_data_item in jpg_data:
            png_filepath = jpg_data_item.filepath.replace(".jpg", ".png")
            if os.path.exists(png_filepath):
                continue
            filtered_jpg_data.append(jpg_data_item)
    else:
        filtered_jpg_data = jpg_data

    _skip_or_overwrite_warning(filtered_jpg_data, force_download, "JPG")
    if not force_download:
        filtered_jpg_data = _filter_existing_images(filtered_jpg_data)
    jpg_download_data = [(image_data_item.url, output_dir) for image_data_item in filtered_jpg_data]

    # download jpg images
    if len(jpg_download_data) > 0:
        Printer.info("Downloading JPG images...")
        downloader = DownloaderTool()
        downloader.display_report = display_report
        downloader.download_tuple(jpg_download_data, parallel_downloads)
        Printer.success(f"{os.linesep}JPG images downloaded")
    else:
        Printer.info("No JPG images to download")

    Printer.success(
        f"{os.linesep}Download complete. {len(png_download_data)} PNG images and {len(jpg_download_data)} "
        f"JPG images have been downloaded.")
    print(os.linesep)
