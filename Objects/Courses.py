import math
from datetime import datetime

MAX_COURSE_POINTS = 5
priority_wanted_courses = {}
priority_wanted_exams = {}


class Course:
    def __init__(self, name: str, id: str, points: int, moed_a: datetime, moed_b: datetime):
        self.name = name
        self.id = id
        self.points = points
        self.moed_a = moed_a
        self.moed_b = moed_b

    def __str__(self):
        if self.moed_a is None:
            exam_a = "----None----"
        else:
            exam_a = datetime.date(self.moed_a)
        if self.moed_b is None:
            exam_b = "----None----"
        else:
            exam_b = datetime.date(self.moed_b)
        return f'{self.id} | {int(self.points * 10) / 10}pts | Moed A: {exam_a}, Moed B: {exam_b} | {self.name}'

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.points < other.points

    def __gt__(self, other):
        return self.points > other.points

    def __le__(self, other):
        return self.points <= other.points

    def __ge__(self, other):
        return self.points >= other.points

    def __ne__(self, other):
        return self.id != other.id


def evaluate_diff_thresholds1(diff: int) -> float:
    # if an exam only got 0-1 days then I want to punish it equaly because I cant take this exam
    if diff < 2:
        mean = 0.5

    # if an exam only got 2 days then I want to punish it still but at least I can revise one day before it
    if diff == 2:
        mean = 0.9

    # if an exam only got more than 7 days then I will not study in the days after the 7th
    if diff > 7:
        diff = 7

    # scaling the values down to ~1 so that when I raise them to the power,
    # they get more reward, while the small days above get punished more.
    rescaled = diff * 0.1  # scalling down the values
    bonus = 0.5 + 0.15
    mean = rescaled + bonus

    multiplier = 2.7  # used to exaggerate the values

    return multiplier * (mean ** 2)


def evaluate_diff_thresholds2(diff: int, punishment_multiplier: float) -> float:
    upper_limit = 5  # the limit that the expression (values) converges to.

    # if an exam only got 0-1 days then I want to punish it equally because I cant take this exam
    if diff < 2:
        return -upper_limit * punishment_multiplier * 5

    # if an exam only got 2 days then I want to punish it still but at least I can revise one day before it
    if diff == 2:
        return -upper_limit * punishment_multiplier * 3

        # diff=3 must return >=1.

    x = diff  # friendlier representation for functions
    multiplier = 50  # used to exaggerate the values
    roundness_factor = 120  # in [50,200], the higher the value, the rounder the graph (no extreme jumps)
    roundness_constant = 2

    # used to start getting close high values at 6-7, and get low values at <3
    convergence_factor = roundness_constant - multiplier / roundness_factor

    return upper_limit + multiplier * (-math.exp(-x / convergence_factor))


def get_exam_differences(courses: list) -> (list, list, int):
    A_exams = [(c.moed_a, c) for c in courses]
    B_exams = [(c.moed_b, c) for c in courses]

    malag_num = 0
    project_num = 0
    str_project_list = [
        "project",
        "Project",
        "PRVYYQT",
        "SMYNR",
        "פרויקט",
        "נושאים"
    ]

    for (moed_a, c) in A_exams:
        if moed_a is None:
            for name in str_project_list:
                if name in c.name:
                    project_num += 1
                    break
            malag_num += 1

    for (moed_b, c) in B_exams:
        if moed_b is None:
            for name in str_project_list:
                if name in c.name:
                    project_num += 1
                    break
            malag_num += 1

    project_num /= 2
    malag_num /= 2

    A_exams = [(moed_a, c) for (moed_a, c) in A_exams if moed_a is not None]
    B_exams = [(moed_b, c) for (moed_b, c) in B_exams if moed_b is not None]

    A_exams.sort()
    B_exams.sort()

    A_differences = []

    previous_exam_date = datetime(2026, 1, 31) #actually it is 2 Feb.
    for exam in A_exams:
        if exam[0] is None: continue
        difference = (exam[0] - previous_exam_date).days
        A_differences.append((difference, exam[1]))
        previous_exam_date = exam[0]

    B_differences = []
    for exam in B_exams:
        if exam[0] is None: continue
        difference = (exam[0] - previous_exam_date).days
        B_differences.append((difference, exam[1]))
        previous_exam_date = exam[0]

    # TODO: change the last element of the tuple to two independent elements
    return A_differences, B_differences, project_num + malag_num


def evaluate_single_exam(studying_days: int, course: Course, prev_course_id: str, multiplier: float,
                         evaluation_strat) -> float:
    exam_priority = priority_wanted_exams[course.id] if course.id in priority_wanted_exams else 1
    if studying_days < 3:
        if prev_course_id in priority_wanted_exams:
            exam_priority = priority_wanted_exams[prev_course_id] * exam_priority

    return (evaluation_strat(studying_days, multiplier) * course.points *
            exam_priority / MAX_COURSE_POINTS) * multiplier


def evaluate_exam_period_sum(A_differences: list, B_differences: list, evaluation_strat) -> float:
    if len(A_differences) + len(B_differences) == 0:
        return float('-inf')

    sum = 0

    A_multiplier = 3
    prev_course_id = ""
    for difference in A_differences:
        course = difference[1]
        studying_days = difference[0]
        sum += evaluate_single_exam(studying_days, course, prev_course_id, A_multiplier, evaluation_strat)
        prev_course_id = course.id

    B_multiplier = 1
    for difference in B_differences:
        course = difference[1]
        studying_days = difference[0]
        sum += evaluate_single_exam(studying_days, course, prev_course_id, B_multiplier, evaluation_strat)
        prev_course_id = course.id

    return sum


def evaluate_exam_period_average(A_differences: list, B_differences: list, evaluation_strat) -> float:
    if len(A_differences) + len(B_differences) == 0:
        return float('-inf')

    sum = evaluate_exam_period_sum(A_differences, B_differences, evaluation_strat)

    return sum / (len(A_differences) + len(B_differences))
