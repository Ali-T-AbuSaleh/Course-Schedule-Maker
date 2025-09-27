import math
from copy import deepcopy

from Course_Information_Containers.Courses_Containers_farewell import courses_containers
from Objects.Courses import evaluate_exam_period_average, get_exam_differences, evaluate_diff_thresholds2, Course, \
    priority_wanted_courses

wanted_points = 16


class Node:
    def __init__(self, courses: list[Course]):
        self.courses = courses
        self.total_points = sum([c.points for c in courses])
        self.has_prioritized = {}
        #        (OS, Compilation, Complexity, ComputerStructure)

        # getting the actual values of has_prioritized,
        #    which represent the existence of the prioritized courses mentioned above.
        prioritized_courses = priority_wanted_courses.keys()
        for course in self.courses:
            if course.id in prioritized_courses:
                self.has_prioritized[course.id] = 1

        self.evaluation = 0
        self.exam_differences = []

    def is_goal(self) -> bool:
        return self.total_points >= wanted_points

        # getting the score/value/evaluation/heuristic of this node:

    def evaluate(self, priority_multiplier: float, goal_bonus: float) -> float:

        project_punishment = -10

        A_differences, B_differences, project_num = get_exam_differences(self.courses)
        self.exam_differences = A_differences + B_differences

        exam_period_score = evaluate_exam_period_average(
            A_differences, B_differences, evaluate_diff_thresholds2)
        if exam_period_score == float('-inf'): return float('-inf')

        priority_bonus = sum([priority_wanted_courses[id] for id, val in self.has_prioritized.items() if val == 1])
        priority_bonus *= priority_multiplier

        x = self.total_points
        x_displacement = x - wanted_points
        stretch_factor = 2.5
        amplitude = 15
        total_points_factor = amplitude * math.exp(-(x_displacement ** 2) / stretch_factor)

        # stress > stress_pivot gives punishment, < stress_pivot gives reward, linear behaviour.
        stress_pivot = 2.5
        stress_score_multiplier = 3
        stress_score = sum([stress_pivot - c.stress for c in self.courses if c.stress > 0])
        stress_score *= stress_score_multiplier
        rating_pivot = 3
        rating_score_multiplier = 1
        rating_score = sum([c.rating - rating_pivot for c in self.courses if c.rating > 0])
        rating_score *= rating_score_multiplier

        bad_average_supremum = 75
        good_average_infimum = 85

        def is_no_feedback_and_do_we_punish(c: Course) -> bool:
            if -1 not in [c.stress, c.rating]:
                return False
            if c.average is None:
                return True
            if c.average < bad_average_supremum:
                return True
            if c.average > good_average_infimum:
                return False
            if len(c.grades) >= 1.5 * c.SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT:
                return False
            return True

        punishment_per_no_feedback_factor = 5
        default_course_average = 50
        no_feedback_punishment = -sum(
            [punishment_per_no_feedback_factor * 100 / (
                c.average if c.average is not None else default_course_average)
             for c in self.courses if is_no_feedback_and_do_we_punish(c)])

        total_feedback_score = rating_score + stress_score + no_feedback_punishment

        def is_new_course(c: Course) -> bool:
            if c.average is None:
                return True
            return len(c.grades) < 1 * c.SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT

        new_course_punishment_factor = 10
        new_courses_punishment = - sum(
            [new_course_punishment_factor * c.points * 100 / (
                c.average if c.average is not None else default_course_average)
             for c in self.courses if is_new_course(c)])

        final_score = ((priority_bonus + exam_period_score +
                        total_feedback_score + new_courses_punishment) * total_points_factor
                       + project_num * project_punishment + goal_bonus * (self.total_points >= wanted_points))

        self.evaluation = final_score
        return final_score

    def neighbors(self, relevant_courses_dict: dict) -> list:
        neighbors = []

        for course in self.courses:
            new_courses = deepcopy(self.courses)
            new_courses.remove(course)
            neighbor = Node(new_courses)
            neighbors.append(neighbor)

        if self.total_points >= 23:  # no need to try and get more courses because that is too much
            return neighbors

        remaining_courses = deepcopy(relevant_courses_dict)
        for course in self.courses:
            remaining_courses.pop(course.id, None)

        for course in remaining_courses.values():
            new_courses = deepcopy(self.courses)
            new_courses.append(course)
            neighbor = Node(new_courses)
            neighbors.append(neighbor)

        return neighbors

    def __str__(self):
        self.courses.sort(key=sort_based_on_moed_a)

        result = "—————————————————————————————————————————————————————————————\n"
        result += f"total points: {self.total_points}\n"
        result += f"has prioritized: {self.has_prioritized}\n"
        result += f"evaluation: {self.evaluation}\n"
        result += "Courses:\n"
        for course in self.courses:
            result += f"{course}\n"

        result += "\n"
        result += "Exam Days| Course ID| Points | MoedA date   , MoedB date    | stress, rating |  AVG  | Course Name\n"
        for diff, course in self.exam_differences:
            if diff > 9:
                result += f"    {diff}   | {course}\n"
            else:
                result += f"    {diff}    | {course}\n"

        result += "—————————————————————————————————————————————————————————————\n"

        return result

    def __lt__(self, other):
        return self.total_points < other.total_points


def sort_based_on_moed_a(course1: Course) -> (int, int, int):
    if course1.moed_a is None: return 0, 0, 0
    return course1.moed_a.year, course1.moed_a.month, course1.moed_a.day
