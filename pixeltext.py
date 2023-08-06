from PIL import Image, ImageOps

#######################
# issues/ideas
#######################
# does not work properly if source image does not start in the top left corner (Y NOT WORKING - check with sprite9)
# idea: create an 3d image of a square. then adjust its angle using a linear transformation to use as the pixelcube for custom matrices

#######################
# parameters
#######################
input_image = Image.open("inputs/sexy.png")
input_height = input_image.height
input_width = input_image.width
buffer = 0
bg_mode = "RGB" # "RGB" or "RGBA"
iso_type = "noah" # "2px" or "4px"
save_im = False # True or False (not working right now)
adjust_color = False
adjusted_color = "red" # "#2a7eeb" # any RGB hex value

#######################
# input
#######################
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
formats = { #standard
            "2px_base": {"file_name": "2px_base.png", "t_matrix_rows": [[6, -6],[3, 3]]},
           "3px_base": {"file_name": "3px_base.png", "t_matrix_rows": [[7, -7],[3, 3]]},
           "4px_base": {"file_name": "4px_base.png", "t_matrix_rows": [[8, -8],[4, 4]]},
           "2px_outline": {"file_name": "2px_outline.png", "t_matrix_rows": [[6, -6],[3, 3]]},
           "3px_outline": {"file_name": "3px_outline.png", "t_matrix_rows": [[7, -7],[3, 3]]},
           "2px_outline_unshaded": {"file_name": "2px_outline_unshaded.png", "t_matrix_rows": [[6, -6],[3, 3]]},
           "3px_outline_unshaded": {"file_name": "3px_outline_unshaded.png", "t_matrix_rows": [[7, -7],[3, 3]]},
           "steps": {"file_name": "3px_outline.png", "t_matrix_rows": [[7, -7],[7, 7]]},
           # special
           "tester": {"file_name": "tester_base.png", "t_matrix_rows": [[6, -6],[3, 3]]},
           "custom_matrix1": {"file_name": "2px_outline.png", "t_matrix_rows": [[8, -8],[8, 8]]},
           "custom_matrix3": {"file_name": "3px_base.png", "t_matrix_rows": [[0, -7],[7, 0]]},
           "hologram": {"file_name": "red.png", "t_matrix_rows": [[5, 0],[0, 10]]},
           "cool_shape": {"file_name": "red.png", "t_matrix_rows": [[3, -3],[3, 3]]},
           "2x2_demo": {"file_name": "2x2.png", "t_matrix_rows": [[6, -6],[3, 3]]},
           "noah": {"file_name": "noah_src.png", "t_matrix_rows": [[128, 0],[0, 128]]},

           }
pixelcube = Image.open("formats/" + formats[iso_type]["file_name"])

#######################
# transformation
#######################
adjusted_dict = {}

def trans(coords, format):
    x = coords[0]
    y = coords[1]
    trans_matrix = formats[format]["t_matrix_rows"]
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
x_max = max(x_only)
x_min = min(x_only)
y_max = max(y_only)
y_min = min(y_only)

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
output_height = (y_max - y_min) + pixelcube.height + (buffer * 2)
output_width = (x_max - x_min) + pixelcube.width + (buffer * 2)

im = Image.new(mode=bg_mode, size=(output_width,output_height))

# to paste im2 on im1 at 0,0
# Image.Image.paste(im, two_px, (0, 0))

# add pixelcube onto im
for coords in output_dict:
    Image.Image.paste(im, pixelcube, (coords[0], coords[1]), mask=pixelcube)

#######################
# adjust color
#######################
if adjust_color:
    im = ImageOps.colorize(image=im.convert('L'), black="black", white=adjusted_color)

#######################
# display/print
#######################
print("input height", input_height)
print("input width", input_width)
print(sorted(output_dict.keys(), key=lambda coord_key: coord_key[1]))
print(x_max, x_min, y_max, y_min, origin_x, origin_width)
print("output_width", output_width)
print("output_height", output_height)

im.show()


#######################
# other
#######################

# straight white line
# for i in range(width):
#     pixel_map[i, 5] = (255, 255, 255)


# save as pixeltext.png
if save_im:
    image_png = im.save("pixeltext", format="png")