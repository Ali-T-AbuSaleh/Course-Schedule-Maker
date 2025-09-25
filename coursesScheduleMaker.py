import math
import random
import sys
from random import shuffle

from Helpers.DataGetters import get_priorities_from_file_to_dict, get_courses_dict, filter_courses
from Helpers.ValidationFunctions import validate_txt_file_path
from Objects.Courses import priority_wanted_courses, priority_wanted_exams
from Objects.Heap import MinHeap
from Objects.Node import Node

COURSES_DATA_JSON_PATH = "CoursesData/courses_data_json.json"
ADDITIONAL_RUNS = 4
starting_temperature = 10000
convergence_factor = 0.95
ε = 10 ** -11


def simulated_annealing(start: Node, T, convergence_factor, epsilon=10 ** -9) -> MinHeap:
    curr = start
    curr_val = start.evaluate(priority_multiplier, goal_bonus)

    # saving the top best number_of_returned_results nodes
    min_heap = MinHeap(number_of_returned_results)
    min_heap.push(curr_val, curr)
    pick_pool = []

    while T > epsilon:
        old_pick_pool = pick_pool
        pick_pool = curr.neighbors(courses_dict)
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

        else:
            probability = -math.exp(-math.fabs(deltaE) / T)
            if random.random() < probability:
                curr = new
                curr_val = new_val
                min_heap.push(curr_val, curr)

        T = convergence_factor * T

    return min_heap


if __name__ == '__main__':
    arg_len = 7
    if not len(sys.argv) == arg_len + 1:
        print(
            "instruction format: coursesScheduleMaker.py <number_of_returned_results> <must18plus> <priority_multiplier> <wanted_courses_priority.txt> <wanted_exam_priority.txt> <completed_courses.txt> <unwanted_courses.txt>")
    number_of_returned_results = sys.argv[1]
    must18plus = sys.argv[2]
    priority_multiplier = sys.argv[3]
    wanted_courses_priority_txt = sys.argv[4]
    wanted_exam_priority_txt = sys.argv[5]
    completed_courses_txt = sys.argv[6]
    unwanted_courses_txt = sys.argv[7]

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

    validate_txt_file_path(wanted_courses_priority_txt)
    validate_txt_file_path(wanted_exam_priority_txt)
    validate_txt_file_path(completed_courses_txt)
    validate_txt_file_path(unwanted_courses_txt)

    #   let the errors propagate
    get_priorities_from_file_to_dict(wanted_courses_priority_txt, priority_wanted_courses,
                                     field_name="wanted_courses_priority.txt")
    get_priorities_from_file_to_dict(wanted_exam_priority_txt, priority_wanted_exams,
                                     field_name="wanted_exam_priority.txt")


    #TODO: make this a user input
    SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT = 6


    courses_dict = get_courses_dict(COURSES_DATA_JSON_PATH)
    courses_dict = filter_courses(courses_dict, completed_courses_txt, unwanted_courses_txt)

    start_courses = ["02340123", "02360343"]
    start = Node([c for cid, c in courses_dict.items() if cid in start_courses])

    main_result_heap = simulated_annealing(start, starting_temperature, convergence_factor, ε)
    result_heaps = [MinHeap(number_of_returned_results) for _ in range(ADDITIONAL_RUNS)]
    for i in range(ADDITIONAL_RUNS):
        result_heaps[i] = simulated_annealing(start, starting_temperature, convergence_factor, ε)

    # merging into main_result_heap
    for i in range(ADDITIONAL_RUNS):
        main_result_heap += result_heaps[i]

    result_sorted = []
    while len(main_result_heap) > 0:
        result_sorted.append(main_result_heap.pop()[1])

    result_sorted.reverse()


    def print_results():
        i = 1
        for node in result_sorted:
            print(f'{i}.\n{node}\n\n')
            i += 1


    print_results()
