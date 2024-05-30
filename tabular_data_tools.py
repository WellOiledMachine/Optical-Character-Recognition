# Author: Cody Sloan
# Project: Optical Character Recognition
# This script contains functions to modify and filter tabular data extracted from tesseract.

def filter_low_conf_extraction(data, conf_threshold = 10):
    """
    Parameters
    ----------
    text : str
        The extracted tabular data string from tesseract.
    conf_threshold : int, optional
        The confidence threshold to filter out low confidence text. The default is 10.
        
    Returns
    -------
    filtered_text : str
        The extracted tabular data string from tesseract with low confidence text removed.
    
    Description
    -----------
    This function filters out tesseract extracted text based on the confidence level of each word. Tesseract outputs 
    its confidence level for each word extracted from the image when using tabular extraction. This confidence level
    is a percentage value that represents how confident tesseract is that the word was extracted correctly. So this
    function filters out any text that has a confidence level below the specified threshold.
    """
    # Convert the string into a list of lists, where each inner list is a row from the tabular data, and each element
    # in the inner list is an element from the row.
    lines = data.split('\n')
    table = [line.split('\t') for line in lines if line]
    
    # Save the header row and remove it from the table
    header = table[0]
    table = table[1:]
    
    # Filter out any rows that have a confidence level below the threshold
    filtered_table = [row for row in table if int(row[10]) >= conf_threshold]
    
    # Add the header row back to the filtered table
    filtered_table.insert(0, header)

    # Convert the filtered table back into a string
    filtered_lines = []
    for row in filtered_table:
        filtered_lines.append('\t'.join(row))
    
    filtered_text = '\n'.join(filtered_lines)
    
    return filtered_text 


def left_is_close(first_line, second_line, distance):
    """
    Parameters
    ----------
    first_line : list
        The first row from the tabular data to compare.
    second_line : list
        The second row from the tabular data to compare.
    distance : int
        The distance threshold to determine if two words are close.
        
    Returns
    -------
    bool
        Whether the leftmost coordinates of the two lines are within the distance threshold.
        
    Description
    -----------
    This function determines if the leftmost coordinates of two words are within a certain distance of each other. This
    is used to determine if two words are close enough to be combined into a single line in the tabular data.
    """
    # First determine the leftmost text out of the two, then use that to 
    # check if the words should be joined together.
    if first_line[6] < second_line[6]:
        return (abs((first_line[6] + first_line[8]) - second_line[6]) <= distance)
    else: 
        return (abs((second_line[6] + second_line[8]) - first_line[6]) <= distance)

    
def top_is_close(first_line, second_line, distance):
    """
    Parameters
    ----------
    first_line : list
        The first row from the tabular data to compare.
    second_line : list
        The second row from the tabular data to compare.
    distance : int
        The distance threshold to determine if two words are close.
        
    Returns
    -------
    bool
        Whether the topmost coordinates of the two lines are within the distance threshold.
        
    Description
    -----------
    This function determines if the topmost coordinates of two words are within a certain distance of each other. This
    is used to determine if two words are close enough to be combined into a single line in the tabular data.
    """
    # Determine if the top coordinates of the two lines are within dist of
    # each other
    return (abs(first_line[7] - second_line[7]) <= distance)
    

def combine_lines(first_line, second_line):
    """
    Parameters
    ----------
    first_line : list
        The first row from the tabular data to combine.
    second_line : list
        The second row from the tabular data to combine.
        
    Returns
    -------
    combined_list : list
        The combined row of text from the two input rows.
        
    Description
    -----------
    This function combines two rows of tabular text extraction data into a single row. It combines the text from
    the two rows, and calculates the new coordinate information for those combined lines. It then returns the
    new row of text.
    """
    # Calculate the new coordinate information for combined text
    left = min(first_line[6], second_line[6])
    top = min(first_line[7], second_line[7])
    height = max(first_line[9], second_line[9])
    conf = (first_line[10] + second_line[10]) // 2
    
    # Ensure that the lists can be passed to this function in any order
    if left == first_line[6]:
        # Find the right most coordinate of either of the two words
        right_most = max(first_line[6] + first_line[8], second_line[6] + second_line[8])
        # Use the right most coordinate to calculate the width of the new text
        width = abs(right_most - first_line[6])
        text = f"{first_line[11]} {second_line[11]}"
    else:
        # Find the right most coordinate of either of the two words
        right_most = max(first_line[6] + first_line[8], second_line[6] + second_line[8])
        # Use the right most coordinate to calculate the width of the new text
        width = abs(right_most - second_line[6])
        text = f"{second_line[11]} {first_line[11]}"

    # Change the elements of the new list to all strings again, and return
    combined_list = first_line[:6].copy()
    combined_list.extend([left, top, width, height, conf, text])
    
    return combined_list


def transform_element(item):
    """
    Parameters
    ----------
    item : str
        The item to transform into a float or int.
    
    Returns
    -------
    item : str or float or int
        The converted item if it could be converted to a float or int, otherwise the original item.
        
    Description
    -----------
    This function attempts to convert a string to a number. It first tries to convert the string to a float, and if
    that works, it then tries to convert the float to an int. If the string cannot be converted to a float, it is
    returned as is. If it cannot be converted from a float to an int, it is returned as a float.
    """
    try:
        num = float(item)
    except (TypeError, ValueError):
        return item
    else:
        if num.is_integer():
            return int(num)
        else:
            return num


def realign_text(data, left_distance, top_distance):
    """
    Parameters
    ----------
    data : str
        The extracted tabular data string from tesseract.
    left_distance : int
        The distance threshold to determine if two words are close horizontally.
    top_distance : int
        The distance threshold to determine if two words are close vertically.
        
    Returns
    -------
    realigned_text : str
        The extracted tabular data string from tesseract with realigned text.
        
    Description
    -----------
    This function iterates over a string of tabular data extracted from tesseract and combines words that are
    considered 'close' to each other. It uses the left_distance and top_distance parameters to determine if two words
    are close enough to be combined into a single line. The pages of the lines are also checked to make sure that two
    words on different pages are not combined. It will iterate over the data as many times as necessary to ensure that
    all lines were realigned. It then returns the realigned tabular data string.
    """
    # Convert the string into a list of lists, where each inner list is a row from the tabular data, and each element
    # in the inner list is an element from the row.
    lines = data.split('\n')
    table = [line.split('\t') for line in lines if line]
    
    # Save the header row and remove it from the table
    header = table[0]
    table = table[1:]
    
    # Convert the elements of each list in the table to the correct data type
    table = [[transform_element(item) for item in row] for row in table]
    
    # Copy
    realigned = table.copy()
    # Keep track of whether or not any changes were made in the latest 
    # iteration. Initialize to True so the while-loop will start.
    modified = True
    # Continue realigning the text until no changes are made
    while modified:
        # Reset to false for beginning of loop
        modified = False
        # Compare every row to every other row only once. Do not compare a row 
        # to itself
        for index, item1 in enumerate(table):
            for item2 in table[index+1:]:
                # Check that the page of the two words are the same
                if item1[1] != item2[1]:
                    continue
                
                # Check if the two rows being compared are 'close'
                if top_is_close(item1, item2, top_distance) and left_is_close(item1, item2, left_distance):
                    # The realigned list is going to become shorter, so we need to
                    # ensure that the item we are comparing is still in the
                    # realigned list.
                    try:
                        modified = True # Changes have been made
                        # Get the positions of the two lines of text that will be
                        # combined
                        first_pos = realigned.index(item1)
                        second_pos = realigned.index(item2)
                    except ValueError:
                        # At least one of the lines were removed
                        continue

                    # Ensure that we combine the text in the right order
                    if int(item1[6]) < int(item2[6]):
                        realigned[first_pos] = combine_lines(item1, item2)
                        realigned.pop(second_pos)
                    else:
                        realigned[second_pos] = combine_lines(item1, item2)
                        realigned.pop(first_pos)
        # Update the table to the realigned list, so that we can keep realigning until completion
        table = realigned.copy()
        
    # Convert all elements in every row back to strings
    table = [[str(item) for item in row] for row in table]
                
    # Add the header row back to the filtered table
    table.insert(0, header)

    # Convert the filtered table back into a string
    realigned_lines = []
    for row in table:
        realigned_lines.append('\t'.join(row))
    
    realigned_text = '\n'.join(realigned_lines)
    
    return realigned_text
    
        