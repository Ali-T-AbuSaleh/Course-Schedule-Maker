from selenium.webdriver.remote.webelement import WebElement
import json

from Course_Information_Containers.Data_Processing import get_container_string_from_text, COURSE_ID_LENGTH
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

HEADLESS = False  # set True to run headless
SAVE_SCREENSHOT = True  # set False to skip screenshots
DELAY_BETWEEN = (0, 1.0)  # random sleep between searches (seconds)
MAX_WAIT = 2  # max seconds to wait for results to appear per search


# ---------------------------
# Helper functions
# ---------------------------
def try_find_search_input(driver):
    """Try several selectors to find the search input on CheeseFork."""
    selector = (By.ID, "course-select-selectized")
    try:
        elems = driver.find_elements(*selector)
        for e in elems:
            # basic sanity check - visible and enabled
            if e.is_displayed() and e.is_enabled():
                return e
    except Exception:
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

        for i, cid in enumerate(course_ids):
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

                #Checking if the course exists in the search-list
                key_word_search_results_dropdown = "selectize-dropdown-content"
                search_results_dropdown_elem = driver.find_element(By.CLASS_NAME,key_word_search_results_dropdown)
                # if the dropdown does not have children then it is empty,
                #   meaning that the course is not in the list
                if len(search_results_dropdown_elem.find_elements(By.CLASS_NAME, "option")) == 0:
                    print(f"  -> {cid} is not passed this semester")
                    continue

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

                course_grades = None
                if course_histograms_wrapper_element is not None:
                    histograms_element = course_histograms_wrapper_element.find_element(By.TAG_NAME, "select")
                    histogram_per_semester_elements = histograms_element.find_elements(By.TAG_NAME, "option")

                    def take_grades_from_histograms_options(histogram_options: list[WebElement]) -> dict:
                        semesters_grades = {}
                        key_word_end_of_semester_name = "  "
                        key_word_FINAL = "סופי "
                        for option in histogram_options:
                            text = option.text
                            idx_end_of_semester_name = text.find(key_word_end_of_semester_name)
                            idx_grade = text.find(key_word_FINAL)
                            if idx_grade == -1 or idx_end_of_semester_name == -1:
                                continue

                            semester_name = text[:idx_end_of_semester_name]
                            idx_grade += len(key_word_FINAL)
                            grade = int(text[idx_grade:idx_grade + 2])

                            semesters_grades[semester_name] = grade

                        return semesters_grades

                    course_grades = take_grades_from_histograms_options(histogram_per_semester_elements)

                # Insuring that the course we clicked is not the same one as before,
                #  and then storing only if not.
                assert prev_course_info_container != course_info_container, f"  -> {cid} is not passed this semester"
                courses_containers.append((course_info_container, course_feedback_container))
                courses_grades[cid] = course_grades
                print(f"  -> saved container and average of: {cid}")
                prev_course_info_container = course_info_container

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

        # ———————storing data into json file as ready-to-use python variables———————————

        safe_name = f"Courses_Containers_and_Data.json"
        file_path = WORKDIR / safe_name
        dict_to_store = {}

        def store_course_containers_into_dict():
            dict_to_store["courses_containers"] = courses_containers

        def store_course_exam_dates_into_dict():
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
                        course_exams_dict[course_id] = [None, None]

                    course_exams_dict[course_id][1] = exam_date_ISO
                return course_exams_dict

            course_exams_dict = get_course_exam_dates()
            dict_to_store["course_exams_dict"] = course_exams_dict

        def store_courses_grades_into_dict():
            dict_to_store["courses_grades"] = courses_grades

        store_courses_grades_into_dict()
        store_course_exam_dates_into_dict()
        store_course_containers_into_dict()

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dict_to_store, f, ensure_ascii=False, indent=4)

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
