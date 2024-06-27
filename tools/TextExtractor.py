# Author: Cody Sloan
# Project: Optical Character Recognition
# This file contains a class to extract text from images and PDFs using the tesserocr library.

import tesserocr
from tesserocr import PSM
from PIL import Image
from pdf2image import convert_from_path
import cv2
import time
import numpy as np
import os


class TextExtractor:
    """This class is used to extract text from images and PDFs using the tesserocr library. The class provides 
    functions to extract text from images and PDFs, as well as functions to extract word-specific data from the images.
    The class requires being initialized with a tesserocr.PyTessBaseAPI object to use the tesserocr library to extract
    text. This means that objects of this class will only be able to work when it has an opened tesserocr API object 
    attached."""
    def __init__(
            self,
            api, 
            seg_func=None, 
            seg_func_args={}, 
            clean_image_func=None,
            clean_image_func_args={}
        ):
        """
        Parameters
        ----------
        api : tesserocr.PyTessBaseAPI
            The tesserocr API object to use to extract text from images.
        seg_func : function, optional
            The function to segment the image into smaller images. The default is None, which means no segmentation will
            be done. This function must return a list of images (or a tuple or something similar).
        seg_func_args : dict, optional
            Dictionary of arguments that maps each key and value of the arguements that need to be passed to the 
            segmentation function. If your segmentation function does not require any arguments, then leave this parameter alone. 
            The default is an empty dict.
            If your segmentation function requires arguments, then you must provide them in a dict in the form of 
            {arg1: value1, arg2: value2, ...}
        clean_image_func : function, optional
            The function to clean the image before extracting text. The default is None, which means the image will not be
            cleaned. This function must return
        clean_image_func_args : dict, optional
            Dictionary of arguments that maps each key and value of the arguements that need to be passed to the 
            cleaning function. If your cleaning function does not require any arguments, then leave this parameter alone. 
            The default is an empty dict.
            If your cleaning function requires arguments, then you must provide them in a dict in the form of 
            {arg1: value1, arg2: value2, ...}
        """

        self.api = api
        self.seg_func = seg_func
        self.seg_func_args = seg_func_args
        self.clean_image_func = clean_image_func
        self.clean_image_func_args = clean_image_func_args
        self.img_file_type  = ['.png', '.jpg', '.jpeg', '.jpe', '.webp', '.bmp', '.webp', '.dib', '.pxm','.pgm',
                               '.pbm', '.pnm']
        
        # Check if a proper API object was provided
        if not isinstance(api, tesserocr.PyTessBaseAPI):
            raise ValueError("API must be a tesserocr.PyTessBaseAPI object.")

        if clean_image_func is None:
            print("No image cleaning function provided.\n")
            self.clean_image_func = lambda image: image
            self.clean_image_func_args = {}

        if seg_func is None:
            # If no segment function is provided, default to no segmentation
            print("No segment function provided. Defaulting to no segmentation.\n")
            self.seg_func = lambda image: [image]
            self.seg_func_args = {}

    def convert_file_to_images(self, file_name, use_PIL_data_type=False):
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
        if file_name.endswith('.pdf'):
            # Create PIL image List from path/to/pdf. Will grab each page and convert it to be an image in the
            # returned list. Will return a list regardless of the number of pages.
            images = convert_from_path(file_name, 300)
            # Convert the images from PIL to OpenCV for the cleaning function
            if not use_PIL_data_type:
                images = [np.array(image.convert('L')) for image in images]
                    
        # Check if the file is an image
        elif file_name.lower().endswith(tuple(self.img_file_type)):
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


    def get_text(self, image, psm=PSM.AUTO):
        """
        Parameters
        ----------
        image : PIL.Image
            The image to extract text from. Must be a PIL.Image object.

        Returns
        -------
        text : str
            The extracted text from the image.

        Description
        -----------
        This function extracts the text from an image using the tesserocr library. The text is returned as a string.
        """
        self.api.SetPageSegMode(psm)
        
        clean_image = self.clean_image_func(image, **self.clean_image_func_args)

        segments = self.seg_func(clean_image, **self.seg_func_args)

        text = ''
        for segment in segments:
            image = Image.fromarray(segment) if not isinstance(segment, Image.Image) else segment
            self.api.SetImage(image)
            text += self.api.GetUTF8Text()

        return text


    def get_coordinate_data(self, image, psm=PSM.AUTO):
        """
        Parameters
        ----------
        image : PIL.Image
            The image to extract text and coordinate data from. Must be a PIL.Image object.

        Returns
        -------
        data : list<dict>
            A list of dictionaries for each word. Each dictionary contains the extracted text, confidence, and coordinate data. The keys are 'left', 'top', 
            'right', 'bottom', 'conf', and 'text'.

        Description
        -----------
        This function extracts the text, confidence, and coordinate data of every word in an image. The data is stored in a
        dictionary to easily access the data.
        """
        self.api.SetPageSegMode(psm)
        
        clean_image = self.clean_image_func(image, **self.clean_image_func_args)
        segments = self.seg_func(clean_image, **self.seg_func_args)
        data = []

        for segment in segments:
            image = Image.fromarray(segment)
            self.api.SetImage(image)
            self.api.Recognize()

            iterator = self.api.GetIterator()

            # Iterate through the words in the image
            for i in tesserocr.iterate_level(iterator, tesserocr.RIL.WORD):
                # Get the bounding box of the word
                bbox = i.BoundingBox(tesserocr.RIL.WORD)
                # Skip over words that don't have a bounding box
                if bbox is None:
                    continue
                
                data.append({
                    'left': bbox[0],
                    'top': bbox[1],
                    'right': bbox[2],
                    'bottom': bbox[3],
                    'conf': round(i.Confidence(tesserocr.RIL.WORD), 2), # Round to 2 decimal places
                    'text': i.GetUTF8Text(tesserocr.RIL.WORD)
                })
        return data


    def convert_coord_data_to_text(self, data):
        """
        Parameters
        ----------
        data : list<dict>
            A list of dictionaries for each word. Each dictionary contains the extracted word, confidence, and
            coordinate data for that word. The keys are 'left', 'top', 'right', 'bottom', 'conf', and 'text'.
        
        Returns
        -------
        text : str
            A string containing the text, confidence, and coordinate data of all the words in the image.

        Description
        -----------
        This function converts the coordinate data returned by get_coordinate_data for extracted words into a string. 
        The string contains the text, confidence, and coordinate data of each word. The data is separated by tabs, and
        each word is separated by a newline.

        This will be useful to for printing the data or saving the data to a text file.
        """
        text = ''
        for word in data:
            text += '\t'.join(str(value) for value in word.values()) + '\n'
        return text


    def extract_from_file(self, file_path, output_path=None, print_results=False, get_data=False, psm=PSM.AUTO):
        """
        Parameters
        ----------
        file_path : str
            The path to the image or PDF file to extract text from.
        output_path : str, optional
            The path to save the extracted text to. The default is None (no text file will be saved).
        print_results : bool, optional
            Whether to print the extracted text to the console. The default is False.
        get_data : bool, optional
            Whether to extract word-specific data from the images. The default is False.
            Word-specific data includes the text, confidence, and coordinate data of each word in the image.

        Returns
        -------
        data or text : list<dict> or str
            -- If get_data is True, then the extracted word-specific data will be returned. This data includes the text,
            confidence, and coordinate data of each word in the image. This data will be returned as a list of dictionaries.
            each dictionary will contain the information for each word, which includes the keys 'left', 'top', 'right',
            'bottom', 'conf', and 'text'.
            -- If get_data is False, then the extracted text will be returned as a string. There will not be any other data
            returned other than the extracted text.

        Description
        -----------
        This function extracts text from an image or PDF file. The text is extracted using the tesseract API through
        the tesserocr library. The extracted text can either be printed to the console or saved to a text file in the
        output_path.

        If get_data is True, then word-specific data will be extracted from the images. This data includes the text,
        confidence, and coordinate data of each word in the image. This is what is printed to the console or saved to
        the text file.

        If neither the print_results or output_path parameters are set, then the text will be extracted but not 
        outputted (Effectively using system resources to do nothing). This function does not return any data, so it
        cannot be used to store the extracted text in a variable.
        """
        images = self.convert_file_to_images(file_path)
        if images is None:
            print(f"Could not extract text from {file_path}.")
            return None
        
        for i, image in enumerate(images):
            # Extract text or data from the image
            if get_data:
                # Extract the text and coordinate data from the image
                data = self.get_coordinate_data(image, psm)
                if output_path or print_results:
                    # Convert the returned data to text, and add a header to the text
                    text = 'left\ttop\tright\tbottom\tconf\ttext\n' + self.convert_coord_data_to_text(data)
            else:
                # Just extract the text from the image
                text = self.get_text(image, psm)

            # Print extracted information to console if print_results is True
            if print_results:
                print(text)

            # Save the extracted text to text file if output_path is provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # If there are multiple images, add a number to the output name
                if len(images) > 1:
                    name, ext = os.path.splitext(output_path)
                    new_output_path = name + f'_{i}' + ext
                else:
                    new_output_path = output_path
                with open(new_output_path, 'w') as f:
                    f.write(text)

        return data if get_data else text

    

    def extract_from_list(self, input_list, output_dir=None, print_results=False, get_data=False, psm=PSM.AUTO):
        """
        Parameters
        ----------
        input_list : list<str>
            A list of file paths to the images or PDFs to extract text from.
        output_dir : str, optional
            The directory to save the extracted text files to. The default is None (no text files will be saved).
        print_results : bool, optional
            Whether to print the extracted text to the console. The default is False.
        get_data : bool, optional
            Whether to extract word-specific data from the images. The default is False.
            Word-specific data includes the text, confidence, and coordinate data of each word in the image.

        Returns
        -------
        None

        Description
        -----------
        This function extracts text from a list of image or PDF file paths. The text is extracted using the tesseract
        API through the tesserocr library. The extracted text can either be printed to the console or saved to a text
        file in the output_dir directory. This function will also print the time taken to extract the from every file.
        
        If get_data is True, then word-specific data will be extracted from the images. This data includes the text,
        confidence, and coordinate data of each word in the image. This is what is printed to the console or saved to
        the text file.

        If the input_list contains non-image or non-pdf files, those files will be ignored and skipped.

        If neither the print_results or output_dir parameters are set, then the text will be extracted but not 
        outputted (Effectively using system resources to do nothing). This function does not return any data, so it
        cannot be used to store the extracted text in a variable.

        This function will use the seg_func and clean_image_func functions provided to the TextExtractor class to 
        segment and clean the images before using tesseract to extract the text. The changing of these functions must
        be done using the TextExtractor class object, not this function.
        """
        start_time = time.time()

        
        for file_name in input_list:
            # Convert the file to into a list of images (could be multiple pages if PDF)
            images = self.convert_file_to_images(file_name)
            if images is None:
                print(f"Could not extract text from {file_name}.")
                continue

            # Loop through each image
            for i, image in enumerate(images):
                # Extract text or data from the image
                if get_data:
                    # Extract the text and coordinate data from the image
                    data = self.get_coordinate_data(image, psm)
                    # Convert the returned data to text, and add a header to the text
                    text = 'left\ttop\tright\tbottom\tconf\ttext\n' + self.convert_coord_data_to_text(data)
                else:
                    # Just extract the text from the image
                    text = self.get_text(image, psm)

                # Print extracted information to console if print_results is True
                if print_results:
                    print("\n"+"#"*50)
                    print(f"Extracted text from {file_name}")
                    print("#"*50)
                    print(text)
                    print("#"*50)
                    print("End of extracted text.")
                    print("#"*50+"\n")

                # Save the extracted text to text file if output_dir is provided
                if output_dir:
                    file_name = os.path.basename(file_name)
                    if len(images) > 1:
                        save_path = os.path.join(output_dir, f'{file_name}_{i}.txt')
                    else:
                        save_path = os.path.join(output_dir, f'{file_name}.txt')

                    os.makedirs(os.path.dirname(save_path), exist_ok=True)   
                    with open(save_path, 'w') as f:
                        f.write(text)

        print(f"Time taken: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    from argparse import ArgumentParser
    # Parse the arguments
    parser = ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-d', '--directory', help='Path to the directory containing the images or PDFs to extract text from')
    group.add_argument('-f', '--file', help='Path to the image or PDF file')
    parser.add_argument('-o', '--output', help='Path to the directory to save the extracted text files to')
    parser.add_argument('--print', action='store_true', help='Print the extracted text to the console')
    parser.add_argument('--get_data', action='store_true', help='Extract word-specific data from the images')
    args = parser.parse_args()

    if not args.output and args.directory:
        print("No output or print arguments provided. No text will be extracted.")
        exit(1)

    # Print if neither print or output is set
    print_text = True if not args.print and not args.output else args.print

    # Import this here because it is the only place it is used
    from ImageProcessor import ImageProcessor
    clean_image_func = ImageProcessor() # Use the default ImageProcessor class to clean the images


    # Define the accepted file types
    accepted_file_types = ('.png', '.jpg', '.jpeg', '.jpe', '.webp', '.bmp', '.webp', '.dib', '.pxm', '.pgm',
                            '.pbm', '.pnm', '.pdf')

    # Need to initialize the API to extract text with the TextExtractor class
    with tesserocr.PyTessBaseAPI() as api:
        api.SetVariable("debug_file", "/dev/null")
        api.SetVariable('tessedit_char_blacklist', '|{}()><\\©')

        text_extractor = TextExtractor(api, clean_image_func=clean_image_func)

        if args.file:
            if not os.path.exists(args.file) and not args.file.lower().endswith(accepted_file_types):
                print(f"Invalid file: {args.file}")
                exit(1)

            # Extract text from the file
            text_extractor.extract_from_file(args.file, output_path=args.output, print_results=print_text,
                                             get_data=args.get_data)
        elif args.directory:
            if not os.path.isdir(args.directory):
                print(f"Invalid directory: {args.directory}")
                exit(1)

            # Get the list of image/pdf files in the directory
            file_list = []
            for file in os.listdir(args.directory):
                if file.lower().endswith(accepted_file_types):
                    file_path = os.path.join(args.directory, file)
                    file_list.append(file_path)

            # Extract text from the list of files
            text_extractor.extract_from_list(file_list, output_dir=args.output, print_results=print_text,
                                             get_data=args.get_data)
            