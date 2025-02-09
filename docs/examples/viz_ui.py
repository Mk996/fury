# -*- coding: utf-8 -*-
"""
===============
User Interfaces
===============

This example shows how to use the UI API. We will demonstrate how to create
several FURY UI elements, then use a list box to toggle which element is shown.

First, a bunch of imports.
"""

import numpy as np

import fury

###############################################################################
# Shapes
# ======
#
# Let's start by drawing some simple shapes. First, a rectangle.

rect = fury.ui.Rectangle2D(size=(200, 200), position=(400, 300), color=(1, 0, 1))

###############################################################################
# Then we can draw a solid circle, or disk.

disk = fury.ui.Disk2D(outer_radius=50, center=(500, 500), color=(1, 1, 0))

###############################################################################
# Add an inner radius to make a ring.

ring = fury.ui.Disk2D(
    outer_radius=50, inner_radius=45, center=(500, 300), color=(0, 1, 1)
)

###############################################################################
# Image
# =====
#
# Now let's display an image. First we need to fetch some icons that are
# included in FURY.

fury.data.fetch_viz_icons()

###############################################################################
# Now we can create an image container.

img = fury.ui.ImageContainer2D(
    img_path=fury.data.read_viz_icons(fname="home3.png"), position=(450, 350)
)

###############################################################################
# Panel with buttons and text
# ===========================
#
# Let's create some buttons and text and put them in a panel. First we'll
# make the panel.

panel = fury.ui.Panel2D(size=(300, 150), color=(1, 1, 1), align="right")
panel.center = (500, 400)

###############################################################################
# Then we'll make two text labels and place them on the panel.
# Note that we specify the position with integer numbers of pixels.

text = fury.ui.TextBlock2D(text="Click me")
text2 = fury.ui.TextBlock2D(text="Me too")
panel.add_element(text, (50, 100))
panel.add_element(text2, (180, 100))

###############################################################################
# Then we'll create two buttons and add them to the panel.
#
# Note that here we specify the positions with floats. In this case, these are
# percentages of the panel size.


button_example = fury.ui.Button2D(
    icon_fnames=[("square", fury.data.read_viz_icons(fname="stop2.png"))]
)

icon_files = []
icon_files.append(("down", fury.data.read_viz_icons(fname="circle-down.png")))
icon_files.append(("left", fury.data.read_viz_icons(fname="circle-left.png")))
icon_files.append(("up", fury.data.read_viz_icons(fname="circle-up.png")))
icon_files.append(("right", fury.data.read_viz_icons(fname="circle-right.png")))

second_button_example = fury.ui.Button2D(icon_fnames=icon_files)

panel.add_element(button_example, (0.25, 0.33))
panel.add_element(second_button_example, (0.66, 0.33))

###############################################################################
# We can add a callback to each button to perform some action.


def change_text_callback(i_ren, _obj, _button):
    text.message = "Clicked!"
    i_ren.force_render()


def change_icon_callback(i_ren, _obj, _button):
    _button.next_icon()
    i_ren.force_render()


button_example.on_left_mouse_button_clicked = change_text_callback
second_button_example.on_left_mouse_button_pressed = change_icon_callback

###############################################################################
# Cube and sliders
# ================
#
# Let's add a cube to the scene and control it with sliders.


cube = fury.actor.cube(
    centers=np.array([[15, 0, 0]]),
    colors=np.array([[0, 0, 1]]),
    scales=np.array([[20, 20, 20]]),
    directions=np.array([[0, 0, 1]]),
)

###############################################################################
# Now we'll add three sliders: one circular and two linear.

ring_slider = fury.ui.RingSlider2D(
    center=(740, 400), initial_value=0, text_template="{angle:5.1f}°"
)

line_slider_x = fury.ui.LineSlider2D(
    center=(500, 250),
    initial_value=0,
    min_value=-10,
    max_value=10,
    orientation="horizontal",
)

line_slider_y = fury.ui.LineSlider2D(
    center=(650, 350),
    initial_value=0,
    min_value=-10,
    max_value=10,
    orientation="vertical",
)

###############################################################################
# We can use a callback to rotate the cube with the ring slider.


def rotate_cube(slider):
    angle = slider.value
    previous_angle = slider.previous_value
    rotation_angle = angle - previous_angle
    cube.RotateX(rotation_angle)


ring_slider.on_change = rotate_cube

###############################################################################
# Similarly, we can translate the cube with line sliders.
# We use global variables to keep track of the position of the cube.

cube_x = 0
cube_y = 0


def translate_cube_x(slider):
    global cube_x, cube_y
    cube_x = slider.value
    cube.SetPosition(cube_x, cube_y, 0)


def translate_cube_y(slider):
    global cube_x, cube_y
    cube_y = slider.value
    cube.SetPosition(cube_x, cube_y, 0)


line_slider_x.on_change = translate_cube_x
line_slider_y.on_change = translate_cube_y

###############################################################################
# Range Slider
# ============
#
# Finally, we can add a range slider. This element is composed of two sliders.
# The first slider has two handles which let you set the range of the second.

range_slider_x = fury.ui.RangeSlider(
    line_width=8,
    handle_side=25,
    range_slider_center=(450, 450),
    value_slider_center=(450, 350),
    length=150,
    min_value=0,
    max_value=10,
    font_size=18,
    range_precision=2,
    value_precision=4,
    shape="square",
)

range_slider_y = fury.ui.RangeSlider(
    line_width=8,
    handle_side=25,
    range_slider_center=(750, 400),
    value_slider_center=(650, 400),
    length=150,
    min_value=0,
    max_value=10,
    font_size=18,
    range_precision=2,
    value_precision=4,
    orientation="vertical",
    shape="square",
)
###############################################################################
# Select menu
# ============
#
# We just added many examples. If we showed them all at once, they would fill
# the screen. Let's make a simple menu to choose which example is shown.
#
# We'll first make a list of the examples.

examples = [
    [rect],
    [disk, ring],
    [img],
    [panel],
    [ring_slider, line_slider_x, line_slider_y],
    [range_slider_x, range_slider_y],
]

###############################################################################
# Now we'll make a function to hide all the examples. Then we'll call it so
# that none are shown initially.


def hide_all_examples():
    for example in examples:
        for element in example:
            element.set_visibility(False)
    cube.SetVisibility(False)


hide_all_examples()

###############################################################################
# To make the menu, we'll first need to create a list of labels which
# correspond with the examples.

values = [
    "Rectangle",
    "Disks",
    "Image",
    "Button Panel",
    "Line & Ring Slider",
    "Range Slider",
]

###############################################################################
# Now we can create the menu.

listbox = fury.ui.ListBox2D(
    values=values, position=(10, 300), size=(300, 200), multiselection=False
)

###############################################################################
# Then we will use a callback to show the correct example when a label is
# clicked.


def display_element():
    hide_all_examples()
    example = examples[values.index(listbox.selected[0])]
    for element in example:
        element.set_visibility(True)
    if values.index(listbox.selected[0]) == 4:
        cube.SetVisibility(True)


listbox.on_change = display_element

###############################################################################
# Show Manager
# ==================================
#
# Now that all the elements have been initialised, we add them to the show
# manager.

current_size = (800, 800)
show_manager = fury.window.ShowManager(size=current_size, title="FURY UI Example")

show_manager.scene.add(listbox)
for example in examples:
    for element in example:
        show_manager.scene.add(element)
show_manager.scene.add(cube)
show_manager.scene.reset_camera()
show_manager.scene.set_camera(position=(0, 0, 200))
show_manager.scene.reset_clipping_range()
show_manager.scene.azimuth(30)

# To interact with the UI, set interactive = True
interactive = False

if interactive:
    show_manager.start()

fury.window.record(
    scene=show_manager.scene, size=current_size, out_path="viz_fury.ui.png"
)
