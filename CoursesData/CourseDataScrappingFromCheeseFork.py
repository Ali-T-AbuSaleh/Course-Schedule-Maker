from CoursesData import Course_IDs_getter


def get_container_string_from_text(text: str, container_opening: str):
    container_closing = "</" + container_opening + ">"
    container_opening = "<" + container_opening
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


# def test_func(func, inputs: tuple, true_result, test_number):
#     result = func(*inputs)
#     if result != true_result:
#         print(f"test {test_number} failed")
#         result = fold_string(result, 150)
#         print(result + '\n')
#     else:
#         print(f"test {test_number} passed")
#
#
# def fold_string(string, max_length) -> str:
#     if len(string) <= max_length:
#         return string
#     trim = str(string[:max_length])
#     trim = trim[::-1]
#     trim = trim[trim.find(' ') + 1:]
#     trim = trim[::-1]
#
#     remaining = string[len(trim) + 1:]
#
#     return trim + '\n' + fold_string(remaining, max_length)
#
#
# if __name__ == "__main__":
#     true_container1 = container1 = '<span class="exam-info-left-arrow"></span>'
#     true_container2 = (
#         '<span class="exam-info-item exam-info-item-course-02360343" style="background-color: rgb(45, 134, 94);">'
#         '<span class="content-absolute">03/02</span><span class="content-bold-hidden">03/02</span></span>')
#     container2 = true_container2 + 'fcuk safjsdknvclamkd vclkjwadf'
#     true_container4 = "<span>1<span>2<span>3</span></span></span>"
#     container4 = true_container4 + "AAAAAAAAAAAAAAAAA"
#     true_container5 = "<span>1<span>2<span>3</span><span>4</span></span></span>"
#     container5 = true_container5 + "AAAAAAAAAAAAAAAAA"
#     true_container3 = true_container1
#     container3 = container1 + container2
#
#     test_func(get_container_string_from_text, (container1, 'span'), true_container1, test_number=1)
#
#     test_func(get_container_string_from_text, (container2, 'span'), true_container2, test_number=2)
#
#     test_func(get_container_string_from_text, (container3, 'span'), true_container3, test_number=3)
#
#     test_func(get_container_string_from_text, (container4, 'span'), true_container4, test_number=4)
#
#     test_func(get_container_string_from_text, (container5, 'span'), true_container5, test_number=5)

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
CHEESEFORK_URL = "https://cheesefork.cf/?semester=202501"
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


def wait_for_course_info_results(driver, By, key_word, wanted_elem):
    """
    Wait for an element in the results that likely indicates that the search finished.
    Strategy: wait for either a results container or for URL to change / for presence of course id text.
    """
    try:
        # Wait for some results container to appear OR an element with the course id text.
        WebDriverWait(driver, MAX_WAIT).until(
            lambda d: (d.find_elements(By, key_word)[-1]
                       == wanted_elem)
        )
        time.sleep(0.2)
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

                # Wait for results to load
                wait_for_course_info_results(driver, By.CLASS_NAME, "course-button-list-badge-text", wanted_button)

                # Saving course information container string in a file
                key_word = "bootstrap-dialog-message"
                html_text = driver.page_source

                trim_until_course_info = html_text[html_text.find(key_word):]
                course_info_container = get_container_string_from_text(trim_until_course_info, "div")

                if prev_course_info_container != course_info_container:
                    courses_containers.append(course_info_container)
                    print(f"  -> saved container of: {cid}")
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
        safe_name = f"Courses_Containers.py"
        file_path = WORKDIR / safe_name
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("courses_containers = [")
            list_content = ""
            for container in courses_containers:
                list_content += f"\n        '{container.replace("'", '`')}',"
            f.write(list_content[0:-1] + "]")
        # Courses_Containers.courses_containers.append(courses_containers)
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
