import os
import re
import utils
from ImageProcessor import ImageProcessor
from TextExtractor import TextExtractor
from ImageCropper import ImageCropper


class Pattern:
    def __init__(
            self,
            name: str = None,
            coordinates: tuple[int,int,int,int] = None,
            search_pattern: str = None,
            search_group: int = 0,
            not_pattern: str = None,
            match_pattern: str = None,
            match_group = 0
    ):
        self.name = name
        self.coordinates = coordinates
        self.search_pattern = search_pattern
        self.search_group = search_group
        self.not_pattern = not_pattern
        self.match_pattern = match_pattern
        self.match_group = match_group

    def __repr__(self):
        return f'Pattern(name={self.name}, coordinates={self.coordinates}, search_pattern={self.search_pattern}, search_group={self.search_group}, not_pattern={self.not_pattern}, match_pattern={self.match_pattern}, match_group={self.match_group})'

    def __str__(self) -> str:
        return self.__repr__()
    
    def is_coordinate_specific(self):
        return self.coordinates is not None


class Parser:
    def __init__(self):
        self.paragraph_format=True
        self.patterns: list[Pattern] = []
        self.parsed_fields: dict[str, str] = {}
        self.includes_coordinates = False
    
    def add_pattern(self, pattern: Pattern):
        """
        Patterns are added to the parser. If a pattern with the same name already exists, it will be overwritten.
        """
        for index, existing_pattern in enumerate(self.patterns):
            if existing_pattern.name == pattern.name:
                print(f"A pattern with the name '{pattern.name}' already exists. Overwriting...")
                self.patterns[index] = pattern
                return
        
        # No duplicates. Add the pattern to the list
        self.patterns.append(pattern)
        self.check_for_coordinates() # Update the coordinate flag
    
    def clear_patterns(self):
        self.patterns = []
    
    def check_for_coordinates(self):
        """
        Make sure the parser knows if there are any coordinate specific patterns
        Since the possibility exists that the only pattern with coordinates in a given parser
        could be overwritten so that it no longer has coordinates, we need to check all patterns
        every time a new pattern is added. 

        Returns:
            bool: True if the parser includes coordinate specific patterns, False
                otherwise
        """
        self.includes_coordinates = False
        for pttrn in self.patterns:
            if pttrn.is_coordinate_specific():
                self.includes_coordinates = True
                break
    
    def has_coordinate_patterns(self):
        self.check_for_coordinates()
        return self.includes_coordinates

    def get_coordinate_set(self):
        return set([pattern.coordinates for pattern in self.patterns if pattern.is_coordinate_specific()])
        
    def parse(self, text:str, pattern: Pattern):
        if not pattern.match_pattern:
            print(f'No match pattern provided for field {pattern.name}. Skipping...')
            return
        if pattern.search_pattern:
            # Search for the search pattern and extract the group
            # This is the string that will be searched for the match pattern
            match = re.search(pattern.search_pattern, text)
            if match:
                text = match.group(pattern.search_group)
        elif pattern.not_pattern:
            # If there is a not pattern, check if the text matches the not pattern
            # This means we have a false match, and should skip this field
            match = re.search(pattern.not_pattern, text)
            if match:
                return
        
        # Finally, search for the match pattern
        match = re.search(pattern.match_pattern, text)
        if match:
            self.parsed_fields[pattern.name] = match.group(pattern.match_group)
    
    def get_parsed_fields(self):
        return self.parsed_fields
    
    def clear_parsed_fields(self):
        self.parsed_fields = {}
    
    def get_parsed_text(self):
        if self.paragraph_format:
            return '\n'.join(f"{key}: {value}" for key, value in self.parsed_fields.items())
        return ' '.join(f"{key}: {value}" for key, value in self.parsed_fields.items())

def extract_and_parse_file(file: str, text_extractor: TextExtractor, parser: Parser):
    # If the allow_newlines flag is set to False, then that means the text will be parsed as a single paragraph
    parser.paragraph_format = not text_extractor.allow_newlines
    
    # Get image(s) from the file path
    images = utils.convert_file_to_images(file, use_PIL_data_type=True)

    cropped_image_texts = {} # Used for memoization: store cropped image texts to avoid reprocessing duplicate coordinates

    # Check if any crops are needed
    if parser.has_coordinate_patterns():
        coordinates = parser.get_coordinate_set() # Get unique set of coordinates from parser
        cropper = ImageCropper() # Initialize the cropper
        cropper.add_multiple_segments(coordinates) # Add the coordinates to the cropper
        # cropper is now ready to have images passed to it to crop them according to the coordinates.


    # Loop through the images (might only be 1) and extract the text
    for image in images:
        # Original text for patterns that are not coordinate specific
        full_text = text_extractor.get_text(image)
        # Get dictionary of cropped images mapped to their coordinates
        cropped_images = cropper.crop(image)
        # Get dictionary of cropped image texts mapped to their coordinates
        cropped_image_texts = {coordinates: text_extractor.get_text(cropped_images[coordinates]) for coordinates in cropped_images}
        for pattern in parser.patterns:
            if pattern.is_coordinate_specific():
                text = cropped_image_texts[pattern.coordinates]
                # else:
                    # cropped_image_texts[pattern.coordinates] = text # Store the cropped text for future reference

                parser.parse(text, pattern) # Parse the coordinate specific text for the specific pattern
            else: # Parse the general text for the specific pattern
                parser.parse(full_text, pattern)

    return parser.get_parsed_text()
        



if __name__ == '__main__':
    # Create file path to the example form
    file_loc = os.path.abspath(__file__)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(file_loc)))
    pdf_path = os.path.join(root_dir, 'example-forms',
                            'emergency-medical-form.pdf')

    bbox = (310, 335, 790, 565)

    parser = Parser()
    parser.add_pattern(
        Pattern(
            name = 'First Name', 
            coordinates=bbox,
            match_pattern=r'(First)(.*)', 
            match_group=2
        )
    )

    clean_image_func = ImageProcessor(deskew=True, global_binarize=True)

    from tesserocr import PyTessBaseAPI

    with PyTessBaseAPI() as api:
        text_extractor = TextExtractor(api, clean_image_func=clean_image_func)
        text = extract_and_parse_file(pdf_path, text_extractor, parser)
        print(text)

        # text_extractor.get_text(images[0])
