import math
from copy import deepcopy

from Objects.Courses import evaluate_exam_period_average, get_exam_differences, evaluate_diff_thresholds2, Course, \
    priority_wanted_courses

wanted_points_min = 16
wanted_points_max = 18
# wanted_points is the math domain [wanted_points_min,wanted_points_max] (with 0.5 increments)
wanted_points = [wanted_points_min + i / 2 for i in range(int((wanted_points_max - wanted_points_min) * 2) + 1)]


class Node:
    def __init__(self, courses: list[Course]):
        self.courses = courses
        self.total_points = sum([c.points for c in courses])
        self._has_prioritized = {}
        #        (OS, Compilation, Complexity, ComputerStructure)

        # getting the actual values of has_prioritized,
        #    which represent the existence of the prioritized courses mentioned above.
        prioritized_courses = priority_wanted_courses.keys()
        for course in self.courses:
            if course.id in prioritized_courses:
                self._has_prioritized[course.id] = 1

        self.evaluation = 0
        self._exam_differences = []
        self.neighbors = []
        self.operation_set = []

    def is_goal(self) -> bool:
        return self.total_points >= wanted_points_min

    # getting the score/value/evaluation/heuristic of this node:
    def evaluate(self, priority_multiplier: float, goal_bonus: float, project_number_limit: int) -> float:
        """
        :param priority_multiplier: an amplifier to the effect of prioritized courses on the evaluation.
        :param goal_bonus: the bonus gotten by reaching the goal total course points.
        :param project_number_limit: the limit to how many projects are allowed (preference) in the schedule.
        :return: an evaluation score for this node – a heuristic.
        """

        project_punishment = -150

        A_differences, B_differences, project_num = get_exam_differences(self.courses)
        self._exam_differences = A_differences + B_differences
        if project_number_limit < project_num:
            project_num *= 10
        exam_period_score = evaluate_exam_period_average(
            A_differences, B_differences, evaluate_diff_thresholds2)
        if exam_period_score == float('-inf'): return float('-inf')

        priority_bonus = sum([priority_wanted_courses[ID] for ID, val in self._has_prioritized.items() if val == 1])
        priority_bonus *= priority_multiplier

        x = self.total_points
        if x < wanted_points_min:
            x_displacement = x - wanted_points_min
        elif x > wanted_points_max:
            x_displacement = x - wanted_points_max
        else:
            x_displacement = 0
        stretch_factor = 5  # 2.5
        amplitude = 15
        total_points_factor = amplitude * math.exp(-(x_displacement ** 2) / stretch_factor)

        # stress > stress_pivot gives punishment, < stress_pivot gives reward, linear behaviour.
        stress_pivot = 2.5
        stress_score_multiplier = 7
        stress_score = sum([stress_pivot - c.stress for c in self.courses if c.stress > 0])
        stress_score *= stress_score_multiplier
        rating_pivot = 3
        rating_score_multiplier = 3
        rating_score = sum([c.rating - rating_pivot for c in self.courses if c.rating > 0])
        rating_score *= rating_score_multiplier

        bad_average_supremum = 75
        # good_average_infimum = 85
        super_good_infimum = 98

        def is_no_feedback_and_do_we_punish(c: Course) -> bool:
            if -1 not in [c.stress, c.rating]:
                return False
            if c.average is None:
                return True
            if c.average < bad_average_supremum:
                return True
            if c.average > super_good_infimum:
                return False
            if len(c.grades) >= 1.5 * c.SEMESTERS_BACK_TO_TAKE_INTO_ACCOUNT:
                return False
            return True

        punishment_per_no_feedback_factor = 50
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

        final_score = ((priority_bonus / amplitude + exam_period_score +
                        total_feedback_score + new_courses_punishment) * total_points_factor
                       + project_num * project_punishment + goal_bonus * self.is_goal())

        self.evaluation = final_score / 5
        return final_score

    #

    def get_neighbors(self, relevant_courses_dict: dict) -> list['Node']:
        """
        :param relevant_courses_dict: a dictionary containing the relevant courses, ID: CourseObject.
        :return: neighbors of this node based on the operation set provided.
        """
        neighbors = []
        for operation in self.operation_set:
            neighbors.extend(operation(self, relevant_courses_dict))
        self.neighbors = neighbors
        return neighbors

    #

    def __str__(self):
        self.courses.sort(key=sort_based_on_moed_a)

        result = "—————————————————————————————————————————————————————————————\n"
        result += f"total points: {self.total_points}\n"
        result += f"has prioritized: {self._has_prioritized}\n"
        result += f"evaluation: {self.evaluation}\n"
        result += "Courses:\n"
        for course in self.courses:
            result += f"{course}\n"

        result += "\n"
        result += "Exam Days| Course ID| Points | MoedA date   , MoedB date    | stress, rating |  AVG  | Course Name\n"
        for diff, course in self._exam_differences:
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


def get_neighbors_del_course(node: Node, trash_param) -> list[Node]:
    """
    :param node: the current node
    :param trash_param: dummy param to simplify logic of where this func is used
    :return: neighbors of node that are gotten by deleting a single course from node's course list.
    """

    neighbors = []

    node_courses_dict = {}
    for c in node.courses:
        node_courses_dict[c.id] = c

    for course in node.courses:
        new_courses = deepcopy(node.courses)
        new_courses.remove(course)
        for c in node.courses:
            # if the course we removed was a parallel to another course, remove the other course.
            if course.id in c.parallels:
                new_courses.remove(c)

        neighbor = Node(new_courses)
        neighbor.operation_set = node.operation_set
        neighbors.append(neighbor)

    return neighbors


def get_neighbors_del_2_courses(node: Node, relevant_courses_dict: dict) -> list[Node]:
    neighbors = []

    allowed_wiggle_room = 2
    if node.total_points < wanted_points_max + allowed_wiggle_room:  # no need to remove 2 courses because that is too much
        return neighbors

    neighbors_del = get_neighbors_del_course(node, relevant_courses_dict)
    for neighbor in neighbors_del:
        neighbors.extend(get_neighbors_del_course(neighbor, relevant_courses_dict))
    return neighbors


def get_neighbors_add_course(node: Node, relevant_courses_dict: dict) -> list[Node]:
    """
    :param node: the current node
    :param relevant_courses_dict: a dictionary containing the relevant courses, ID: CourseObject.
    :return: neighbors of node that are gotten by adding one course to node's course list.
    """

    neighbors = []

    if node.total_points >= 23:  # no need to try and get more courses because that is too much
        return neighbors

    remaining_courses = deepcopy(relevant_courses_dict)
    for course in node.courses:
        for equivalent in course.equivalents:
            remaining_courses.pop(equivalent, None)
        remaining_courses.pop(course.id, None)

    for course in remaining_courses.values():
        new_courses = deepcopy(node.courses)
        new_courses.append(course)
        for parallel_id in course.parallels:
            # if the parallel is cannot be taken, then this is an invalid schedule.
            if parallel_id not in remaining_courses:
                continue
            # if it can be taken, we must take it.
            new_courses.append(relevant_courses_dict[parallel_id])
        neighbor = Node(new_courses)
        neighbor.operation_set = node.operation_set
        neighbors.append(neighbor)

    return neighbors


def get_neighbors_replace_course(node: Node, relevant_courses_dict: dict) -> list[Node]:
    """
    :param node: the current node
    :param relevant_courses_dict: a dictionary containing the relevant courses, ID: CourseObject.
    :return: neighbors of node that are gotten by replacing one course in node's course list.
    """

    neighbors_del = get_neighbors_del_course(node, relevant_courses_dict)
    neighbors = []
    remaining_courses = deepcopy(relevant_courses_dict)
    for course in node.courses:
        remaining_courses.pop(course.id, None)

    for neighbor in neighbors_del:
        neighbors.extend(get_neighbors_add_course(neighbor, remaining_courses))
    neighbors.extend(neighbors_del)
    return neighbors
