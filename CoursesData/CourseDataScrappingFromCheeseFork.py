from selenium.webdriver.remote.webelement import WebElement
from typing_extensions import Final

from Course_Information_Containers.Containers_Processing import get_container_string_from_text, COURSE_ID_LENGTH
from CoursesData import Course_IDs_getter

import time
import random
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, )
from selenium.webdriver.support.ui import WebDriverWait

# webdriver-manager will auto-download the ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from winsound import Beep

# ---------------------------
# User config
# ---------------------------
YEAR = 2026
SEMESTER = 1
CHEESEFORK_URL = f"https://cheesefork.cf/?semester={YEAR - 1}0{SEMESTER}"
WORKDIR = Path("../Course_Information_Containers")
WORKDIR.mkdir(exist_ok=True)

# Put all course ids here (example IDs; replace/extend with the full list)
course_ids = [
    "02340114", "02340117", "02340118", "02340123", "02340124", "02340125", "02340128", "02340129", "02340141",
    "02340218", "02340221", "02340247", "02340292", "02340313", "02340326", "02340329", "02340493", "02340901",
    "02360002", "02360003", "02360004", "02360005", "02360006", "02360007", "02360008", "02360009", "02360010",
    "02360011", "02360012", "02360013", "02360014", "02360016", "02360025", "02360026", "02360125", "02360201",
    "02360203", "02360204", "02360205", "02360206", "02360207", "02360216", "02360268", "02360270", "02360271",
    "02360272", "02360278", "02360299", "02360303", "02360304", "02360306", "02360309", "02360310", "02360313",
    "02360315", "02360318", "02360319", "02360321", "02360322", "02360323", "02360324", "02360328", "02360329",
    "02360330", "02360332", "02360333", "02360334", "02360336", "02360340", "02360341", "02360342", "02360345",
    "02360346", "02360347", "02360348", "02360349", "02360350", "02360351", "02360356", "02360357", "02360358",
    "02360359", "02360360", "02360361", "02360363", "02360366", "02360369", "02360370", "02360371", "02360372",
    "02360373", "02360374", "02360376", "02360377", "02360378", "02360379", "02360381", "02360388", "02360422",
    "02360490", "02360491", "02360496", "02360499", "02360500", "02360501", "02360502", "02360503", "02360504",
    "02360506", "02360508", "02360509", "02360510", "02360512", "02360513", "02360515", "02360518", "02360520",
    "02360521", "02360522", "02360523", "02360524", "02360525", "02360526", "02360612", "02360613", "02360620",
    "02360621", "02360622", "02360623", "02360624", "02360625", "02360627", "02360628", "02360629", "02360630",
    "02360631", "02360632", "02360633", "02360634", "02360635", "02360637", "02360638", "02360640", "02360641",
    "02360643", "02360644", "02360645", "02360646", "02360647", "02360648", "02360649", "02360650", "02360651",
    "02360652", "02360653", "02360654", "02360655", "02360657", "02360658", "02360660", "02360661", "02360662",
    "02360663", "02360664", "02360667", "02360668", "02360669", "02360670", "02360698", "02360700", "02360703",
    "02360712", "02360715", "02360716", "02360719", "02360729", "02360754", "02360755", "02360757", "02360759",
    "02360760", "02360763", "02360766", "02360767", "02360768", "02360777", "02360779", "02360780", "02360781",
    "02360800", "02360811", "02360812", "02360813", "02360814", "02360815", "02360816", "02360817", "02360818",
    "02360819", "02360820", "02360821", "02360822", "02360823", "02360824", "02360825", "02360826", "02360827",
    "02360828", "02360829", "02360830", "02360831", "02360832", "02360833", "02360834", "02360835", "02360836",
    "02360837", "02360838", "02360839", "02360860", "02360861", "02360862", "02360873", "02360874", "02360875",
    "02360927", "02360990", "02360991", "02380100", "02380125", "02380739", "02380790",
    "00360044", "00440105", "00440127", "00440131", "00440137", "00440157", "00440167", "00440169", "00440202",
    "00460201", "00460206", "00460332", "00460880", "00480878", "00480921", "00860761", "00940222", "00940313",
    "00940314", "00940333", "00940334", "00940423", "00940591", "00960200", "00960211", "00960224", "00960250",
    "00960262", "00960326", "00960411", "00970317", "01040122", "01040135", "01040142", "01040157", "01040165",
    "01040174", "01040158", "01040177", "01040192", "01040221", "01040223", "01040276", "01040279", "01040293",
    "01040294", "01060378", "01060383", "01140101", "01140246", "01150203", "01150204", "01140036", "01160217",
    "01160354", "01240120", "01240400", "01240503", "01240801", "01250801", "01340019", "01340020", "01340058",
    "01340082", "01340113", "01340128", "01340119", "01340142", "02140909",
]

HEADLESS = False  # set True to run headless
SAVE_SCREENSHOT = True  # set False to skip screenshots
DELAY_BETWEEN = (0, 1.0)  # random sleep between searches (seconds)
MAX_WAIT = 2  # seconds to wait for results to appear per search
START_INDEX = 0  # change to resume from a specific index if interrupted


# ---------------------------
# Helper functions
# ---------------------------
def try_find_search_input(driver):
    """Try several selectors to find the search input on CheeseFork."""
    selectors = [
        (By.CSS_SELECTOR, 'input[type="search"]'),
        (By.CSS_SELECTOR, 'input[placeholder*="חיפוש"]'),
        (By.CSS_SELECTOR, 'input[placeholder*="Search"]'),
        (By.CSS_SELECTOR, 'input[name="search"]'),
        (By.CSS_SELECTOR, 'input[name="q"]'),
        (By.CSS_SELECTOR, 'input#search'),
        (By.XPATH, "//input[contains(@placeholder,'חיפוש')]"),
        (By.XPATH, "//input[contains(@aria-label,'search')]"),
        (By.TAG_NAME, "input"),
    ]
    for by, sel in selectors:
        try:
            elems = driver.find_elements(by, sel)
            for e in elems:
                # basic sanity check - visible and enabled
                if e.is_displayed() and e.is_enabled():
                    return e
        except Exception:
            continue
    raise NoSuchElementException("Could not find a suitable search input on the page.")


def close_cookie_banner_if_present(driver):
    """Attempt to close cookie or welcome banners (best-effort)."""
    candidates_xpath = [
        "//button[contains(., 'Accept') or contains(., 'ACCEPT') or contains(., 'הבנתי') or contains(., 'אני מסכים')]",
        "//button[contains(., 'Agree') or contains(., 'Agree')]",
        "//button[contains(., 'סגור') or contains(., 'Close') or contains(., 'close')]",
    ]
    for xp in candidates_xpath:
        try:
            btns = driver.find_elements(By.XPATH, xp)
            for b in btns:
                if b.is_displayed() and b.is_enabled():
                    try:
                        b.click()
                        time.sleep(0.4)
                        return
                    except Exception:
                        continue
        except Exception:
            continue
    # no banner found or couldn't close — that's fine, continue


def wait_for_search_results(driver, course_id):
    """
    Wait for an element in the results that likely indicates that the search finished.
    Strategy: wait for either a results container or for URL to change / for presence of course id text.
    """
    try:
        # Wait for some results container to appear OR an element with the course id text.
        WebDriverWait(driver, MAX_WAIT).until(
            lambda d: (
                    d.find_elements(By.CSS_SELECTOR, ".course-card") or
                    d.find_elements(By.XPATH, f"//*[contains(text(), '{course_id}')]") or
                    "search" in d.current_url
            )
        )
    except TimeoutException:
        # fallback: just sleep a little longer and proceed
        time.sleep(1.0)


def wait_for_course_results(driver, By, key_word):
    """
    Wait for an element in the results that likely indicates that the search finished.
    Strategy: wait for either a results container or for URL to change / for presence of course id text.
    """
    try:
        # Wait for some results container to appear OR an element with the course id text.
        WebDriverWait(driver, MAX_WAIT).until(
            lambda d: (d.find_element(By, key_word))
        )
        time.sleep(0.1)
    except TimeoutException:
        # fallback: just sleep a little longer and proceed
        time.sleep(1.0)


# ---------------------------
# Main
# ---------------------------
def main():
    global course_ids
    course_ids = Course_IDs_getter.update_course_ids()

    # Resulting Data Storage variable
    courses_containers = []
    courses_grades = {}

    chrome_opts = Options()
    if HEADLESS:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--start-maximized")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_opts)
    try:
        driver.get(CHEESEFORK_URL)
        time.sleep(1.2)
        close_cookie_banner_if_present(driver)
        # initiating this for later below as base case
        prev_course_info_container = ""
        try_find_search_input(driver).send_keys(Keys.ESCAPE)

        for i, cid in enumerate(course_ids[START_INDEX:], start=START_INDEX):
            try:
                print(f"[{i}/{len(course_ids) - 1}] Searching course id: {cid}")
                # find search input
                search_input = try_find_search_input(driver)

                # Clear previous value (some inputs may require .clear() + select-all)
                try:
                    search_input.clear()
                except Exception:
                    pass
                # click to focus and send the course id
                try:
                    search_input.click()
                    # safety small pause
                    time.sleep(0.12)
                except Exception:
                    pass

                # Send keys
                search_input.send_keys(cid)
                # small additional delay to let JS render fully
                time.sleep(random.uniform(0.2, 0.5))
                # Press ENTER
                search_input.send_keys(Keys.ENTER)

                # Wait for results to load
                wait_for_search_results(driver, cid)

                # small additional delay to let JS render fully
                time.sleep(random.uniform(0.6, 1.6))

                # Pressing course-information button
                i_buttons = driver.find_elements(By.CLASS_NAME, "course-button-list-badge-text")
                wanted_button = i_buttons[-1]
                wanted_button.click()

                # —————————————getting course information data——————————————————

                key_word_info = "course-information"

                # Wait for results to load
                wait_for_course_results(driver, By.CLASS_NAME, key_word_info)

                # Saving course information container string in a file
                course_info_element = driver.find_element(By.CLASS_NAME, key_word_info)
                course_info_container = course_info_element.get_attribute("outerHTML")

                # —————————————————getting feedback data——————————————————————
                key_word_feedback = "course-feedback-summary"

                wait_for_course_results(driver, By.ID, key_word_feedback)

                course_feedback_container = ""

                try:
                    course_feedback_summary_element = driver.find_element(By.ID, key_word_feedback)
                except Exception:
                    course_feedback_summary_element = None
                assert course_feedback_summary_element is not None, "course_feedback_summary_element is none"

                try:
                    course_feedback_container_element = course_feedback_summary_element.find_element(By.TAG_NAME,
                                                                                                     "div")
                except Exception:
                    course_feedback_container_element = None

                # deals with the case where there is no feedback for the course.
                if course_feedback_container_element is not None:
                    course_feedback_container = course_feedback_container_element.get_attribute("outerHTML")

                # ————————————getting histograms data (course averages)—————————————————

                key_word_histogram = "histogram-content"

                wait_for_course_results(driver, By.ID, key_word_histogram)

                try:
                    course_histograms_wrapper_element = driver.find_element(By.CLASS_NAME, key_word_histogram)
                except Exception:
                    course_histograms_wrapper_element = None

                course_average = None
                if course_histograms_wrapper_element is not None:
                    histograms_element = course_histograms_wrapper_element.find_element(By.TAG_NAME, "select")
                    YEARS_TO_TAKE_INTO_ACCOUNT = 7
                    histogram_per_year_elements = histograms_element.find_elements(By.TAG_NAME, "option")

                    def take_average_from_histograms_options(histogram_options: list[WebElement]):
                        sum = 0
                        count = 0
                        key_word_FINAL = "סופי "
                        i = 0
                        for option in histogram_options:
                            if i >= YEARS_TO_TAKE_INTO_ACCOUNT:
                                break
                            text = option.text

                            idx_grade = text.find(key_word_FINAL)
                            if idx_grade == -1:
                                continue
                            i += 1
                            idx_grade += len(key_word_FINAL)
                            grade = int(text[idx_grade:idx_grade + 2])
                            count += 1
                            sum += grade
                        return sum / count

                    course_average = take_average_from_histograms_options(histogram_per_year_elements)

                if prev_course_info_container != course_info_container:
                    courses_containers.append((course_info_container, course_feedback_container))
                    courses_grades[cid] = course_average
                    print(f"  -> saved container and average of: {cid}")
                    prev_course_info_container = course_info_container
                else:
                    print(f"  -> {cid} is not passed this semester")

                # Random delay between searches to appear human-like
                time.sleep(random.uniform(*DELAY_BETWEEN))

                # Navigate back to main search page in case the search navigated away
                # (this keeps behavior consistent)
                driver.get(CHEESEFORK_URL)
                time.sleep(0.6)
                close_cookie_banner_if_present(driver)
            except Exception as ex:
                print(f"Error while processing {cid}: {ex}")
                # Optional: save error page for debugging
                err_path = WORKDIR / f"{cid}_error.txt"
                with open(err_path, "w", encoding="utf-8") as f:
                    f.write(str(ex))
                # continue to next id
                time.sleep(1.0)
                driver.get(CHEESEFORK_URL)
                time.sleep(0.6)
                close_cookie_banner_if_present(driver)

    finally:

        # —————————storing data into file as ready-to-use python variables—————————————

        safe_name = f"Courses_Containers.py"
        file_path = WORKDIR / safe_name
        with open(file_path, "w", encoding="utf-8") as f:
            def write_course_containers_into_file():
                f.write("courses_containers = [")
                list_content = ""
                for info_container, feedback_container in courses_containers:
                    list_content += f"\n        ("
                    list_content += f"\n        '{info_container.replace("'", '`').replace("\n", "\\n")}',"
                    list_content += f"\n        '{feedback_container.replace("'", '`').replace("\n", "\\n")}'"
                    list_content += f"\n        ),"
                f.write(list_content[0:-1] + "]")

            def write_course_exam_dates_into_file():
                def get_course_exam_dates() -> dict:
                    exam_info_container = driver.find_element(By.ID, "course-exam-info")
                    exam_A_and_B_info_containers = exam_info_container.find_elements(By.CLASS_NAME, "exam-info-content")
                    exam_A_info_container, exam_B_info_container = exam_A_and_B_info_containers[0].find_element(
                        By.TAG_NAME,
                        "span"), \
                        exam_A_and_B_info_containers[1].find_element(By.TAG_NAME, "span")

                    def get_moed_course_elements(moed_info_container: WebElement) -> list[WebElement]:
                        moed_elements = moed_info_container.find_elements(By.TAG_NAME, "span")
                        moed_course_elements = [element for element in moed_elements if
                                                "exam-info-item exam-info-item-course" in element.get_dom_attribute(
                                                    "class")]
                        return moed_course_elements

                    displacement_for_course_id = len("exam-info-item exam-info-item-course-")

                    def get_course_exam_from_span_element(element: WebElement) -> (str, str):
                        course_id = element.get_dom_attribute("class")[
                                    displacement_for_course_id:displacement_for_course_id + COURSE_ID_LENGTH]

                        # if this element is not the first one, the date is in the following property:
                        exam_day_month = element.get_attribute("data-original-title")

                        # if this element is the first one, then it contains the date in text
                        if exam_day_month is None:
                            exam_day_month = element.find_element(By.CLASS_NAME, "content-absolute").text

                        exam_date_ISO = f"{YEAR}-" + "-".join(exam_day_month.split("/")[::-1])
                        return course_id, exam_date_ISO

                    moed_A_course_elements = get_moed_course_elements(exam_A_info_container)
                    moed_B_course_elements = get_moed_course_elements(exam_B_info_container)
                    course_exams_dict: dict[str:list[str, str]] = {}
                    for element in moed_A_course_elements:
                        course_id, exam_date_ISO = get_course_exam_from_span_element(element)
                        course_exams_dict[course_id] = [None, None]
                        course_exams_dict[course_id][0] = exam_date_ISO

                    for element in moed_B_course_elements:
                        course_id, exam_date_ISO = get_course_exam_from_span_element(element)

                        # some courses may have only one exam (eg: project deadline) which may be signed as Moed B for convenience
                        if course_id not in course_exams_dict:
                            course_exams_dict[course_id] = [None, ""]

                        course_exams_dict[course_id][1] = exam_date_ISO
                    return course_exams_dict

                course_exams_dict = get_course_exam_dates()
                f.write("course_exams_dict = {")
                dict_content = ""
                for course_id, exams in course_exams_dict.items():
                    dict_content += f"\n        '{course_id}': ['{exams[0]}','{exams[1]}'],"
                f.write(dict_content[0:-1] + "}")

            def write_courses_grades_into_file():
                f.write("courses_grades = {")
                dict_content = ""
                for course_id, grade in courses_grades.items():
                    dict_content += f"\n        '{course_id}': {grade},"
                f.write(dict_content[0:-1] + "}")

            write_courses_grades_into_file()
            f.write("\n\n")
            write_course_exam_dates_into_file()
            f.write("\n\n")
            write_course_containers_into_file()

        # —————————————————printing finish message and making sound——————————————————————
        print(f"  -> saved courses containers at: {file_path}!")
        for i in range(1, 2):
            Beep(500, 400)
            time.sleep(0.4)
            Beep(700, 400)
            time.sleep(0.4)
            Beep(900, 900)
            time.sleep(0.9)
            Beep(500, 999)
            time.sleep(0.999)
        # driver.quit()
        print("Done. All saved to:", WORKDIR.resolve())
        time.sleep(120)


if __name__ == "__main__":
    main()
