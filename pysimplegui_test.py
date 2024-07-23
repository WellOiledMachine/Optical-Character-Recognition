from io import BytesIO
import base64
import PySimpleGUI as sg
from PIL import Image, ImageTk
import os

"""
This code was borrowed from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Graph_Drag_Rectangle.py
and modified. It allows the user to draw a rectangle on an image and get the coordinates of the rectangle. Unfortunately,
the window is not big enough to display the entire image, so some scrolling would need to be implemented for this to work
the way we need it to. It does not seem possible to just display the image/graph small, but with a coordinate size that still
allows the entire image to be displayed and the coordinates to be accurate. This is a limitation of PySimpleGUI.
"""


image_file =  os.path.join(os.getcwd(), "test_images", "about_pearson.jpg")

GRAPH_SIZE = 500

layout = [[sg.Graph(
    canvas_size=(GRAPH_SIZE, GRAPH_SIZE),
    graph_bottom_left=(0, 0),
    graph_top_right=(GRAPH_SIZE, GRAPH_SIZE),
    key="-GRAPH-",
    change_submits=True,  # mouse click events
    background_color='lightblue',
    drag_submits=True), ],
    [sg.Text(key='info', size=(60, 1))]]

window = sg.Window("draw rect on image", layout, finalize=True)
# get the graph element for ease of use later
graph = window["-GRAPH-"]  # type: sg.Graph

# Open Image file
image = Image.open(image_file)

# Convert image to base64
buffered = BytesIO()
image.save(buffered, format="PNG")  # PNG format is recommended
img_str = base64.b64encode(buffered.getvalue()).decode()

# Draw image on the graph
graph.draw_image(data=img_str, location=(0,GRAPH_SIZE))
dragging = True
start_point = end_point = prior_rect = None

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break  # exit

    if event == "-GRAPH-":  # if there's a "Graph" event, then it's a mouse
        x, y = values["-GRAPH-"]
        if not dragging:
            start_point = (x, y)
            dragging = True
        else:
            end_point = (x, y)
        if prior_rect:
            graph.delete_figure(prior_rect)
        if None not in (start_point, end_point):
            prior_rect = graph.draw_rectangle(start_point, end_point, line_color='red')

    elif event.endswith('+UP'):  # The drawing has ended because mouse up
        info = window["info"]
        info.update(value=f"grabbed rectangle from {start_point} to {end_point}")
        start_point, end_point = None, None  # enable grabbing a new rect
        dragging = False

    else:
        print("unhandled event", event, values)