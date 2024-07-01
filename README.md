# Optical-Character-Recognition

## Overview
A collection of utilities designed for automating the extraction of text from images/documents through Optical Character Recognition methods.
Will contain tools to effectively and efficiently read text from files and parse through that text to find important data.

## Features
- **Image Preprocessing:** Includes built in image quality improvement methods to ensure that OCR extraction is as accurate as possible.
- **Customizable Text Extraction:** Simply provide images or pdf documents to extract text from images using the tesseract engine. You can easily provide your own custom functions for preprocessing the images, or use the built-in ones. You can also create custom functions to grab segments of the images and extract the text from those segments.
- **Customizable Text Parsing:** *Currently in development*. 

## Installation
### Windows
**Step 1**: Install the [Miniconda](https://docs.anaconda.com/miniconda/miniconda-install/) Conda Installer  

**Step 2**: Download the repository. In the Anaconda Prompt shell, navigate to the desired direcory, then copy and paste these commands and press enter:
```bash
git clone https://github.com/WellOiledMachine/Optical-Character-Recognition.git
cd Optical-Character-Recognition
```
- You will need to open one of the new Anaconda Prompt (miniconda3) shell applications for the next steps
   - You may need to restart your computer after installing miniconda to find this shell
 
**Step 3**: Create the conda environment.  
To make sure you are not currently in an environment, and then create a new one using our configuration file, run these commands in the Anaconda shell:
```bash
conda deactivate
conda env create --file environment.yaml -y
```
You may now continue to the `Run application` section. Make sure you continue to use the Anaconda Prompt Shell for each step.

---

### Linux / WSL on Windows
**Step 1**: Install Miniconda for your linux distribution by following the instructions [here](https://docs.anaconda.com/miniconda/).  
- Make sure conda is installed correctly. Use `conda -V` and make sure conda prints its version.

**Step 2**: Download the repository. Navigate to the desired directory and run these commands:
```bash
git clone https://github.com/WellOiledMachine/Optical-Character-Recognition.git
cd Optical-Character-Recognition
```
**Step 3**: Create the conda environment:
```bash
conda deactivate
conda env create --file environment.yaml -y
```

Extra packages may need to be downloaded for Ubuntu / WSL + Ubuntu systems that conda can not provide. It is recommended to run these commands, especially if you run into errors:
```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install libglapi-mesa libegl-mesa0 libegl1 libopengl0 libgl1-mesa-glx -y
```
You may now continue to the `Run application` section.

### Run application

---

Make sure your conda environment is installed using the command `conda activate text_extraction`, then you should be able to run code in this repository:
```bash
conda activate text_extraction
python example_text_extraction.py
```

### Uninstallation

---

If you would like to uninstall the repository, you can just delete the Optical-Character-Recognition folder.  
If you would like to delete the conda environment created to run the repository, run these commands:
```bash
conda deactivate
conda remove --name text_extraction --all
```

Refer to [this link](https://docs.anaconda.com/anaconda/install/uninstall/) if you wish to uninstall conda.

## Getting Started
### Command Line Usage
This repository contains the functionality to do simple text extractions on pdf and photo files using the command line. It also contains functionality to perform simple image processing from the command line.  
Detailed explanations of the commands can be found below:
#### Text Extraction  
**Usage**: `python tools/TextExtractor.py [-h] (-d DIRECTORY | -f FILE) [-o OUTPUT] [--print] [--get_data]`

| flag  | option | explanation |
| ------ | -------------- | --- |
| -h | --help | If set, show the help message that explains these options and exit |  
| -d \<path\> | --directory \<path\> | Path to the directory containing the images or PDFs to extract text from. Mutually exclusive with --file. |  
| -f \<path\> | --file \<path\> | Path to the image or PDF file. Mutually exclusive with --directory.|  
| -o \<path\> | --output \<path\> | Path to the directory to save the extracted text files to |  
| N/A | --print | If set, will print the extracted text to the console. True by default if --output not set. |  
| N/A | --get_data | If set, will extract word-specific data from the images |  

**Example**: `python tools/TextExtractor.py -d example_forms -o output_folder --get_data` will extract all of the text and its coordinate information from the pdf and image files in the example_forms folder and outputs that information to the provided output directory.

---

#### Image Processing
From the root folder of the repository, use command `python tools/ImageProcessor.py` to use the ImageProcessor class to process image files and clean them.  
**Usage**: `python tools/ImageProcessor.py [-h] (--image IMAGE | --directory DIRECTORY) [--output OUTPUT]`

| flag  | option | explanation |
| ------ | ------------- | --- |
| -h | --help | If set, show the help message that explains these options and exit |  
| -i | --image \<path\> | Path to the image file. Mutually exclusive with --directory. |
| -d \<path\> | --directory \<path\> | Path to the directory of images. Mutually exclusive with --image. |
| -o \<path\> | --output \<path\> | Path to the output directory. Processed images will be output with a '_annotated' appended to the title. |

**Example**: `python tools/ImageProcessor.py -i test_images/SampleText.jpg -o output_folder` will process a single image and output it to the folder `output_folder`.


### Creating a custom text extraction script
An example file [example_text_extraction](example_text_extraction.py) has been provided to show how different methods in the TextExtractor class work.

A basic text extraction script would look something like this:

```py
import tesserocr
from tools.TextExtractor import TextExtractor
from tools.ImageProcessor import ImageProcessor

clean_image_func = ImageProcessor() # Define image processing function with default arguments 

image_path = 'path/to/image.jpg'
with tesserocr.PyTessBaseAPI() as api:
    text_extractor = TextExtractor(api, clean_image_func=clean_image_func)
    text_extractor.extract_from_file(image_path, print_results=True)
```

Then, you would run the script using `python text_extraction_script.py`.
