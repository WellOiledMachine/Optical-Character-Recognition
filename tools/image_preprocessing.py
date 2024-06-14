# Author: Cody Sloan
# Project: Optical Character Recognition
# This script contains functions to preprocess images for to use with
# the tesseract OCR engine.

import numpy as np
import cv2
import os
from argparse import ArgumentParser
import matplotlib.pyplot as plt
from skimage.transform import rotate
from deskew import determine_skew

class ImagePreprocessor:
    """
    This class provides a place to configure every OCR relevant image preprocessing step to be applied to an image.
    The class is callable, so it can be used as a function to apply the preprocessing steps to an image. The class is 
    set up to have defaults for each preprocessing step, so it will apply very basic preprocessing steps. Every
    preprocessing step is uses OpenCV functions, except for the deskew function, which uses the deskew library.
    It is not advised to apply too many preprocessing steps to an image, as many of the steps are not meant to be combined.
    First initialize the class with the desired preprocessing steps, then call the class with an image to apply those
    preprocessing steps to the image.
    Those who wish to configure the parameters are assumed to understand cv2 image processing methods and how to use
    them.
    """
    def __init__(
                self,
                grayscale = cv2.COLOR_BGR2GRAY,
                normalize: bool = True,
                normalize_args: dict = {"alpha": 0, "beta": 255, "norm_type": cv2.NORM_MINMAX},
                sharpen: bool = False,
                deskew: bool = True,
                denoise: bool = True,
                denoise_args: dict = {"h": 10, "templateWindowSize": 7, "searchWindowSize": 21},
                bilateral_filter: bool = False,
                bilateral_filter_args: dict = {"d": 9, "sigmaColor": 75, "sigmaSpace": 75},
                global_binarize: bool = False,
                global_binarize_args: dict = {"threshold": 127, "maxval": 255, "type": cv2.THRESH_BINARY},
                gaussian_blur: bool = False,
                gaussian_blur_args: dict = {"ksize": (5, 5), "sigmaX": 0},
                otsu_threshold: bool = False,
                otsu_threshold_args: dict = {"threshold": 0, "maxval": 255},
                adaptive_gaussian_threshold: bool = False,
                adaptive_mean_threshold: bool = False,
                adaptive_threshold_args: dict = {"maxval": 255, "blockSize": 11, "C": 2},
                erode: bool = False,
                erosion_args: dict = {"kernel_size": (1,1), "iterations": 1},
                dilate: bool = False,
                dilation_args: dict = {"kernel_size": (1,1), "iterations": 1},
                morphology: bool = False,
                morphology_args: dict = {"kernel_size": (1,1), "op": cv2.MORPH_OPEN}
                ):
        self.grayscale = grayscale
        self.normalize = normalize
        self.normalize_args = normalize_args
        self.sharpen = sharpen
        self.deskew = deskew
        self.denoise = denoise
        self.denoise_args = denoise_args
        self.bilateral_filter = bilateral_filter
        self.bilateral_filter_args = bilateral_filter_args
        self.global_binarize = global_binarize
        self.global_binarize_args = global_binarize_args
        self.gaussian_blur = gaussian_blur
        self.gaussian_blur_args = gaussian_blur_args
        self.otsu_threshold = otsu_threshold
        self.otsu_threshold_args = otsu_threshold_args
        self.adaptive_mean_threshold = adaptive_mean_threshold
        self.adaptive_gaussian_threshold = adaptive_gaussian_threshold
        self.adaptive_threshold_args = adaptive_threshold_args
        self.erode = erode
        self.erosion_args = erosion_args
        self.dilate = dilate
        self.dilation_args = dilation_args
        self.morphology = morphology
        self.morphology_args = morphology_args
        
    def __call__(self, image):
        if self.grayscale is not None:
            image = cv2.cvtColor(image, self.grayscale)
        
        if self.normalize:
            image = cv2.normalize(image, None, **self.normalize_args)

        if self.sharpen:
            kernel = np.array([[-1, -1, -1],
                                [-1, 9, -1],
                                [-1, -1, -1]])
            cv2.filter2D(image, -1, kernel)

        if self.deskew:
            # Determine the angle of rotation needed to deskew the image
            angle = determine_skew(image)
    
            # Apply the rotation to the image, and convert it back to a uint8 image
            image = (rotate(image, angle, resize=True, cval=1)*255).astype(np.uint8)
        
        if self.denoise:
            image = cv2.fastNlMeansDenoising(image, None, **self.denoise_args)

        if self.bilateral_filter:
            image = cv2.bilateralFilter(image, **self.bilateral_filter_args)
        
        if self.global_binarize:
            args = self.global_binarize_args
            image = cv2.threshold(image, args.threshold, args.maxval, cv2.THRESH_BINARY)[1]

        if self.gaussian_blur:
            image = cv2.GaussianBlur(image, **self.gaussian_blur_args)
        
        if self.otsu_threshold:
            args = self.otsu_threshold_args
            image = cv2.threshold(image, args.threshold, args.maxval, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        if self.adaptive_mean_threshold:
            args = self.adaptive_threshold_args
            image = cv2.adaptiveThreshold(image, args.maxval, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                          cv2.THRESH_BINARY,args.blockSize, args.C)
            
        if self.adaptive_gaussian_threshold:
            args = self.adaptive_threshold_args
            image = cv2.adaptiveThreshold(image, args.maxval, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY,args.blockSize, args.C)
        
        if self.erode:
            kernel_size = self.erosion_args.kernel_size
            kernel = np.ones(kernel_size, np.uint8)
            image = cv2.erode(image, kernel, iterations=self.erosion_args.iterations)
        
        if self.dilate:
            kernel_size = self.erosion_args.kernel_size
            kernel = np.ones(kernel_size, np.uint8)
            image = cv2.dilate(image, kernel, iterations=self.erosion_args.iterations)
        
        if self.morphology:
            kernel_size = self.morphology_args.kernel_size
            kernel = np.ones(kernel_size, np.uint8)
            image = cv2.morphologyEx(image, self.morphology_args.op, kernel)

        return image


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

        # Read the image
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        clean_image = ImagePreprocessor(grayscale=None) # Initialize the ImagePreprocessor and turn off grayscaling
        cleaned_image = clean_image(image)
        
        # Give the cleaned image the same name as the original image with '_cleaned' added to the end
        new_name = os.path.splitext(image_name)[0] + '_cleaned' + os.path.splitext(image_name)[1]
        # Save the cleaned image
        output_file = os.path.join(output_path, new_name)
        cv2.imwrite(output_file, cleaned_image)
    
    print('Images cleaned and saved to ' + output_path)
    

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
        image = cv2.imread(args.image, cv2.IMREAD_GRAYSCALE)
        clean_image = ImagePreprocessor(grayscale=None) # Initialize the ImagePreprocessor and turn off grayscaling
        cleaned_image = clean_image(image)
        plt.imshow(cleaned_image, cmap='gray')
        plt.show()
    elif args.directory:
        clean_image_dir(args.directory, args.output)
    
