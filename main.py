from PIL import Image, ImageOps
import formats
import numpy as np

#######################
# issues/ideas
#######################
# does not work properly if source image does not start in the top left corner (Y NOT WORKING - check with sprite9)
# idea: create an 3d image of a square. then adjust its angle using a linear transformation to use as the pixelcube for custom matrices

#######################
# parameters
#######################
input_image = Image.open("inputs/eeh.png")
iso_type = "2px_base" # choose from formats.py
transparent_background = True # set to True for RGB; set to False for RGBA
adjust_color = True # set to True for colorful output; set to False for black & white
adjusted_color = "white" # any color or RGB hex value like "red", "#2a7eeb", "#A12331" # BLACK DOESN'T WORK
show_output_img = True # show the output image [for testing]

#######################
# experimental parameters
#######################
custom_colors = False # set to True for create custom colors for output; set to False for black & white
buffer = 0 # supposed to set buffer around resulting image
save_im = False # save as png


#######################
# input
#######################
input_height = input_image.height
input_width = input_image.width

input_dict = {}
for y in range(0, input_height):
    for x in range (0, input_width):
        current_pixel = input_image.getpixel((x,y))
        if (len(current_pixel) <= 3 or current_pixel[3] != 0) and list(current_pixel[:3]) == [0,0,0]:
            input_dict[(x,y)] = current_pixel

#######################
# pixel cube types
#######################
# "t_matrix_rows": [[6, -6],[3, 3]] represents a matrix of:
# 6 -6
# 3 3
chosen_format = formats.get_format(iso_type)
pixelcube = Image.open("formats/" + chosen_format["file_name"])

#######################
# transformation
#######################
adjusted_dict = {}

def trans(coords, format):
    x = coords[0]
    y = coords[1]
    trans_matrix = formats.get_format(format)["t_matrix_rows"]
    new_x = (trans_matrix[0][0] * x + trans_matrix[0][1] * y) + buffer
    new_y = (trans_matrix[1][0] * x + trans_matrix[1][1] * y) + buffer
    return [new_x, new_y]

#######################
# output dict
#######################

for coords in input_dict:
    new_coords = trans(coords, iso_type)
    adjusted_dict[(new_coords[0], new_coords[1])] = input_dict[coords]
    # adjusted_dict[(coords[0], coords[1])] = input_dict[coords]

# using zip() to unzip 
x_only = list(zip(*adjusted_dict.keys()))[0]
y_only = list(zip(*adjusted_dict.keys()))[1]

# maxes and mins
x_max, x_min, y_max, y_min = max(x_only), min(x_only), max(y_only), min(y_only)

origin_x = 0
for coords in adjusted_dict.keys():
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
output_dict = {}
for coords in adjusted_dict:
    output_dict[(coords[0] + origin_width, coords[1])] = adjusted_dict[(coords[0], coords[1])]
    # not shifted over version (for testing)
    # output_dict[(coords[0], coords[1])] = adjusted_dict[(coords[0], coords[1])]


#######################
# output image
#######################
bg_mode = "RGBA"

output_height = (y_max - y_min) + pixelcube.height + (buffer * 2)
output_width = (x_max - x_min) + pixelcube.width + (buffer * 2)

im = Image.new(mode=bg_mode, size=(output_width,output_height))

# to paste im2 on im1 at 0,0
# Image.Image.paste(im, two_px, (0, 0))

# add pixelcube onto im
for coords in output_dict:
    Image.Image.paste(im, pixelcube, (coords[0], coords[1]), mask=pixelcube)

#######################
# image colors
#######################
max_colors = 10
# color_example_location, color_list = zip(*im.getcolors(max_colors))
color_list = list(zip(*im.getcolors(max_colors)))[1] # list of all colors in the image
color_list = np.asarray(color_list) # convert from list to np array
non_alpha_colors = (color_list[:,3] != 0) # filter array to only choose colors that do not have an alpha of 0
color_array = color_list[non_alpha_colors][:,:3] # create array from filter. REMOVE [:,:3] TO INCLUDE ALPHA IN ARRAY

order = np.asarray([])
for color in color_array:
    order = np.append(order, np.sum(color))
order = np.argsort(order)[::-1] # [::-1] reverses the list
color_array_sorted = color_array[order]

### main colors
primary,secondary,tertiary=(0,0,0),(0,0,0),(0,0,0)
if 0 < len(color_array_sorted):
    primary = tuple(color_array_sorted[0])
if 1 < len(color_array_sorted):
    secondary = tuple(color_array_sorted[1])
if 2 < len(color_array_sorted):
    tertiary = tuple(color_array_sorted[2])

#######################
# adjust color
#######################

if adjust_color:
    im = ImageOps.colorize(image=im.convert('L'), black="black", white=adjusted_color)
    if transparent_background:
        im = im.convert("RGBA")
        data = np.array(im)
        reds, greens, blues, alphas = data.T
        black_background_filter = (reds == 0) & (greens == 0) & (blues == 0)
        data[:,:,:][black_background_filter.T] = (0,0,0,0)
        im=Image.fromarray(data)

if custom_colors:
    data = np.array(im)
    ########
    # transpose of the data numpy array
    # changes data from (width*height) rows and 4 columns to
    # 4 rows of (width*height) columns
    # then correlate r/g/b/a to each of the 4 rows
    reds, greens, blues, alphas = data.T # each is a 2d array of the r/g/b/a at that pixel
    ########
    # numpy array filtering. creates a numpy filter array of True/False values
    # https://www.w3schools.com/python/numpy/numpy_array_filter.asp
    nonzero_alpha_filter = (alphas != 0) & (reds == 255)
    primary_filter = (alphas != 0) & (reds == primary[0]) & (greens == primary[1]) & (blues == primary[2])
    secondary_filter = (alphas != 0) & (reds == secondary[0]) & (greens == secondary[1]) & (blues == secondary[2])
    tertiary_filter = (alphas != 0) & (reds == tertiary[0]) & (greens == tertiary[1]) & (blues == tertiary[2])

    data[:,:,:-1][primary_filter.T] = (255,0,255)
    data[:,:,:-1][secondary_filter.T] = (255,255,0)
    data[:,:,:-1][tertiary_filter.T] = (0,255,255)
    im=Image.fromarray(data)


#######################
# testing
#######################

# print("input height", input_height)
# print("input width", input_width)
# print(x_max, x_min, y_max, y_min, origin_x, origin_width)
# print("output_width", output_width)
# print("output_height", output_height)

# print(sorted(output_dict.keys(), key=lambda coord_key: coord_key[1])) # extras

#######################
# apply parameters
#######################

if not transparent_background:
    im=im.convert("RGB")
if show_output_img:
    im.show()
if save_im:
    image_png = im.save("pixeltext.png")
