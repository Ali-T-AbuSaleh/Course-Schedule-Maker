import json
from abc import abstractmethod
from copy import deepcopy

GET_FROM_JSON_FILE_PATH = "Courses_Containers_and_Data.json"

STORE_IN_JSON_FILE_PATH = "../CoursesData/courses_data_json.json"
COURSE_ID_LENGTH = 8


def get_container_string_from_text(text: str, container_opening: str, container_closing):
    num_opened = 1
    num_closed = 0

    added_idx = 0

    next_closing_idx = -1
    next_opening_idx = text.find(container_opening)
    text = text[next_opening_idx:]
    text_copy = text[len(container_opening):]
    added_idx += next_opening_idx + len(container_opening)
    next_opening_idx = -1

    while text_copy != "":
        assert num_opened > num_closed
        if next_closing_idx < 0:
            next_closing_idx = text_copy.find(container_closing)
            num_closed += 1
        if next_opening_idx < 0:
            next_opening_idx = text_copy.find(container_opening)

        if next_closing_idx == -1:
            num_closed -= 1
            raise ValueError("\nText doesnt have a closing for the container!\n\n")
        final_closing_idx = next_closing_idx

        if next_opening_idx == -1:  # then we did not find another opening

            trim_start_idx = next_closing_idx + len(container_closing)
            next_closing_idx = -1

        else:
            if next_closing_idx < next_opening_idx:
                trim_start_idx = next_closing_idx + len(container_closing)
                next_closing_idx = -1
                next_opening_idx -= trim_start_idx
            else:
                num_opened += 1
                trim_start_idx = next_opening_idx + len(container_opening)
                next_opening_idx = -1
                next_closing_idx -= trim_start_idx

        if num_closed == num_opened:
            return text[0:final_closing_idx + len(container_closing) + added_idx]

        assert trim_start_idx > 0 or trim_start_idx < len(text_copy), "\nsomething went wrong with trimming\n\n"

        text_copy = text_copy[trim_start_idx:]
        added_idx += trim_start_idx

    raise ValueError("\nText doesnt have a closing for the container!\n\n")


class DecisionNode:
    def __init__(self, data: list):
        self.data = deepcopy(data)

    @abstractmethod
    def type(self) -> str: ...

    @abstractmethod
    def repr_as_logic_with_variable(self, dict_name_courses_taken) -> str: ...

    @abstractmethod
    def __str__(self) -> str: ...

    def __repr__(self) -> str:
        return self.__str__()


class AndNode(DecisionNode):
    def __init__(self, data: list):
        super().__init__(data)

    def type(self) -> str:
        return "and"

    def repr_as_logic_with_variable(self, dict_name_courses_taken) -> str:
        return "(" + " & ".join([
            f"{expression.repr_as_logic_with_variable(dict_name_courses_taken) if isinstance(expression, DecisionNode) else f"{dict_name_courses_taken}.get('{expression}',False)"}"
            for expression in self.data]) + ")"

    def __str__(self) -> str:
        return "(" + " & ".join(map(str, self.data)) + ")"


class OrNode(DecisionNode):
    def __init__(self, data: list):
        super().__init__(data)

    def type(self) -> str:
        return "or"

    def repr_as_logic_with_variable(self, dict_name_courses_taken) -> str:
        return "(" + " | ".join([
            f"{expression.repr_as_logic_with_variable(dict_name_courses_taken) if isinstance(expression, DecisionNode) else f"{dict_name_courses_taken}.get('{expression}',False)"}"
            for expression in self.data]) + ")"

    def __str__(self) -> str:
        return "(" + " | ".join(map(str, self.data)) + ")"


from html.parser import HTMLParser
from typing import List, Union


class PrereqHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_a = False
        self.tokens: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'a':
            self.in_a = True

    def handle_endtag(self, tag):
        if tag.lower() == 'a':
            self.in_a = False

    def handle_data(self, data):
        data = data.strip()
        if not data:
            return
        if self.in_a:
            self.tokens.append(data.strip())
        else:
            s = data.replace('(', ' ( ').replace(')', ' ) ')
            s = s.replace('ו-', ' ו- ')
            parts = [p for p in s.split() if p.strip()]
            for p in parts:
                if p == '(' or p == ')':
                    self.tokens.append(p)
                else:
                    if p == 'או':
                        self.tokens.append('או')
                    elif p == 'ו' or p == 'ו-':
                        self.tokens.append('ו')
                    else:
                        pass


def parse_prereqs_from_html(html: str) -> OrNode:
    parser = PrereqHTMLParser()
    parser.feed(html)
    tokens = parser.tokens

    idx = 0

    def peek():
        return tokens[idx] if idx < len(tokens) else None

    def consume(expected=None):
        nonlocal idx
        t = peek()
        if expected and t != expected:
            raise ValueError(f"expected {expected}, got {t}")
        idx += 1
        return t

    def parse_atom() -> Union[str, List]:
        t = peek()
        if t == '(':
            consume('(')
            node = parse_or()
            if peek() != ')':
                raise ValueError("Missing closing parenthesis")
            consume(')')
            return node
        elif t is None:
            raise ValueError("Unexpected end")
        else:
            return consume()

    def parse_and() -> str | list | AndNode:
        data = [parse_atom()]
        while peek() == 'ו':
            consume('ו')
            data.append(parse_atom())
        if len(data) == 1:
            return data[0]
        return AndNode(data)

    def parse_or() -> str | list | AndNode | OrNode:
        data = [parse_and()]
        while peek() == 'או':
            consume('או')
            data.append(parse_and())
        if len(data) == 1:
            return data[0]
        return OrNode(data)

    parsed = parse_or()

    def collect(node) -> OrNode:
        if isinstance(node, str):
            return OrNode([node])
        else:
            return node

    result = collect(parsed)
    return result


def get_course_name_and_id_from_container(info_container: str) -> (str, str):
    # trimming the prefix:
    trim = info_container[37:]
    # trimming the suffix and getting the string in the shape of:
    # <ID> - <NAME>
    id_name_string = trim[:trim.find('<')]
    return id_name_to_tuple(id_name_string)


def id_name_to_tuple(id_name: str) -> (str, str):
    separated_by_dash = id_name.split('-')

    # removing additional space:
    id = separated_by_dash[0].strip(' ')
    # removing id:
    separated_by_dash = separated_by_dash[1:]
    # removing additional space and joining the course name back (if it split):
    name = "-".join(separated_by_dash)[1:]
    return name, id


def get_course_points(info_container: str) -> float:
    key_word_points = "<br>נקודות: "
    idx = info_container.find(key_word_points)
    assert idx != -1
    trim = info_container[idx + len(key_word_points):]
    points_str = trim[:trim.find('<')]
    result = float(points_str)
    return result


def get_course_prerequisites(info_container) -> OrNode:
    prerequisites: OrNode

    # getting the index of the start of the "<span>" info_container that has the prerequisites
    idx = info_container.find("<span>מקצועות קדם: ")
    if idx == -1:
        return OrNode(["No Prerequisites"])
    prerequisites_container = get_container_string_from_text(info_container[idx:], "<span", "</span>")

    prerequisites = parse_prereqs_from_html(prerequisites_container)

    return prerequisites


def get_course_equivalents(info_container: str) -> list:
    result = (
        get_included_courses(info_container))
    result.extend(
        get_courses_that_include_this_course(info_container))
    result.extend(
        get_courses_from_simple_list_in_container(info_container, "<span>מקצועות ללא זיכוי נוסף: "))
    return result


def get_included_courses(info_container: str) -> list:
    return get_courses_from_simple_list_in_container(info_container, "<span>מקצועות ללא זיכוי נוסף (מוכלים): ")


def get_courses_that_include_this_course(info_container: str) -> list:
    return get_courses_from_simple_list_in_container(info_container, "<span>מקצועות ללא זיכוי נוסף (מכילים): ")


def get_course_parallels(info_container: str) -> list:
    return get_courses_from_simple_list_in_container(info_container, "<span>מקצועות צמודים: ")


def get_courses_from_simple_list_in_container(info_container: str, list_starting_at: str) -> list:
    list: List
    idx = info_container.find(list_starting_at)
    if idx == -1:
        return []
    list_container = get_container_string_from_text(info_container[idx:], "<span", "</span>")
    parser = PrereqHTMLParser()
    parser.feed(list_container)
    if parser.tokens is None: return []

    result = [token for token in parser.tokens if token not in ['(', ')']]
    return result


def get_course_weight(feedback_container: str) -> float:
    full_weight_class_id = "fas fa-weight-hanging"
    half_weight_svg_code = "m510.28,445.86l-73.03,-292.13c-3.8,-15.19 -16.44,-25.72 -30.87,-25.72l-72.41,0c6.2,-12.05 10.04,-25.51 10.04,-40c0,-48.6 -39.4,-88 -88,-88s-88,39.4 -88,88c0,14.49 3.83,27.95 10.04,40l-72.41,0c-14.43,0 -27.08,10.54 -30.87,25.72l-73.05,292.13c-8.33,33.31 14.66,66.14 46.31,66.14l415.95,0c31.64,0 54.63,-32.83 46.3,-66.14zm-294.28,-357.86c0,-22.06 17.94,-40 40,-40s40,17.94 40,40c0,22.05 -17.94,40 -40,40s-40,-17.95 -40,-40zm246.72,376c-137.64664,0 -69.07336,0 -206.72,0l0,-288l137.34,0l70.38,281.5c0.81,3.27 -0.3,5.54 -1,6.5z"
    feedback_type = "עומס"
    return get_course_general_feedback(feedback_container, feedback_type, full_weight_class_id, half_weight_svg_code)


def get_course_rating(feedback_container: str) -> float:
    full_star_class_id = "fas fa-star"
    half_star_class_id = "fas fa-star-half-alt"
    feedback_type = "כללי"
    return get_course_general_feedback(feedback_container, feedback_type, full_star_class_id, half_star_class_id)


def get_course_general_feedback(feedback_container: str, feedback_type: str, full_star_class_id: str,
                                half_star_class_id: str) -> float:
    if feedback_container == "":
        return -1
    feedback = 0
    idx = feedback_container.find(feedback_type) + 3
    general_feedback_container = get_container_string_from_text(feedback_container[idx:], "<div", "</div>")
    while idx != -1:
        idx = general_feedback_container.find(full_star_class_id)
        feedback += 1
        general_feedback_container = general_feedback_container[idx + len(full_star_class_id):]
    feedback -= 1

    idx = general_feedback_container.find(half_star_class_id)
    if idx != -1:
        feedback += 0.5
    return feedback


if __name__ == '__main__':
    with open(GET_FROM_JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        data_dict = json.load(f)

    courses_grades = data_dict["courses_grades"]
    course_exams_dict = data_dict["course_exams_dict"]
    courses_containers = data_dict["courses_containers"]

    containers = [(info, feedback) for info, feedback in courses_containers]

    dict_results_organized = {}

    for container in containers:
        info = container[0]
        feedback = container[1]

        name, ID = get_course_name_and_id_from_container(info_container=info)
        points = get_course_points(info_container=info)
        prerequisites = get_course_prerequisites(info_container=info)
        prerequisites_logical_expression = prerequisites.repr_as_logic_with_variable(
            dict_name_courses_taken="completed_courses")
        equivalents = get_course_equivalents(info_container=info)
        parallels = get_course_parallels(info_container=info)
        weight = get_course_weight(feedback)
        rating = get_course_rating(feedback)
        course_grades = courses_grades.get(ID, None)

        exams = course_exams_dict[ID] if ID in course_exams_dict.keys() else [None, None]
        moed_a = exams[0]
        moed_b = exams[1]

        dict_results_organized[ID] = {
            "name": name,
            "id": ID,
            "points": points,
            "prerequisites_logical_expression": prerequisites_logical_expression,
            "equivalents": equivalents,
            "parallels": parallels,
            "stress": weight,
            "rating": rating,
            "course_grades": course_grades,
            "moed_a": moed_a,
            "moed_b": moed_b
        }
    with open(STORE_IN_JSON_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(dict_results_organized, f, ensure_ascii=False, indent=4)
