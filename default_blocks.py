formats = { 
        ### standard
        "2px": {"block_img_file": "2px.png", "t_matrix": [[6, -6],[3, 3]]},
        "3px": {"block_img_file": "3px.png", "t_matrix": [[7, -7],[3, 3]]},
        "4px": {"block_img_file": "4px.png", "t_matrix": [[8, -8],[4, 4]]},
}

def get_format(iso_type):
    return formats[iso_type]