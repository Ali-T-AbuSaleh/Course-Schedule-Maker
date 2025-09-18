import math
from Objects.Courses import evaluate_exam_period_average, get_exam_differences, evaluate_diff_thresholds2, Course, \
    priority_wanted_courses

wanted_points = 16

class Node:
    def __init__(self, courses: list):
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

        project_punishment = -70

        A_differences, B_differences, project_num = get_exam_differences(self.courses)
        self.exam_differences = A_differences + B_differences

        exam_period_score = evaluate_exam_period_average(
            A_differences, B_differences, evaluate_diff_thresholds2)
        if exam_period_score == float('-inf'): return float('-inf')

        priority_bonus = sum([priority_wanted_courses[id] for id, val in self.has_prioritized.items() if val == 1])

        x = self.total_points
        x_displacement = x - wanted_points
        squish_factor = 2.5
        total_points_factor = 15 * math.exp(-x_displacement ** 2 / squish_factor)

        final_score = ((priority_bonus + exam_period_score) * total_points_factor
                       + project_num * project_punishment + goal_bonus * (self.total_points >= wanted_points))

        self.evaluation = final_score
        return final_score

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
        result += "Exam Days| Course ID| Points | MoedA date, MoedB date | Course Name\n"
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
