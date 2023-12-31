# Yande.re Image Downloader

This script downloads images from **yande.re** based on the specified tags.

## Install packages

```shell
pip install -r requirements.txt
```

## Usage

```shell
python yandere.py [OPTIONS]
```

## Options

- `-t`, `--tags` (required): Tags to search for. Multiple tags can be specified by separating them with a space and enclosing them in quotes.
- `-o`, `--output` (optional): Output directory. Default is `./output`.
- `-s`, `--start-page` (optional): Start page. Default is `1`.
- `-e`, `--end-page` (optional): End page. Default is not set. It will download all pages if not set.
- `-png`, `--prefer-png` (optional): Prefer PNG images over JPG. Default is `False`.
- `-p`, `--parallel-downloads` (optional): Number of parallel downloads. Default is `4`.
- `-r`, `--report` (optional): Generate a report after download is completed. Default is `True`.
- `-f`, `--force` (optional): Force download even if the file already exists. Default is `False`.

## Notes
 
- If the prefer-png option is set, the script will download the PNG version of the image if it exists.  
  Otherwise, it will download the JPG version. Enabling this option will check for the existence of the PNG version of each image  
  therefore the parsing will be significantly slower. Also, the filesize of the PNG version will be significantly larger than the JPG version,  
  so only enable this if you really need the PNG version of the image.

## Examples

Download images with the tag "sword" to the default output directory:

```shell
python yandere.py -t sword
```

Download images with the tags "sword" and "dress" to the default output directory:

```shell
python yandere.py -t "sword dress"
```

Download images with the tag "sword" to a custom output directory:

```shell
python yandere.py -t sword -o /path/to/output
```

Download images with the tag "sword" and prefer PNG images over JPG:

```shell
python yandere.py -t sword --prefer-png
```

Download images with the tag "sword" and force download even if the file already exists:

```shell
python yandere.py -t sword --force
```