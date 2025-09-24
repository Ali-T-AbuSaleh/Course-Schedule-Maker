import json
import math
import random
import sys
from copy import deepcopy
from datetime import datetime
from random import shuffle

from Objects.Courses import Course, priority_wanted_courses, priority_wanted_exams
from Objects.Heap import MinHeap
from Objects.Node import Node
from CoursesData.CoursesList import raw_courses_list

import os


def neighbors(node: Node, relevant_courses_dict: dict) -> list:
    neighbors = []

    for course in node.courses:
        new_courses = deepcopy(node.courses)
        new_courses.remove(course)
        neighbor = Node(new_courses)
        neighbors.append(neighbor)

    if node.total_points >= 23:  # no need to try and get more courses because that is too much
        return neighbors

    remaining_courses = deepcopy(relevant_courses_dict)
    for course in node.courses:
        remaining_courses.pop(course.id, None)

    for course in remaining_courses.values():
        new_courses = deepcopy(node.courses)
        new_courses.append(course)
        neighbor = Node(new_courses)
        neighbors.append(neighbor)

    return neighbors


def simulated_annealing(start: Node, T, convergence_factor, epsilon=10 ** -9) -> MinHeap:
    curr = start
    curr_val = start.evaluate(priority_multiplier, goal_bonus)

    # saving the top best number_of_returned_results nodes
    min_heap = MinHeap()
    min_heap.push(curr_val, curr)
    pick_pool = []

    while T > epsilon:
        old_pick_pool = pick_pool
        pick_pool = neighbors(curr, courses_dict)
        pick_pool = pick_pool + old_pick_pool
        shuffle(pick_pool)

        if len(pick_pool) == 0: break

        new = pick_pool.pop()
        new_val = new.evaluate(priority_multiplier, goal_bonus)
        deltaE = new_val - curr_val

        if deltaE > 0:
            curr = new
            curr_val = new_val
            min_heap.push(curr_val, curr)
            if len(min_heap) > number_of_returned_results:
                min_heap.pop()
        else:
            probability = -math.exp(-math.fabs(deltaE) / T)
            if random.random() < probability:
                curr = new
                curr_val = new_val
                min_heap.push(curr_val, curr)
                if len(min_heap) > number_of_returned_results:
                    min_heap.pop()

        T = convergence_factor * T

    return min_heap


def get_courses_list(courses_data_json_path: str) -> dict[str, Course]:
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
        average = dict_data["course_average"]
        moed_a = dict_data["moed_a"]
        moed_b = dict_data["moed_b"]

        if moed_a == "None" or moed_a == "":
            moed_a = None
        elif moed_a is not None:
            moed_a = datetime.fromisoformat(moed_a)
        if moed_b == "None" or moed_b == "":
            moed_b = None
        elif moed_b is not None:
            moed_b = datetime.fromisoformat(moed_b)
        course = Course(name, ID, points, prerequisites_logical_expression,
                        equivalents, stress, rating, average, moed_a, moed_b)
        result_dict[course_id] = course

    return result_dict


def filter_courses(courses: dict, completed_courses_file_path: str) -> dict:
    completed_courses_id = []
    with open(completed_courses_file_path, 'r') as f:
        for line in f:
            line = line.strip('\n')
            words = line.split(' ')
            if not len(words) == 1:
                raise ValueError(
                    f"invalid {completed_courses_file_path} format, must be:"
                    f"{2 * "\n<COURSE ID (8 digits)>"}\n...")
            course_id = words[0]
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

    filter_courses_equivalents()
    filter_completed_courses()
    filter_courses_with_no_prerequisites()

    return courses


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

            validate_1to5_digit(course_priority, field_name)
            validate_course_id(course_id, field_name)

            # otherwise, everything is valid
            priority_dict[course_id] = float(course_priority)

            line = f.readline().strip('\n')


if __name__ == '__main__':
    arg_len = 6
    if not len(sys.argv) == arg_len + 1:
        print(
            "instruction format: coursesScheduleMaker.py <number_of_returned_results> <must18plus> <priority_multiplier> <wanted_courses_priority.txt> <wanted_exam_priority.txt> <completed_courses.txt>")
    number_of_returned_results = sys.argv[1]
    must18plus = sys.argv[2]
    priority_multiplier = sys.argv[3]
    wanted_courses_priority_txt = sys.argv[4]
    wanted_exam_priority_txt = sys.argv[5]
    completed_courses_txt = sys.argv[6]

    if not number_of_returned_results.isnumeric():
        raise ValueError("number of returned results must be an integer")
    number_of_returned_results = int(number_of_returned_results)

    if must18plus == '1' or must18plus == 'true' or must18plus == 'True':
        goal_bonus = 100  # goal states dominate
    elif must18plus == '0' or must18plus == 'false' or must18plus == 'False':
        goal_bonus = 50  # good bonus for goal states but not extreme — not necessary
    else:
        raise ValueError("invalid must18plus value: it must be boolean")

    if not priority_multiplier.isdecimal():
        raise ValueError("invalid priority_multiplier value: it must be a number")
    priority_multiplier = float(priority_multiplier)

    if not (os.path.exists(wanted_courses_priority_txt) and wanted_courses_priority_txt.endswith('.txt')):
        raise ValueError("invalid wanted_courses_priority.txt: it must be a path to a txt file")

    if not (os.path.exists(wanted_exam_priority_txt) and wanted_exam_priority_txt.endswith('.txt')):
        raise ValueError("invalid wanted_exam_priority.txt: it must be a path to a txt file")

    if not (os.path.exists(completed_courses_txt) and completed_courses_txt.endswith('.txt')):
        raise ValueError("invalid completed_courses.txt: it must be a path to a txt file")

    #   let the errors propagate
    get_priorities_from_file_to_dict(wanted_courses_priority_txt, priority_wanted_courses,
                                     field_name="wanted_courses_priority.txt")
    get_priorities_from_file_to_dict(wanted_exam_priority_txt, priority_wanted_exams,
                                     field_name="wanted_exam_priority.txt")

    courses_dict = get_courses_list("CoursesData/courses_data_json.json")
    # courses_list = courses_dict.values()
    courses_dict = filter_courses(courses_dict, completed_courses_txt)

    start_courses = ["02340123", "02360343"]
    start = Node([c for cid, c in courses_dict.items() if cid in start_courses])

    main_result_heap = simulated_annealing(start, T=10000, convergence_factor=0.95)
    ADDITIONAL_RUNS = 0
    result_heaps = [ADDITIONAL_RUNS * []]
    for i in range(ADDITIONAL_RUNS):
        result_heaps[i] = simulated_annealing(start, T=1000, convergence_factor=0.95)

    # merging into main_result_heap
    for i in range(ADDITIONAL_RUNS):
        while len(result_heaps[i]) > 0:
            evaluation_node = result_heaps[i].get_min()
            result_heaps[i].pop()
            if evaluation_node[0] > main_result_heap.get_min()[0]:
                main_result_heap.pop()
                main_result_heap.push(evaluation_node[0], evaluation_node[1])

    result_sorted = []
    while len(main_result_heap) > 0:
        result_sorted.append(main_result_heap.pop()[1])

    result_sorted.reverse()
    i = 1
    for node in result_sorted:
        print(f'{i}.\n{node}\n\n')
        i += 1
