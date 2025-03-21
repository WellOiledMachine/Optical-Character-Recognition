import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image
import cv2


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


def convert_pathlist_to_imagelist(file_paths, use_PIL_data_type=False):
    """
    Parameters
    ----------
    file_paths : list<str>
        A list of file paths to convert to images.
    use_PIL_data_type : bool, optional
        Whether to return the images in PIL.Image data type. The default is False, which uses the numpy.ndarray
        data type. This is useful for cv2 cleaning functions, which will expect a numpy.ndarray data type.
    
    Returns
    -------
    images : list<numpy.ndarray OR PIL.Image>
        A list of images to extract text from.

    Description
    -----------
    This function converts a list of image or PDF file paths into a list of images. Must return a list because the PDF file
    could have multiple pages, so the pdf2image conversion function returns a list of images as well. Image files
    will be converted to a list of one image, unless the image is a TIFF file with multiple frames, in which case 
    each frame will be in the returned list.

    The images will be returned as numpy.ndarray objects by default. Setting use_PIL_data_type to True will make
    the images be returned as PIL.Image objects instead.

    NOTE: The numpy images will be using RGB color space, which is not what cv2 uses by default (BGR). If you don't
    properly use color space flags when using cv2 functions, you will likely have issues.
    """
    images = []
    for file_path in file_paths:
        images.extend(convert_file_to_images(file_path, use_PIL_data_type))
        
    return images

def show_grid(image, font_size=1):
    """
    Parameters
    ----------
    image : numpy.ndarray
        The image to display the grid on.
    font_size : float, optional
        The font size to use for the coordinates. The default is 1.
    
    Returns
    -------
    None

    Description
    -----------
    This function displays a grid on the image with pixel coordinates. The grid will have 4 lines horizontally and vertically
    drawn on the image with the pixel coordinates displayed next to the lines. The coordinates will be displayed in the corners
    of the image as well. The font size can be adjusted to make the coordinates larger or smaller. The positions of the displayed
    coordinates will automatically be adjusted based on the font size.

    """
    # Define how close to the edges of the page the coordinates will be displayed.
    top_coords_y = 40
    left_coords_x = 10

    number_of_lines = 5 # Number of lines to draw on the image
    height, width = image.shape[:2]
    
    # Calculate the spacing between lines
    horizontal_spacing = width // number_of_lines+2
    vertical_spacing = height // number_of_lines+2
    
    # Draw horizontal lines and display pixel coordinates
    for i in range(1, number_of_lines):
        y = i * vertical_spacing
        cv2.line(image, (0, y), (width, y), (0, 255, 0), 2)
        cv2.putText(image, str(y), (left_coords_x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 255, 0), 2)
    
    # Draw vertical lines and display pixel coordinates
    for i in range(1, number_of_lines):
        x = i * horizontal_spacing
        cv2.line(image, (x, 0), (x, height), (0, 255, 0), 2)
        cv2.putText(image, str(x), (x + 10, int(top_coords_y*font_size)), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 255, 0), 2)
    
    # Display the (x, y) coordinates of each corner
    cv2.putText(image, "(0, 0)", (left_coords_x, int(top_coords_y*font_size)), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 255, 0), 2)
    cv2.putText(image, f"({width}, 0)", (int(width - (175*font_size)), int(top_coords_y*font_size)), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 255, 0), 2)
    cv2.putText(image, f"(0, {height})", (left_coords_x, height - 10), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 255, 0), 2)
    cv2.putText(image, f"({width}, {height})", (int(width - (225*font_size)), height - 10), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 255, 0), 2)

    # Display the image
    import matplotlib.pyplot as plt
    plt.axis('off')
    plt.imshow(image, cmap='gray')
    plt.show()



def parse_config_file(file_path):
    """
    Parameters
    ----------
    file_path : str
        The path to the configuration file to parse.

    """
    import json
    with open(file_path, 'r') as file:
        config = json.load(file)
    
    return config


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--show-grid",action="store_true", help="Display a grid on the image with pixel coordinates.")
    parser.add_argument("file", type=str, help="The path to the image or PDF file to convert to images.")
    parser.add_argument("--font-size", type=float, default=1, help="The font size to use for the coordinates.")
    args = parser.parse_args()

    if args.show_grid:
        images = convert_file_to_images(args.file, use_PIL_data_type=False)
        for image in images:
            show_grid(image, args.font_size)
    
    print("Done")