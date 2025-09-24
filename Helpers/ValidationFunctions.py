import os

def validate_simple_course_list_input(list_input: str, location_of_list_input: str) -> str:
    words = list_input.split(' ')
    if not len(words) == 1:
        raise ValueError(
            f"invalid {location_of_list_input} format, must be:"
            f"{2 * "\n<COURSE ID (8 digits)>"}\n...")
    return words[0]


def validate_course_id(course_id: str, location_of_course_id: str) -> None:
    bad_course_id = f"invalid course id in {location_of_course_id}, it must be made up of 8 digits\n"
    if len(course_id) < 8:
        raise ValueError(bad_course_id)
    if len(course_id) > 8:
        if course_id[8].isdigit():
            raise ValueError(bad_course_id)

    course_id = course_id[0:8]
    for letter in course_id:
        if not letter.isdigit():
            raise ValueError(bad_course_id)


def validate_1to5_digit(digit: str, location_of_digit: str) -> None:
    bad_digit = f"invalid priority in {location_of_digit}, it must be a digit from 1-5\n"
    if not digit.isdigit():
        raise ValueError(bad_digit)
    course_priority = float(digit)
    if course_priority > 5 or course_priority < 1:
        raise ValueError(bad_digit)


def validate_txt_file_path(file_path: str) -> None:
    if not (os.path.exists(file_path) and file_path.endswith('.txt')):
        raise ValueError(f"invalid .txt file path:\n{file_path}\n it must be a path to a txt file")
