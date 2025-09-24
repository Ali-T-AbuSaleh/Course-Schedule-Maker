import math
import random
import sys
from copy import deepcopy
from datetime import datetime
from random import shuffle

from select import error

from Objects.Courses import Course, priority_wanted_courses, priority_wanted_exams
from Objects.Heap import MinHeap
from Objects.Node import Node
from CoursesData.CoursesList import raw_courses_list

import os


def neighbors(node: Node, all_courses: list) -> list:
    neighbors = []

    for course in node.courses:
        new_courses = deepcopy(node.courses)
        new_courses.remove(course)
        neighbor = Node(new_courses)
        neighbors.append(neighbor)

    if node.total_points >= 23:  # no need to try and get more courses because that is too much
        return neighbors

    remaining_courses = deepcopy(all_courses)
    for course in node.courses:
        remaining_courses.remove(course)

    for course in remaining_courses:
        new_courses = deepcopy(node.courses)
        new_courses.append(course)
        neighbor = Node(new_courses)
        neighbors.append(neighbor)

    return neighbors


def simulated_annealing(start: Node, T, convergence_factor, epsilon=10 ** -11) -> MinHeap:
    curr = start
    curr_val = start.evaluate(priority_multiplier, goal_bonus)

    # saving the top best number_of_returned_results nodes
    min_heap = MinHeap()
    min_heap.push(curr_val, curr)
    pick_pool = []

    while T > epsilon:
        old_pick_pool = pick_pool
        pick_pool = neighbors(curr, courses_list)
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


def get_courses_list(raw_list: list) -> list:
    result_list = []
    for raw_course in raw_list:

        ID = raw_course[0]
        name = raw_course[1]
        points = raw_course[2]
        if raw_course[3] is None:
            moed_a = None
        else:
            moed_a = datetime.fromisoformat(raw_course[3])
        if raw_course[4] is None:
            moed_b = None
        else:
            moed_b = datetime.fromisoformat(raw_course[4])
        course = Course(name, ID, points, moed_a, moed_b)
        result_list.append(course)

    return result_list

def get_priorities_from_file_to_dict(file_path: str, priority_dict: dict, field_name:str) -> None:
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
            if not course_priority.isdigit():
                raise ValueError(f"invalid priority in {field_name}, it must be a digit from 1-5\n")

            bad_course_id = f"invalid course id in {field_name}, it must be made up of 8 digits\n"
            if not len(course_id) == 9:
                raise ValueError(bad_course_id)

            course_id = course_id[0:8]
            for letter in course_id:
                if not letter.isdigit():
                    raise ValueError(bad_course_id)

            # otherwise, everything is valid
            priority_dict[course_id] = float(course_priority)

            line = f.readline().strip('\n')

if __name__ == '__main__':
    arg_len = 5
    if not len(sys.argv) == arg_len + 1:
        print(
            "instruction format: coursesScheduleMaker.py <number_of_returned_results> <must18plus> <priority_multiplier> <wanted_courses_priority.txt> <wanted_exam_priority.txt>")
    number_of_returned_results = sys.argv[1]
    must18plus = sys.argv[2]
    priority_multiplier = sys.argv[3]
    wanted_courses_priority_txt = sys.argv[4]
    wanted_exam_priority_txt = sys.argv[5]

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
        raise ValueError("invalid wanted_courses_priority.txt value: it must be a path to a txt file")
    
    if not (os.path.exists(wanted_exam_priority_txt) and wanted_exam_priority_txt.endswith('.txt')):
        raise ValueError("invalid wanted_exam_priority.txt value: it must be a path to a txt file")
    

    #   let the errors propagate
    get_priorities_from_file_to_dict(wanted_courses_priority_txt, priority_wanted_courses, field_name="wanted_courses_priority.txt")
    get_priorities_from_file_to_dict(wanted_exam_priority_txt, priority_wanted_exams, field_name="wanted_exam_priority.txt")

    courses_list = get_courses_list(raw_courses_list)

    wanted_courses = ["02340123","02360343"]
    start = Node([c for c in courses_list if c.id in wanted_courses])

    main_result_heap = simulated_annealing(start, T=10000, convergence_factor=0.95)
    result_heaps = [[], [], [], []]
    result_heaps[0] = simulated_annealing(start, T=1000, convergence_factor=0.95)
    result_heaps[1] = simulated_annealing(start, T=1000, convergence_factor=0.95)
    result_heaps[2] = simulated_annealing(start, T=1000, convergence_factor=0.95)
    result_heaps[3] = simulated_annealing(start, T=1000, convergence_factor=0.95)

    # merging into main_result_heap
    for i in range(0, 4):
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