# Author: Cody Sloan
# Project: Optical Character Recognition
# The ImageCropper class provides methods to define specific crop locations within an image and gathers the resulting
# crop cutouts into a list for further processing.

from tesserocr import RIL, PSM, iterate_level
from PIL import Image
import numpy as np

class ImageCropper():
    """
    Parameters
    ----------
    api : tesserocr.PyTessBaseAPI
        The tesserocr API object to use to extract text from images.

    Description
    -----------
    This class is used to segment images into smaller images. This is useful for extracting text from specific areas
    of an image, improving the accuracy of the text extraction. The  class can also be paired with the tesserocr
    library to automatically detect text segments in an image.
    This class does not contain any methods to preprocess the image before segmenting it. The images should be
    preprocessed before being passed to any of the methods in this class if necessary.
    
    """
    def __init__(self):
        self.segment_coordinates = []

    def __call__(self, image: Image.Image):
        return self.crop(image.convert('L'))

    def add_segment(self, coordinates):
        """Takes a tuple or list of coordinates and adds them to the list of segment coordinates that will be used to
        cut the image into segments."""
        self.segment_coordinates.append(tuple(coordinates))
    
    def add_multiple_segments(self, coordinates_list):
        """Takes a list of coordinates in the form of tuples or lists and adds them to the list of segment coordinates
        that will be used to cut the image into segments."""
        for coordinates in coordinates_list:
            self.add_segment(tuple(coordinates))
    
    def clear_segments(self):
        """Clears all the segment coordinates that have been added to the list of segment coordinates."""
        self.segment_coordinates = []

    def get_tess_auto_segments(self, image, api, level=RIL.BLOCK):
        """
        Parameters
        ----------
        image : numpy.ndarray
            The image to extract text from. Must be a numpy.ndarray object. Must be grayscaled.
        level : tesserocr.RIL, optional
            The level to extract the text from. The default is tesserocr.RIL.BLOCK.
            The levels are defined in the tesserocr library and are used to extract specific segments of the image.
        api : tesserocr.PyTessBaseAPI
            The tesserocr API object to use to analyze the layout of the image.

        Returns
        -------
        images : list<PIL.Image>
            A list of images that contain the extracted text segments. These should be much more accurate than just
            feeding the entire image to tesseract.
        
        Description
        -----------
        This function uses the tesserocr library to analyze the layout of the image and find the coordinates of the 
        text segments that are automatically detected by tesseract.
        """
        # Convert the image to a PIL image
        image = Image.fromarray(image)

        # Set the image to the tesserocr API
        api.SetPageSegMode(PSM.AUTO_ONLY)
        api.SetImage(image)

        # Analyze the layout of the image
        layout = api.AnalyseLayout()
        if layout is None:
            print("No layout found. Exiting.")
            return []

        coordinates = []
        for block in iterate_level(layout, level):
            # Get the bounding box of the text block
            bbox = block.BoundingBox(level)
            if bbox:  # Ensure the bounding box is valid
                # Expand the bounding box slightly to ensure the text block is fully captured
                bbox = [bbox[0]-5, bbox[1]-5, bbox[2]+5, bbox[3]+5]

                coordinates.append(bbox)
            
        self.add_multiple_segments(coordinates)
        api.SetPageSegMode(PSM.AUTO) # Reset the page segmentation mode

        return coordinates

    def crop(self, image):
        """
        Parameters
        ----------
        image : PIL.Image.Image
            The image to segment into smaller images. Must be a grayscaled PIL.Image object.
            Should already be preprocessed before being passed to this function.

        Returns
        -------
        segments : Dict[tuple, PIL.Image.Image]
            A Dictionary of the cropped images mapped with their respective coordinates.

        Description
        -----------
        Takes an input image and grabs specified cropped portions of the image to then be returned in 
        a list. The images will be cropped based on the coordinates provided to the add_segment(), and
        add_multiple_segments(), as well as the coordinates retrieved from get_tess_auto_segments().
        Useful for extracting text from specific areas of an image, improving the accuracy of the text extraction.
        """
        segments = {}
        for coordinates in self.segment_coordinates:
            # Crop the image based on the coordinates
            segment = image.crop(coordinates)
            segments[coordinates] = segment
        
        return segments

