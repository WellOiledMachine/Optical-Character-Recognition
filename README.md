# Optical-Character-Recognition

## Overview
A collection of utilities designed for automating the extraction of text from images/documents through Optical Character Recognition methods.
Will contain tools to effectively and efficiently read text from files and parse through that text to find important data.

## Features
- **Image Preprocessing:** Includes built in image quality improvement methods to ensure that OCR extraction is as accurate as possible.
- **Customizable Text Extraction:** Simply provide images or pdf documents to extract text from images using the tesseract engine. You can easily provide your own custom functions for preprocessing the images, or use the built-in ones. You can also create custom functions to grab segments of the images and extract the text from those segments.
- **Customizable Text Parsing:** *Currently in development*. 

## Installation
First, install the repository and the package requirements using:
```bash
git clone https://github.com/WellOiledMachine/Optical-Character-Recognition.git
cd Optical-Character-Recognition
pip install -r requirements.txt
```
You may want to use a conda environment to make managing packages easier: [Conda Environments](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

Make sure that you have the [tesseract-ocr repository](https://tesseract-ocr.github.io/tessdoc/Installation.html) installed on your system, and that its version matches up with the version that tesserocr is expecting.
 - You can find your installed tesseract version using `tesseract --version`.  
 - You can find the expected version from tesserocr by running `print(tesserocr.tesseract_version())` in a python file.  
 - Check the [tesserocr library](https://github.com/sirfz/tesserocr) for further details or troubleshooting.

## Getting Started
An example file [example_text_extraction](example_text_extraction.py) has been provided to show how different methods in the TextExtractor class work.

A basic text extraction file would look something like this:
```py
import tesserocr
import cv2
from tools.TextExtractor import TextExtractor
from tools.image_preprocessing import clean_image

image_path = 'path/to/image.jpg'
with tesserocr.PyTessBaseAPI() as api:
    text_extractor = TextExtractor(api, clean_image_func=clean_image)
    text_extractor.extract_from_file(image_path, print_results=True)
```

