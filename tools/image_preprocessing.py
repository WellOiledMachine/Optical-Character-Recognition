# Author: Cody Sloan
# Project: Optical Character Recognition
# This script contains functions to preprocess images for to use with
# the tesseract OCR engine.

import numpy as np
import cv2
import os
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from skimage import io
from skimage.transform import rotate
from deskew import determine_skew

def clean_image(image_path, crop=True):
    # Read in the image as grayscale
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    rotated, _ = deskew(gray)
    
    # Apply bilateral filter to the image to reduce noise
    bi_filter = cv2.bilateralFilter(rotated,9,75,75)
    
    # Apply adaptive gaussian threshold to the image to get a binary image
    thresh = cv2.adaptiveThreshold(bi_filter,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
                cv2.THRESH_BINARY,11,2)
    
    return thresh

def clean_image_dir(directory, output_path):
    """
    Parameters
    ----------
    directory : str
        The path to the directory containing the images to clean.
    output_path : str
        The path to the directory to save the cleaned images to.
    
    Returns
    -------
    None
    
    Description
    -----------
    This function cleans all the images in a directory and saves them to a new directory. The 'cleaning' done to the
    images are defined in the clean_image function. The images are saved with the same name as the original image with
    an added '_cleaned' to the end of the name.
    """
    # Create a directory to store the cleaned images
    os.makedirs(output_path, exist_ok=True)

    # Get the list of images in the directory
    images = os.listdir(directory)
    
    # Prepare list of valid image formats
    valid_image_formats = ['.png', '.jpg', '.jpeg', '.jpe', '.webp', '.bmp', '.webp'
                           '.dib','.tiff', '.tif', '.pxm', '.pgm', '.pbm', '.pnm']

    # Loop through the images in the directory
    for image_name in images:
        # Check that the file is not a directory
        if os.path.isdir(os.path.join(directory, image_name)):
            continue
        
        # Check that the file is a valid image format
        if not any(image_name.endswith(ext) for ext in valid_image_formats):
            print(f'Invalid image format: {image_name}')
            continue
        
        # Clean and save the image to the output directory
        input_path = os.path.join(directory, image_name)
        cleaned_image = clean_image(input_path)
        
        # Give the cleaned image the same name as the original image with '_cleaned' added to the end
        new_name = os.path.splitext(image_name)[0] + '_cleaned' + os.path.splitext(image_name)[1]
        # Save the cleaned image
        output_file = os.path.join(output_path, new_name)
        cv2.imwrite(output_file, cleaned_image)
    
    print('Images cleaned and saved to ' + output_path)


def deskew(image):
    """
    Parameters
    ----------
    image : numpy array
        The image to deskew.
        
    Returns
    -------
    rotated : numpy array
        The deskewed image.
    angle : float
        The angle of rotation applied to deskew the image.
        
    Description
    -----------
    This function deskews an image by rotating it to align text with the horizontal axis. 
    """
    # Determine the angle of rotation needed to deskew the image    
    angle = determine_skew(image)
    
    # Apply the rotation to the image, and convert it back to a uint8 image
    rotated = (rotate(image, angle, resize=True, cval=1)*255).astype(np.uint8)
    
    return rotated, angle
    

if __name__ == "__main__":
    # Parse the arguments
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--image', help='Path to the image file')
    group.add_argument('--directory', help='Path to the directory of images')
    
    parser.add_argument('--output', help='Path to the output directory')
    
    args = parser.parse_args()
    
    # Clean either a single image and display it, or clean a directory of images and save them to a new directory
    if args.image:
        cleaned_image = clean_image(args.image)
        plt.imshow(cleaned_image, cmap='gray')
        plt.show()
    elif args.directory:
        clean_image_dir(args.directory, args.output)
        print('Images cleaned and saved to ' + args.output)
    
