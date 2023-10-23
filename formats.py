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

def get_format(iso_type):
    return formats[iso_type]