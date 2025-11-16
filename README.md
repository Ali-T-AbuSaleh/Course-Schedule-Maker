# Course Schedule Maker

An AI-powered course scheduler that web-scrapes academic data and applies local-search optimization algorithms to generate optimal semester schedules under complex constraints.

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 🎯 Overview

This tool automates the tedious process of semester course planning by:

- **Scraping** live course data (exam dates, ratings, stress levels, historical grades, prerequisites)
- **Optimizing** schedule combinations using Simulated Annealing and Steepest Ascent Hill Climbing
- **Balancing** multiple constraints: exam conflicts, workload stress, course ratings, credit requirements, and user preferences

**Result**: Generate conflict-free, optimized course schedules in minutes instead of hours of manual planning.

---

## ✨ Features

### Core Functionality

- **Multi-Algorithm Search**: Choose between Simulated Annealing (probabilistic global search) or Steepest Ascent Hill Climbing (greedy local search)
- **Smart Constraint Handling**:
  - Prerequisite validation via dynamic boolean logical expression evaluation
  - Equivalent course exclusion
  - Parallel course co-enrollment enforcement
  - Completed course filtering
  - User-defined course blacklisting

### Data-Driven Heuristics

- **Exam Conflict Minimization**: Exponential scoring for exam spacing (penalizes <2 days between exams)
- **Workload Balancing**: Weighted stress ratings (linear; pivot at 2.5/5 for optimal difficulty)
- **Quality Maximization**: Course rating integration (linear; pivot at 3/5)
- **Historical Analysis**: 6-semester rolling grade averages with new-course detection
- **New Course Penalty**: Punishes courses with limited historical data (<6 semesters) or low grade averages, prioritizing established courses with proven track records
- **Flexible Credit Targeting**: Gaussian-weighted preference for 16-18 credit hours

### User Customization

- **Priority System**: 1-10 scale for course/exam preferences
- **Course Blacklisting**: Exclude unwanted courses via `unwanted_courses.txt` (even if prerequisites are met)
- **Exam Priority Weighting**: Set higher priorities for courses needing more study time during exam period via `priority_wanted_exams.txt`
- **Completed Courses Input**: Specify already-taken courses via `completed_courses.txt` to filter them out and handle prerequisite validation
- **Configurable Parameters**:
  - Must-meet 18+ credit requirement (hard constraint mode)
  - Priority multipliers (amplify course preferences)
  - Project number limits (control non-exam courses)
  - Semester lookback windows (historical grade analysis)

---

## 🏗️ Architecture

### Project Structure

```
courseScheduleMaker/
├── coursesScheduleMaker.py       # Main orchestrator (SA/HC algorithms)
├── config.py                      # Hyperparameters & global settings
├── CoursesData/
│   ├── CourseDataScrappingFromCheeseFork.py  # Selenium web scraper
│   ├── courses_data_json.json                # Scraped course database
│   ├── Course_IDs_getter.py                  # Course ID extraction
│   ├── List_A_and_B_string.txt               # Raw course list (Lists A & B from catalogue PDF)
│   └── List_Rest_of_Courses.txt              # Raw course list (remaining courses from catalogue PDF)
├── Course_Information_Containers/
│   ├── Courses_Containers_and_Data.json      # Intermediate scraped data (raw HTML containers)
│   └── Data_Processing.py                    # Raw data parser & JSON transformer
├── Objects/
│   ├── Courses.py                 # Course class & exam evaluation logic
│   ├── Node.py                    # State-space node & heuristic function
│   ├── Heap.py                    # MinHeap/MaxHeap for top-N tracking
│   └── Strategy.py                # Algorithm selection enum
├── Helpers/
│   ├── DataGetters.py             # File I/O & course filtering
│   ├── Mode.py                    # DEBUG/USER mode enum
│   └── ValidationFunctions.py     # Input validation utilities
└── UserInput/
    ├── completed_courses.txt      # User's completed courses
    ├── priority_wanted_courses.txt # Course preferences (1-10)
    ├── priority_wanted_exams.txt   # Exam spacing priorities
    └── unwanted_courses.txt        # Blacklisted courses
```

### Algorithm Design

#### **Simulated Annealing**

```python
# Probabilistic acceptance with temperature cooling
T = 10000  # Initial temperature
gamma = 0.95  # Cooling factor

while T > epsilon:
    neighbor = random_pick(current.neighbors)
    ΔE = neighbor.evaluation - current.evaluation

    if ΔE > 0:  # Better solution
        current = neighbor
    else:  # Probabilistic acceptance
        if random() < exp(ΔE / T):
            current = neighbor

    T = gamma * T
```

**Neighbor Operations**:

- `add_course`: Add 1 course (up to 23 credits)
- `delete_course`: Remove 1 course
- `replace_course`: Swap 1 course for another

#### **Heuristic Evaluation Function**

Multi-factor scoring combining:

1. **Total Points Gaussian**: $\text{amplitude} \times e^{-(\text{displacement}^2) / \text{stretch}}$ (peaks at 16-18 credits)
2. **Exam Spacing Exponential**: $5 + 50 \times (-e^{-x/c})$ (rewards 3+ day gaps)
3. **Stress Score**: Linear pivot at 2.5/5 (preference for moderate difficulty)
4. **Rating Score**: Linear pivot at 3/5 (favor well-rated courses)
5. **New Course Penalty**: Punish courses with <6 semesters of historical data
6. **No Feedback Penalty**: Extra punishment for courses lacking stress/rating data
7. **Priority Bonuses**: User-defined weighted preferences (1-10 scale)
8. **Project Limits**: Hard penalty if project-based courses exceed threshold
9. **Goal Bonus**: Reward for meeting 18+ credit requirement

---

## 🚀 Installation

### Prerequisites

- Python 3.x
- Chrome browser (for Selenium WebDriver)

### Setup

```bash
# Clone repository
git clone https://github.com/Ali_T_AbuSaleh/Course-Schedule-Maker.git
cd Course-Schedule-Maker

# Install dependencies
pip install selenium webdriver-manager winsound

# (Optional) Configure Python environment
# See config.py for MODE settings (DEBUG/USER)
```

---

## 📖 Usage

### 1. Configure User Inputs

Edit files in `UserInput/`:

- **completed_courses.txt**: One course ID per line (e.g., `02340123`)
- **priority_wanted_courses.txt**: `<course_id> <priority_1-10>`
- **priority_wanted_exams.txt**: `<course_id> <priority_1-10>`
- **unwanted_courses.txt**: One course ID per line to blacklist

### 2. Scrape Course Data (Optional)

If you need fresh data from CheeseFork:

```bash
# Step 1: Scrape raw data from CheeseFork
python CoursesData/CourseDataScrappingFromCheeseFork.py

# Step 2: Process raw data into optimizer-ready JSON
python Course_Information_Containers/Data_Processing.py
```

This generates `courses_data_json.json` with:

- Exam dates (Moed A/B)
- Stress ratings (1-5)
- Course ratings (1-5)
- Historical grades (6+ semesters)
- Prerequisites & equivalents

### 3. Run Optimizer

```bash
python coursesScheduleMaker.py <num_results> <must18plus> <priority_mult> <project_limit> <wanted_courses.txt> <wanted_exams.txt> <completed.txt> <unwanted.txt>
```

**Example**:

```bash
python coursesScheduleMaker.py 5 true 10 2 UserInput/priority_wanted_courses.txt UserInput/priority_wanted_exams.txt UserInput/completed_courses.txt UserInput/unwanted_courses.txt
```

**Parameters**:

- `num_results`: Number of top schedules to return (e.g., 5)
- `must18plus`: `true` = hard 18+ credit requirement, `false` = soft preference
- `priority_mult`: Amplifier for priority bonuses (e.g., 10)
- `project_limit`: Max project-based courses allowed (e.g., 2)

### 4. Review Results

Output includes top-N schedules ranked by heuristic score:

```
—————————————————————————————————————————————————————————————
total points: 17.5
has prioritized: {'02340123': 1, '02360343': 1}
evaluation: 24.3
Courses:
02340123 | 3.5pts | A: 2026-01-15, B: 2026-02-10 | 2.8/5, 3.5/5 | 85.32 | Operating Systems
02360343 | 4.0pts | A: 2026-01-22, B: 2026-02-17 | 3.1/5, 3.8/5 | 78.45 | Compilation
...

Exam Days| Course ID| Points | MoedA date   , MoedB date    | stress, rating |  AVG  | Course Name
    7    | 02340123 | 3.5pts | 2026-01-15   , 2026-02-10    | 2.8   , 3.5    | 85.32 | Operating Systems
    5    | 02360343 | 4.0pts | 2026-01-22   , 2026-02-17    | 3.1   , 3.8    | 78.45 | Compilation
—————————————————————————————————————————————————————————————
```

---

## ⚙️ Configuration

### Hyperparameters (`config.py`)

```python
MODE = Mode.USER  # or Mode.DEBUG for verbose output
starting_temperature = 10000
convergence_factor = 0.95  # Cooling rate
epsilon = 10 ** -9  # Termination threshold
```

### Algorithm Selection (`coursesScheduleMaker.py`)

```python
strategy = Strategy.SIMULATED_ANNEALING  # or Strategy.STEEPEST_AHC
```

---

## 🧪 Technical Highlights

### Web Scraping Engine

- **Selenium WebDriver** with automatic ChromeDriver management
- Robust error handling: retry logic, cookie-banner dismissal, dynamic waits
- Structured data extraction: DOM parsing with CSS selectors and XPath
- Multi-field scraping: exam dates, feedback (stress/rating), grade distributions

### Optimization Algorithms

- **Simulated Annealing**: Temperature-based probabilistic search with exponential cooling
- **Steepest Ascent HC**: Greedy best-neighbor selection with stochastic tie-breaking

### Data Structures

- **Custom MinHeap/MaxHeap**: Top-N result tracking using `heapq`
- **Node State Representation**: Course list + cached evaluation + neighbor operations
- **Prerequisite DAG**: Dynamic boolean expression evaluation for dependency validation

### Constraint Satisfaction

- **Hard Constraints**: Prerequisites, equivalents, parallels, credit minimums
- **Soft Constraints**: Exam spacing, stress balance, rating maximization
- **User Preferences**: Priority-weighted course selection with configurable multipliers

---

## 📊 Performance

- **Search Space**: Evaluates 1000+ state combinations per SA run
- **Convergence**: Typically reaches stable solutions in 200-500 iterations
- **Speed**: Generates optimized schedules in ~10-30 seconds (depending on course pool size)
- **Quality**: Gaussian-weighted heuristic ensures schedules cluster around optimal 16-18 credit range

---

## 🛠️ Development Timeline

**Sep 18-28, 2025** (10-day sprint, 17 commits):

1. Initial heuristic framework & basic SA implementation
2. Web scraper development (Selenium + CheeseFork integration)
3. Data processing pipeline (HTML parsing → JSON transformation)
4. Advanced heuristic tuning (exam spacing, stress/rating integration)
5. Steepest Ascent HC implementation
6. Parallel course support & final optimizations

---

## 🔮 Future Enhancements

See [`Features_to_come.out`](Features_to_come.out) for planned features:

- **Adaptive Stress Preferences**: Gaussian-weighted semester stress targeting (1-5 scale)
- **Smart Semester Lookback**: Automatic detection of "major course changes" via statistical analysis (For ignoring outdated data)
- **Evaluation Mode**: Score user-created schedules without optimization
- **Memory Optimization**: Pointer-based course references to reduce duplication

---

## 📝 License

This project is open-source under the MIT License.

---

## 🤝 Contributing

This is a personal project, but suggestions and improvements are welcome! Feel free to:

- Open issues for bugs or feature requests
- Submit pull requests for enhancements
- Share your optimized schedules!

---

## 👤 Author

**Ali_T_AbuSaleh**

- GitHub: [@Ali_T_AbuSaleh](https://github.com/Ali_T_AbuSaleh)
- Repository: [Course-Schedule-Maker](https://github.com/Ali_T_AbuSaleh/Course-Schedule-Maker)

---

## 🙏 Acknowledgments

- **CheeseFork** for course data platform
- **Selenium** team for robust web automation tools
- **AI search algorithms** literature for SA/HC implementations

---

_Built with ❤️ to make semester planning less painful_
