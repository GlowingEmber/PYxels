import argparse
from matplotlib.colors import is_color_like
from PIL import Image, ImageOps
import numpy as np
import struct
import default_blocks

parser = argparse.ArgumentParser(
    prog="PYxel"
)

VALID_PARAMETERS = {
    "block": ["2px", "3px", "4px"],
    "background": ["opaque", "transparent"],
    "bg_mode": ["RGB", "RGBA"]
}

########################### argparse

# required arguments
parser.add_argument('input_file')
# optional arguments
parser.add_argument('-b', '--block', default="2px", choices=VALID_PARAMETERS["block"])
parser.add_argument('-m', '--matrix', default=None)
parser.add_argument('-g', '--background', default="transparent", choices=VALID_PARAMETERS["background"])
parser.add_argument('-c', '--color', nargs="*")
# supposed to set buffer around resulting image [not working]
parser.add_argument('--buffer', default=0, type=(lambda b: int(b)))
parser.add_argument('--bg_mode', default="RGBA", choices=VALID_PARAMETERS["bg_mode"])

def __color_valid_check(color):
    if color == None:
        args_dict["color"] = "#fff"
        return
    if len(color) == 1 and is_color_like(color[0]):
        return
    # disabled until tricoloration is fixed
    # if len(color) == 3 and all([is_color_like(c) for c in color]):
    #     return
    raise argparse.ArgumentTypeError(f'Invalid color input{'(s)' if len(color) > 1 else ''}: {color}')

def __matrix_valid_check(matrix):
    if matrix != None and (row_count := len(matrix)) != 2:
        raise argparse.ArgumentTypeError(f'Invalid matrix input: Expected 2 rows, given {row_count}')

args_dict = vars(parser.parse_args())
__color_valid_check(args_dict["color"])
__matrix_valid_check(args_dict["matrix"])

########################### initial setup

INPUT_IMAGE = Image.open("inputs/%s" % args_dict["input_file"])
INPUT_HEIGHT = INPUT_IMAGE.height
INPUT_WIDTH = INPUT_IMAGE.width

def select_input(current_pixel):
    if (len(current_pixel) <= 3 or current_pixel[3] != 0) and list(current_pixel[:3]) == [0,0,0]:
            return True
    return False

coords = [(x,y) for y in range(0, INPUT_HEIGHT) for x in range(0, INPUT_WIDTH)]
coords_dict = {(x,y):(0,0,0,255) for (x,y) in coords if select_input(INPUT_IMAGE.getpixel((x,y)))}

format_dict = default_blocks.get_format(args_dict["block"])
format_dict |= args_dict

print(format_dict)

def __transform_coords(coords, format):
    x = coords[0]
    y = coords[1]
    trans_matrix = format_dict["t_matrix"]
    new_x = (trans_matrix[0][0] * x + trans_matrix[0][1] * y) + format_dict["buffer"]
    new_y = (trans_matrix[1][0] * x + trans_matrix[1][1] * y) + format_dict["buffer"]
    return [new_x, new_y]

# calculate new "adjusted" coordinates with transformation matrix
adjusted_coords_dict = {}
for coords in coords_dict:
    new_coords = __transform_coords(coords, format_dict["block"])
    adjusted_coords_dict[(new_coords[0], new_coords[1])] = coords_dict[coords]

x_only = list(zip(*adjusted_coords_dict.keys()))[0] # unzips with zip(*x)
y_only = list(zip(*adjusted_coords_dict.keys()))[1] # unzips with zip(*x)
x_max, x_min, y_max, y_min = max(x_only), min(x_only), max(y_only), min(y_only) # finds boundaries of image

origin_x = 0
for coords in adjusted_coords_dict.keys():
    if coords[1] == y_min:
        origin_x = coords[0]
        break

# calculate distance from leftmost point to origin point (for the backmost cube)
origin_width = 0 - x_min

# adjust widths by origin width
x_max += origin_width
x_min += origin_width
origin_x += origin_width

# output coordinates
final_coords_dict = {}
for coords in adjusted_coords_dict:
    final_coords_dict[(coords[0] + origin_width, coords[1])] = adjusted_coords_dict[(coords[0], coords[1])]
    # unshifted version (for testing)
    # final_coords_dict[(coords[0], coords[1])] = adjusted_coords_dict[(coords[0], coords[1])]

########################### creating final image

block_unit = Image.open("formats/" + format_dict["block_img_file"])

output_height = (y_max - y_min) + block_unit.height + (format_dict["buffer"] * 2)
output_width = (x_max - x_min) + block_unit.width + (format_dict["buffer"] * 2)

final_image = Image.new(mode=format_dict["bg_mode"], size=(output_width, output_height))

# adding each block unit onto the final image
for coords in final_coords_dict:
    Image.Image.paste(final_image, block_unit, coords, mask=block_unit)

###########################

MAX_COLORS = 256 # final_image.getcolors(MAX_COLORS) returns 0 if (# of colors in img > MAX_COLORS)
color_list = list(zip(*final_image.getcolors(MAX_COLORS)))[1] # list of all colors in the image
color_list = np.asarray(color_list) # convert from list to np array
non_alpha_colors = (color_list[:,3] != 0) # remove colors with an alpha of 0
color_array = color_list[non_alpha_colors][:,:3] # can remove [:,:3] to include alpha in the array

print(color_array)

# sort color_array by lightest colors
light_to_dark_order = np.asarray([])
for color in color_array:
    light_to_dark_order = np.append(light_to_dark_order, np.sum(color))
light_to_dark_order = np.argsort(light_to_dark_order)[::-1] # [::-1] reverses the list
color_array_sorted = color_array[light_to_dark_order]

# set main three colors
primary = secondary = tertiary = (0,0,0)
if 0 < len(color_array_sorted): primary = tuple(color_array_sorted[0])
if 1 < len(color_array_sorted): secondary = tuple(color_array_sorted[1])
if 2 < len(color_array_sorted): tertiary = tuple(color_array_sorted[2])

# #######################
# # adjust color
# #######################

if len(format_dict["color"]) == 1:
    final_image = ImageOps.colorize(image=final_image.convert('L'), black="black", white=format_dict["color"][0])

elif len(format_dict["color"]) == 3:
    data = np.array(final_image)
    # perform transpose then set R, G, B, and A to each of the 4 rows
    reds, greens, blues, alphas = data.T
    nonzero_alpha_filter = (alphas != 0) & (reds == 255)
    primary_filter = (alphas != 0) & (reds == primary[0]) & (greens == primary[1]) & (blues == primary[2])
    secondary_filter = (alphas != 0) & (reds == secondary[0]) & (greens == secondary[1]) & (blues == secondary[2])
    tertiary_filter = (alphas != 0) & (reds == tertiary[0]) & (greens == tertiary[1]) & (blues == tertiary[2])

    data[:,:,:-1][primary_filter.T] = struct.unpack("BBB", bytes.fromhex(format_dict["color"][0]))
    data[:,:,:-1][secondary_filter.T] = struct.unpack("BBB", bytes.fromhex(format_dict["color"][1]))
    data[:,:,:-1][tertiary_filter.T] = struct.unpack("BBB", bytes.fromhex(format_dict["color"][2]))
    final_image=Image.fromarray(data)

if format_dict["background"] == "transparent":
    final_image = final_image.convert("RGBA")
    data = np.array(final_image)
    reds, greens, blues, alphas = data.T
    black_background_filter = (reds == 0) & (greens == 0) & (blues == 0)
    data[:,:,:][black_background_filter.T] = (0,0,0,0)
    final_image=Image.fromarray(data)


if format_dict["bg_mode"] == "rgb":
    final_image = final_image.convert("RGB")

final_image.show()
