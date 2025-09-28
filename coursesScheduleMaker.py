import math
import random
import sys
from random import shuffle

from Helpers.DataGetters import get_priorities_from_file_to_dict, get_courses_dict, filter_courses, \
    get_and_validate_boolean_str
from Helpers.ValidationFunctions import validate_txt_file_path
from Objects.Courses import priority_wanted_courses, priority_wanted_exams
from Objects.Heap import MinHeap
from Objects.Node import Node, get_neighbors_add_course, get_neighbors_del_course, get_neighbors_replace_course, \
    get_neighbors_del_2_courses
from Objects.Strategy import Strategy
from config import ADDITIONAL_RUNS, starting_temperature, convergence_factor, ε, COURSES_DATA_JSON_PATH


def simulated_annealing(start: Node, T, gamma, epsilon=10 ** -9) -> MinHeap:
    curr = start
    curr_val = start.evaluate(priority_multiplier, goal_bonus, project_number_limit)

    # saving the top best number_of_returned_results nodes
    min_heap = MinHeap(number_of_returned_results)
    min_heap.push(curr_val, curr)
    pick_pool = []

    while T > epsilon:
        if prev != curr:
            pick_pool = list(curr.get_neighbors(courses_dict))
            # for elite in min_heap.parse_to_list():
            #     pick_pool.extend(elite.neighbors)
            shuffle(pick_pool)
        prev = curr

        if len(pick_pool) == 0:
            break

        new = pick_pool.pop()
        new_val = new.evaluate(priority_multiplier, goal_bonus, project_number_limit)
        deltaE = new_val - curr_val

        if deltaE > 0:
            curr = new
            curr_val = new_val
            min_heap.push(curr_val, curr)

        else:
            probability = math.exp(- math.fabs(deltaE) / T)
            if random.random() < probability:
                curr = new
                curr_val = new_val
                min_heap.push(curr_val, curr)

        T = gamma * T

    return min_heap


def steepest_ascent_hill_climbing(start: Node, WITH_SIDEWAY_STEPS=True, epsilon=10 ** -1) -> list[Node]:
    curr = start
    curr.evaluate(priority_multiplier, goal_bonus, project_number_limit)

    # saving the top best number_of_returned_results nodes
    results_queue = [None for _ in range(number_of_returned_results)]

    def push_result_pop_previous(n: Node):
        results_queue.append(n)
        results_queue.pop(0)

    push_result_pop_previous(curr)
    while True:
        neighbors = curr.get_neighbors(courses_dict)
        shuffle(neighbors)
        if len(neighbors) == 0: break
        if WITH_SIDEWAY_STEPS:
            max_neighbor = None
            max_eval = float('-inf')
        else:
            max_neighbor = curr
            max_eval = curr.evaluation

        for neighbor in neighbors:
            neighbor.evaluate(priority_multiplier, goal_bonus, project_number_limit)
            if max_eval < neighbor.evaluation:
                max_neighbor = neighbor
                max_eval = neighbor.evaluation
        if max_neighbor.evaluation <= curr.evaluation - epsilon * WITH_SIDEWAY_STEPS:
            return results_queue
        push_result_pop_previous(max_neighbor)
        curr = max_neighbor


if __name__ == '__main__':
    arg_len = 8
    if not len(sys.argv) == arg_len + 1:
        raise SyntaxError(
            "instruction format: coursesScheduleMaker.py <number_of_returned_results> <must18plus> <priority_multiplier> <project_number_limit> <wanted_courses_priority.txt> <wanted_exam_priority.txt> <completed_courses.txt> <unwanted_courses.txt>")
    number_of_returned_results = sys.argv[1]
    must18plus = sys.argv[2]
    priority_multiplier = sys.argv[3]
    project_number_limit = sys.argv[4]
    wanted_courses_priority_txt = sys.argv[5]
    wanted_exam_priority_txt = sys.argv[6]
    completed_courses_txt = sys.argv[7]
    unwanted_courses_txt = sys.argv[8]

    if not number_of_returned_results.isnumeric():
        raise ValueError("number of returned results must be an integer")
    number_of_returned_results = int(number_of_returned_results)

    if get_and_validate_boolean_str(must18plus, "must18plus"):
        goal_bonus = 100  # goal states dominate
    else:
        goal_bonus = 50  # good bonus for goal states but not extreme — not necessary

    if not float(priority_multiplier):
        raise ValueError("invalid priority_multiplier value: it must be a number")
    priority_multiplier = float(priority_multiplier)

    if not project_number_limit.isnumeric():
        raise ValueError("project_number_limit must be a number")
    project_number_limit = int(project_number_limit)

    validate_txt_file_path(wanted_courses_priority_txt)
    validate_txt_file_path(wanted_exam_priority_txt)
    validate_txt_file_path(completed_courses_txt)
    validate_txt_file_path(unwanted_courses_txt)

    #   let the errors propagate
    get_priorities_from_file_to_dict(wanted_courses_priority_txt, priority_wanted_courses,
                                     field_name="wanted_courses_priority.txt")
    get_priorities_from_file_to_dict(wanted_exam_priority_txt, priority_wanted_exams,
                                     field_name="wanted_exam_priority.txt")

    # TODO: make this a user input
    SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT = 6

    courses_dict = get_courses_dict(COURSES_DATA_JSON_PATH)
    courses_dict = filter_courses(courses_dict, completed_courses_txt, unwanted_courses_txt)

    start_courses_ids = ["02340123", "02360343", "00970317"]
    # start_courses_ids = ["00940412", "02340218", "02340129", "02340125"] #Anwaar courses
    start_courses = [c for cid, c in courses_dict.items() if cid in start_courses_ids]


    def print_results(results):
        i = 1
        for node in results:
            print(f'{i}.\n{node}\n\n')
            i += 1


    # TODO: make it user input
    strategy = Strategy.SIMULATED_ANNEALING

    # –––––––––––––––––––––––––SIMULATED ANNEALING RUNS–––––––––––––––––––––––––
    if strategy == Strategy.SIMULATED_ANNEALING:
        sim_annealing_operation_set = [get_neighbors_add_course,
                                       get_neighbors_del_course,
                                       get_neighbors_replace_course]
        sim_annealing_start = Node(start_courses)
        sim_annealing_start.operation_set = sim_annealing_operation_set
        try:
            main_result_heap = simulated_annealing(sim_annealing_start, starting_temperature, convergence_factor, ε)
            result_heaps = [MinHeap(number_of_returned_results) for _ in range(ADDITIONAL_RUNS)]
            for i in range(ADDITIONAL_RUNS):
                result_heaps[i] = simulated_annealing(sim_annealing_start, starting_temperature, convergence_factor, ε)

            # merging into main_result_heap
            for i in range(ADDITIONAL_RUNS):
                main_result_heap += result_heaps[i]
        finally:
            result_sorted = []
            while len(main_result_heap) > 0:
                result_sorted.append(main_result_heap.pop()[1])

            result_sorted.reverse()

            print_results(result_sorted)

    # –––––––––––––––––––––––––Steepest AHC RUNS–––––––––––––––––––––––––
    if strategy == Strategy.STEEPEST_AHC:
        steepest_AHC_operation_set = [get_neighbors_add_course,
                                      get_neighbors_del_course,
                                      get_neighbors_replace_course]
        steepest_AHC_start = Node(start_courses)
        steepest_AHC_start.operation_set = steepest_AHC_operation_set

        result_sorted = steepest_ascent_hill_climbing(steepest_AHC_start, WITH_SIDEWAY_STEPS=False)
        result_sorted.reverse()
        print_results(result_sorted)

    # –––––––––––––––––––––––evaluating a given schedule–––––––––––––––––––––––
    if strategy == Strategy.EVALUATE_GIVEN_SCHEDULE:
        given_courses_ids = ["02340123", "02360343", "00970317", "02360833", "01140054"]
        # given_courses_ids = ["00940412", "02340218", "02340129", "02340125","01140075"] #Anwaar courses
        given_courses = [courses_dict[cid] for cid in given_courses_ids]
        evaluation_node = Node(given_courses)
        evaluation_node.evaluate(priority_multiplier, goal_bonus, project_number_limit)
        print(evaluation_node)
