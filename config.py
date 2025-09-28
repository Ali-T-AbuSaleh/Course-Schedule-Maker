from Helpers.Mode import Mode


# change to Mode.USER when not debugging.
MODE = Mode.DEBUG

COURSES_DATA_JSON_PATH = "CoursesData/courses_data_json.json"
ADDITIONAL_RUNS = 4
starting_temperature = 10000
convergence_factor = 0.95
epsilon = 10 ** -9
