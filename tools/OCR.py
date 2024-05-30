# Author: Cody Sloan
# Project: Optical Character Recognition
# This script contains functions to produce text from images using
# the tesseract OCR engine.

import numpy as np
import pytesseract
from image_preprocessing import clean_image
import os
from argparse import ArgumentParser
import csv
from pandas import DataFrame

def extract_text(image_name, psm=3, get_data=False):
    """
    Parameters
    ----------
    image_name : str
        The path to the image file that text is to be extracted from.
    psm : int, optional
        The page segmentation mode to use. The default is 3 (the default that tesseract uses). 
        The possible values and their uses are found here:
            Page segmentation modes:
                0    Orientation and script detection (OSD) only.
                1    Automatic page segmentation with OSD.
                2    Automatic page segmentation, but no OSD, or OCR. (not implemented)
                3    Fully automatic page segmentation, but no OSD. (Default)
                4    Assume a single column of text of variable sizes.
                5    Assume a single uniform block of vertically aligned text.
                6    Assume a single uniform block of text.
                7    Treat the image as a single text line.
                8    Treat the image as a single word.
                9    Treat the image as a single word in a circle.
                10    Treat the image as a single character.
                11    Sparse text. Find as much text as possible in no particular order.
                12    Sparse text with OSD.
                13    Raw line. Treat the image as a single text line,
                    bypassing hacks that are Tesseract-specific.
    get_data : bool, optional
        Whether to return the tabular data from the OCR. The default is False, which means it just returns the text.
        
    Returns
    -------
    text : str
        The text extracted from the image. If get_data is True, it will contain the location information for each word.
    
    Description
    -----------
    This function uses the pytesseract library to extract text from an image. First it preprocesses the image using the
    clean_image function, then it uses tesseract to extract text from the image based on the arguments. It can return 
    the text only or the tabular data of the text as a string. The page segmentation mode can be set to change how text
    is extracted from the image (Explained better in the psm parameter description above). The form feed character that
    pytesseract adds to the end of the text is also removed.
    """
    # Define the configuration for pytesseract
    sconfig = ''
    if psm is not None:
        sconfig = '--psm ' + str(psm)
        
    # Clean the image
    image = clean_image(image_name)
    
    # Use pytesseract to extract text from the image
    try:
        if get_data:
            # Reads text and returns a string with each word and location information
            text = pytesseract.image_to_data(image, config=sconfig)
        else:
            # Reads text and returns a string
            text = pytesseract.image_to_string(image, config=sconfig)
    except Exception as e:
        text = 'FAILED OCR: ' + str(e)
        
    # Remove the form feed character at the end of the text
    if text.endswith('\f'):
        text = text[:-1]
    
    return text


def extract_from_dir(directory, output_dir, psm=3, get_data=False):
    """
    Parameters
    ----------
    directory : str
        The directory containing the images to extract text from.
    output_dir : str
        The directory to save the extracted text files.
    psm : int, optional
        The page segmentation mode to use when extracting text. The default is 3 (the default that tesseract uses).
    get_data : bool, optional
        Whether to extract the tabular data from the OCR. The default is False, which means it just extracts the text.
        
    Returns
    -------
    None
        
    Description
    -----------
    This function extracts text from images in a directory and saves the text to files in the specified output 
    directory. The page segmentation mode can be set to change how the text is extracted from the image (more
    information in the extract_text function description). The function will check if each image is valid, and print
    out the path of each image it processes and the path of the text file it saves. The text file will either only be
    the extracted text, or it will contain the tabular data from the OCR (each word and its location information), 
    based on the get_data parameter.
    """
    # Get the list of images in the directory
    images = os.listdir(directory)
    
    # Prepare list of valid image formats
    valid_image_formats = ['.png', '.jpg', '.jpeg', '.jpe', '.webp', '.bmp', '.webp'
                           '.dib','.tiff', '.tif', '.pxm', '.pgm', '.pbm', '.pnm']
    
    # Create the output directory if it does not exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Loop through the images in the directory
    for image_name in images:
        # Check that the file is not a directory
        if os.path.isdir(os.path.join(directory, image_name)):
            continue
        
        # Check that the file is a valid image format
        if not any(image_name.endswith(ext) for ext in valid_image_formats):
            print(f'Invalid image format: {image_name}')
            continue
        
        # Use pytesseract to extract text from the image
        input_path = os.path.join(directory, image_name)
        text = extract_text(input_path, psm, get_data)
        
        # Write the text to a file
        output_path = os.path.join(output_dir, image_name) + '.txt'
        with open(output_path, 'w') as f:
            f.write(text)
            
    print(f'Text extracted from photos in {directory} and saved to {output_dir}')
    

def extract_and_print(image_name, psm=3, get_data=False):
    """
    Parameters
    ----------
    image_name : str
        The path to the image file that text is to be extracted from.
    psm : int, optional
        The page segmentation mode to use when extracting text. The default is 3 (the default that tesseract uses).
    get_data : bool, optional
        Whether to extract the tabular data from the OCR. The default is False, which means it just extracts the text.
        
    Returns
    -------
    None
        
    Description
    -----------
    Preprocesses the image using the clean_image function and then extracts text from the image using the extract_text 
    function. The extracted text is printed to the console. The page segmentation mode can be set to change how the
    text is extracted (more information in the extract_text function description). The printed text will either only be
    the extracted text, or it will contain the tabular data from the OCR (each word and its location information),
    based on the get_data parameter.
    """
    # Use pytesseract to extract text from the image
    text = extract_text(image_name, psm, get_data)
    print(text)
    
def extract_and_save(image_name, output_path, psm=None, get_data=False):
    """
    Parameters
    ----------
    image_name : str
        The path to the image file that text is to be extracted from.
    output_path : str
        The path to save the extracted text.
    psm : int, optional
        The page segmentation mode to use when extracting text. The default is 3 (the default that tesseract uses).
    get_data : bool, optional
        Whether to extract the tabular data from the OCR. The default is False, which means it just extracts the text.
        
    Returns
    -------
    None
    
    Description
    -----------
    Preprocesses the image using the clean_image function and then extracts text from the image using the extract_text
    function. The extracted text will either only be the extracted text, or it will contain the tabular data from the 
    OCR (each word and its location information), based on the get_data parameter. The extracted text is then saved to
    the specified output path.
    """
    # Use pytesseract to extract text from the image
    text = extract_text(image_name, psm, get_data)
    
    # Create the output directory if it does not exist
    os.makedirs(os.path.split(output_path)[0], exist_ok=True)
    
    # Write the text to a file
    with open(output_path, 'w') as f:
        f.write(text)
        
    print(f'Text from {image_name} extracted and saved to {output_path}')
    
    
if __name__ == "__main__":
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image', help='Path to the image file')
    group.add_argument('--directory', help='Path to the directory of images')
    
    parser.add_argument('--save', help='Path to save the extracted text')
    parser.add_argument('--psm', help='Page segmentation mode', type=int)
    parser.add_argument('--get_data', help='Return data from OCR', action='store_true')
    
    args = parser.parse_args()
    
    if args.directory and not args.save:
        parser.error("--save is required when --directory is used")
        
    if args.directory:
        extract_from_dir(args.directory, args.save, args.psm, args.get_data)
    elif args.image and args.save:
        extract_and_save(args.image, args.save, args.psm, args.get_data)
    else:
        extract_and_print(args.image, args.psm, args.get_data)
    