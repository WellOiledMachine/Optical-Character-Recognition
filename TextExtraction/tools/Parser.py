import os
import re
import utils
from ImageProcessor import ImageProcessor
from TextExtractor import TextExtractor

class text_parser_args:
    def __init__(self):
        self.simple_patterns = {}
        self.coord_specific_patterns = {}

    def add_simple_pattern(self, name, pattern, match_group=0):
        # TODO: Add a check to make sure the same name isn't being used twice
        # Or maybe dont. It will just overwrite the old pattern
        self.simple_patterns[name] = (pattern, match_group)

    def add_coord_specific_pattern(self, name, coordinates, pattern, match_group=0):
        """
        Parameters
        ----------
        name : str
            The name of the pattern to be matched.
        coordinates : list or tuple
            A list of length 4 that represents the coordinates of the area in the image to search for the pattern.
            The list should be in the form (x1, y1, x2, y2), where x1, y1 is the top left corner and x2, y2 is the
            bottom right corner of the area.
        pattern : str
            The regular expression pattern to search for in the specified area.
        match_group : int, optional
            The index of the match group to return. The default is 0, which returns the entire match.
            
        Description
        -----------
        Adds a pattern that is specific to a certain area of the image. This will allow you to use the coordinates in the 
        coordinates tuple to crop the image, extract text from the cropped image, and then search for the pattern in that
        extracted text."""
        if name in self.coord_specific_patterns:
            print(f'Warning: pattern already exists with name {name}. Overwriting...')
        
        if not isinstance(coordinates, tuple):
            if len(coordinates) != 4:
                raise ValueError('coordinates list must have a length of 4')
            
            try:
                coordinates = tuple(coordinates)
            except:
                raise ValueError('coordinates must be a tuple or a list')
        self.coord_specific_patterns[name] = (coordinates, pattern, match_group)

    def add_complex_pattern(self, name, search_pattern, not_pattern, match_pattern, match_group=0):
        pass
        

from ImageCropper import ImageCropper

def extract_and_parse(text_extractor, parser_args, images):
    if not isinstance(text_extractor, TextExtractor):
        raise TypeError('text_extractor must be an instance of the TextExtractor class')
    
    parsed_text = '' # Initialize the parsed text string

    coord_patterns = parser_args.coord_specific_patterns
    # Initialize Cropper outside of loop if a cropper is needed
    if len(coord_patterns) != 0:
        # Create an image cropper that will use all of the coordinate information to crop images
        cropper = ImageCropper()
        
        # Add all of the coordinate sets to the cropper
        for name, (coordinates, pattern, match_group) in coord_patterns.items():
            cropper.add_segment(coordinates)
    

    for image in images:
        # Check if there are any simple patterns to match
        if len(parser_args.simple_patterns) != 0:

            # Use normal text extraction to get the text from the file
            input_text = text_extractor.get_text(image)
            parsed_text += '########## SIMPLE PATTERN MATCHES ##########\n'
            
            # Loop through the simple patterns and try to find a match in the input text
            for name, (pattern, match_group) in parser_args.simple_patterns.items():
                match = re.search(pattern, input_text, re.DOTALL | re.MULTILINE)
                if match:
                    parsed_text += f'{name}: {match.group(match_group)}\n'
                else:
                    parsed_text += f'{name}: PATTERN NOT FOUND\n'
        
        # Check if there are any coordinate specific patterns to match
        if len(coord_patterns) != 0:
            # Use the cropper to get the cropped images
            crops = cropper(image)


            # import matplotlib.pyplot as plt
# 
            # for value in crops.values():
                # plt.imshow(value, cmap='gray')
                # plt.show()

            # Join the cropped images with the coord_patterns to create a dictionary of coordinates
            # for keys that map to the cropped images and the pattern list to use in parsing
            joined_dict = {}
            for name, (coordinates, pattern, match_group) in coord_patterns.items():
                if coordinates in crops:
                    joined_dict[name] = (crops[coordinates], pattern, match_group)
            
            # Loop through the joined dictionary and extract text from the cropped images
            # Then search for the patterns in the extracted text
            parsed_text += '########## COORDINATE SPECIFIC PATTERN MATCHES ##########\n'
            for name, (crop, pattern, match_group) in joined_dict.items():
                extracted_text = text_extractor.get_text(crop)
                print(extracted_text)
                match = re.search(pattern, extracted_text, re.DOTALL | re.MULTILINE)
                if match:
                    parsed_text += f'{name}: {match.group(match_group)}\n'
                else:
                    parsed_text += f'{name}: PATTERN NOT FOUND\n'
        
    return parsed_text
        


if __name__ == '__main__':
    # Create file path to the example form
    file_loc = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))
    pdf_path = os.path.join(root_dir, 'example-forms', 'emergency-medical-form.pdf')

    images = utils.convert_file_to_images(pdf_path, use_PIL_data_type=True)
    
    bbox = (310, 335, 790, 565)

    parser_args = text_parser_args()
    parser_args.add_simple_pattern('hehe Words', r'example')
    parser_args.add_coord_specific_pattern('Name', bbox, r'(First)(.*)', 2)
    # parser_args.add_coord_specific_pattern('Name', (100, 100, 200, 200), r'Name: (.+)')


    # text = "For example, blah blah blah"
    
    # match = re.search(r'example', text)
    # print(match.group())
    clean_image_func = ImageProcessor(deskew=True, global_binarize=True )

    from tesserocr import PyTessBaseAPI

    with PyTessBaseAPI() as api:
        text_extractor = TextExtractor(api, clean_image_func=clean_image_func)
        text = extract_and_parse(text_extractor, parser_args, images)
        print(text)
  
        # text_extractor.get_text(images[0])
