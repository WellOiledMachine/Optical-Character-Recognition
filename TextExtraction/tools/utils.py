import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image


def convert_file_to_images(file_name, use_PIL_data_type=False):
    """
    Parameters
    ----------
    file_name : str
        The path to the image or PDF file to extract text from.
    use_PIL_data_type : bool, optional
        Whether to return the images in PIL.Image data type. The default is False, which uses the numpy.ndarray
        data type. This is useful for cv2 cleaning functions, which will expect a numpy.ndarray data type.
    
    Returns
    -------
    images : list<numpy.ndarray OR PIL.Image>
        A list of images to extract text from.

    Description
    -----------
    This function converts an image or PDF file into a list of images. Must return a list because the PDF file
    could have multiple pages, so the pdf2image conversion function returns a list of images as well. Image files
    will be converted to a list of one image, unless the image is a TIFF file with multiple frames, in which case 
    each frame will be in the returned list.

    The images will be returned as numpy.ndarray objects by default. Setting use_PIL_data_type to True will make
    the images be returned as PIL.Image objects instead.

    NOTE: The numpy images will be using RGB color space, which is not what cv2 uses by default (BGR). If you don't
    properly use color space flags when using cv2 functions, you will likely have issues.
    """
    # Define the accepted image file types
    img_file_type  = ('.png', '.jpg', '.jpeg', '.jpe', '.webp', '.bmp', '.webp', '.dib', '.pxm','.pgm',
                            '.pbm', '.pnm')

    if file_name.endswith('.pdf'):
        # Create PIL image List from path/to/pdf. Will grab each page and convert it to be an image in the
        # returned list. Will return a list regardless of the number of pages.
        images = convert_from_path(file_name, 300)
        # Convert the images from PIL to OpenCV for the cleaning function
        if not use_PIL_data_type:
            images = [np.array(image.convert('L')) for image in images]
                
    # Check if the file is an image
    elif file_name.lower().endswith(img_file_type):
        if use_PIL_data_type:
            # Read the image using PIL
            image = Image.open(file_name).convert('L')
            images = [image]
        else:
            # Read the image using OpenCV
            image = cv2.imread(file_name, cv2.IMREAD_GRAYSCALE)
            # This function expects a list of images, so need to convert the image to a list of itself.
            images = [image]
    
    # Handle TIFF files, which may have multiple frames
    elif file_name.lower().endswith('.tif') or file_name.lower().endswith('.tiff'):
        # Read the image using PIL
        image = Image.open(file_name)
        images = []
        # Loop through each frame in the TIFF file and convert it to a numpy array
        for i in range(image.n_frames):
            image.seek(i)
            if use_PIL_data_type:
                images.append(image.convert('L'))
            else:
                images.append(np.array(image.convert('L')))

    else:
        print(f"File {file_name} is not a PDF or image file.")
        return None
    
    return images
