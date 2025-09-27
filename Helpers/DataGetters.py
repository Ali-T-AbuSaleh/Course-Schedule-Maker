import sys
import json
from datetime import datetime

from Helpers.ValidationFunctions import validate_1to10_digit, validate_course_id, validate_simple_course_list_input
from Objects.Courses import Course

SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT = 6


def get_courses_dict(courses_data_json_path: str) -> dict[str, Course]:
    result_dict = {}
    try:
        with open(courses_data_json_path, 'r', encoding="utf-8") as f:
            dict_courses = json.load(f)
    except Exception as ex:
        print("an error occurred while reading json file. Error:", sys.stderr)
        raise ex

    for course_id, dict_data in dict_courses.items():

        ID = dict_data["id"]
        name = dict_data["name"]
        points = dict_data["points"]
        prerequisites_logical_expression = dict_data["prerequisites_logical_expression"]
        equivalents = dict_data["equivalents"]
        stress = dict_data["stress"]
        rating = dict_data["rating"]
        grades = dict_data["course_grades"]
        moed_a = dict_data["moed_a"]
        moed_b = dict_data["moed_b"]

        #TODO: modify and add support for customized value of
        #       SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT for each course.


        if moed_a == "None" or moed_a == "":
            moed_a = None
        elif moed_a is not None:
            moed_a = datetime.fromisoformat(moed_a)
        if moed_b == "None" or moed_b == "":
            moed_b = None
        elif moed_b is not None:
            moed_b = datetime.fromisoformat(moed_b)
        course = Course(name, ID, points, prerequisites_logical_expression,
                        equivalents, stress, rating, grades, moed_a, moed_b)
        result_dict[course_id] = course

    return result_dict


def filter_courses(courses: dict, completed_courses_file_path: str, unwanted_courses_file_path: str) -> dict:
    completed_courses_id = []
    with open(completed_courses_file_path, 'r') as f:
        for line in f:
            line = line.strip('\n')
            course_id = validate_simple_course_list_input(line, completed_courses_file_path)
            validate_course_id(course_id, completed_courses_file_path)

            # otherwise, everything is valid
            completed_courses_id.append(course_id)

    def filter_completed_courses():
        for cid in completed_courses_id:
            try:
                courses.pop(cid)
            finally:
                continue

    def filter_courses_with_no_prerequisites():
        completed_courses = {'No Prerequisites': True}
        for cid in completed_courses_id:
            completed_courses[cid] = True

        dont_satisfy_prerequisites = []
        for cid, course in courses.items():
            if not eval(course.prerequisites_logical_expression):
                dont_satisfy_prerequisites.append(cid)

        for cid in dont_satisfy_prerequisites:
            try:
                courses.pop(cid)
            finally:
                continue

    def filter_courses_equivalents():
        for cid in completed_courses_id:
            if cid in courses:
                equivalents = courses[cid].equivalents
            else:
                equivalents = []
            for equivalent in equivalents:
                try:
                    courses.pop(equivalent)
                finally:
                    continue

    def filter_unwanted_courses():
        with open(unwanted_courses_file_path, 'r') as f:
            for line in f:
                line = line.strip('\n')
                course_id = validate_simple_course_list_input(line, completed_courses_file_path)
                validate_course_id(course_id, completed_courses_file_path)

                # otherwise, everything is valid
                try:
                    courses.pop(course_id)
                finally:
                    continue

    filter_courses_equivalents()
    filter_completed_courses()
    filter_courses_with_no_prerequisites()
    filter_unwanted_courses()

    return courses


def get_priorities_from_file_to_dict(file_path: str, priority_dict: dict, field_name: str) -> None:
    with open(file_path, 'r') as f:
        line = f.readline().strip('\n')
        while line:
            words = line.split(' ')
            if not len(words) == 2:
                raise ValueError(
                    f"invalid {field_name} format, must be:"
                    f"{2 * "\n<COURSE ID (8 digits)>: <PRIORITY (1-5)>"}\n...")
            course_id = words[0]
            course_priority = words[1]

            validate_1to10_digit(course_priority, field_name)
            validate_course_id(course_id, field_name)

            # otherwise, everything is valid
            priority_dict[course_id] = float(course_priority)

            line = f.readline().strip('\n')
