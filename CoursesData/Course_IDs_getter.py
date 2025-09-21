from CourseDataScrappingFromCheeseFork import course_ids


def check_course_id_existence(line: str) -> (bool, str):
    mask = 0x10001000  # = 1 000 1 000

    potential_id = line[-8:]
    potential_id_hex = 0x0

    for c in potential_id:
        if not c.isdigit(): return False, ""
        potential_id_hex = (potential_id_hex << 0x4) + int(c)

    masking_result = mask & potential_id_hex
    if masking_result == 0:
        return True, potential_id

    return False, ""


def update_course_ids() -> list:
    course_ids.clear()
    List_A_and_B_text_file_path = "List_A_and_B_string.txt"
    with open(List_A_and_B_text_file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip('\n')
            id_exists, course_id = check_course_id_existence(line)
            if id_exists:
                course_ids.append(course_id)
        # print(course_ids)
    return course_ids