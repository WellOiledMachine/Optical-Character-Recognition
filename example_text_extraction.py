import tesserocr
from tools.TextExtractor import TextExtractor
from tools.ImageCropper import ImageCropper
from tools.image_preprocessing import ImagePreprocessor
import os
import cv2

# Set the path to the tesseract data directory
os.environ['TESSDATA_PREFIX'] = '/usr/share/tesseract-ocr/5/tessdata'

if __name__ == '__main__':
    # Set up the paths to the files
    image_path = 'test_images/SampleText.jpg'
    pdf_John = 'example-forms/emergency-medical-form.pdf'
    pdf_Alex = 'example-forms/emergency-medical-form-example.pdf'

    # using a text file just to test if the code will catch invalid file types and handle them correctly
    # this file shouldn't exist
    txt_path = 'emergency-medical-form.txt'


    filenames = [pdf_Alex, pdf_John, image_path, txt_path]


    # Need to initialize the API in the same thread as the one it will be used in
    with tesserocr.PyTessBaseAPI() as api:
        # Set the debug file to /dev/null to suppress the "Detected X diacritics" messages (and everything else)
        api.SetVariable("debug_file", "/dev/null")
        api.SetVariable('tessedit_char_blacklist', '|{}()><\\©')

        # Initialize the ImagePreprocessor
        clean_image = ImagePreprocessor(grayscale=None)

        text_extractor = TextExtractor(api, clean_image_func=clean_image)

        """1) Let's try just extracting text from all of the files in the list. Can also set get_data=True to get coordinate data.
        You can also specify an output directory to save the extracted .txt files to."""
        # You may want to comment the line below when you are done testing.
        text = text_extractor.extract_from_list(filenames, output_dir=None, print_results=True, get_data=False)


        """2) You can also extract text from a single image
        It should be noted that if get_data=True, the returned value will be a list of dictionaries. If you want to print
        the coordinate data, you have to use the print_results=True argument (or figure out how to print it yourself).
        You could also use the convert_coord_data_to_text method in the TextExtractor class."""
        # UNCOMMENT THE LINE BELOW

        # text = text_extractor.extract_from_file(pdf_John, output_name=None, print_results=False, get_data=False)
        # print(text)


        """3) You can also use a custom function to split your image into multiple parts and feed each of them into the
        OCR engine seperatetly. This can improve OCR accuracy for some images."""
        # UNCOMMENT THE LINES BELOW

        # def split_image_vertically(image, y):
        #     print("Splitting image vertically at y =", y)
        #     return image[:y], image[y:]
        
        # seg_func_args = {'y': 1545}
        # text_extractor.seg_func = split_image_vertically 
        # text_extractor.seg_func_args = seg_func_args
        
        # text = text_extractor.extract_from_file(pdf_John, output_name=None, print_results=True, get_data=False)

        """4) You may find that the accuracy of the extracted text is not good enough. You can try to improve the
        accuracy by cropping out the text segments and feeding them into the OCR engine seperately. This is what 
        tesseract does by default, but manually cropping the text segments can sometimes improve the accuracy.
        The get_tess_auto_segments method in the ImageCropper class will use tesseracts page segmentation analysis
        methods to grab cropped images of the automatically detected text segments. Feeding these back into tesseract
        for OCR can make sure that text is properly segmented (sometimes the first analysis is off), which can improve
        accuracy."""
        # UNCOMMENT THE LINES BELOW
        
        # # Read in the image
        # image = text_extractor.convert_file_to_images(pdf_John)[0]
        # clean_img = clean_image(image)
        #
        # cropper = ImageCropper()
        # # This is going to grab a lot of segments, and some may just have gibberish. Also, sometimes text is duplicated
        # # in different segments.
        # cropper.get_tess_auto_segments(clean_img, api)
        # cropped_images = cropper(clean_img)
        #
        # # Don't use TextExtractor.get_text for this because it will try to clean the images again.
        # text = ""
        # for img in cropped_images:
        #     api.SetImage(img)
        #     text += api.GetUTF8Text()
        #
        # print(text)        
