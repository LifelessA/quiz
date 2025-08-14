# 📚 Airport Test Prep - Streamlit App

An interactive quiz platform built using **Streamlit** to help users prepare for airport-related tests. This app allows uploading custom test files, taking timed or untimed quizzes, reviewing answers, and analyzing performance.

Live Demo: [🚀 Launch App](https://nytcrtzddaewsczwptzjbn.streamlit.app/)

Repository: [GitHub - LifelessA/quiz](https://github.com/LifelessA/quiz/blob/main/test.py)

---

## ✨ Features

* **Default Test Included**: Preloaded with *Paper 10 (Default)* from `questions.csv`.
* **Custom Test Uploads**: Upload your own CSV files with bilingual questions.
* **Dark & Light Mode**: Toggle theme from the sidebar.
* **Timer Mode**: Set custom durations for quizzes.
* **Randomized Questions**: Questions are shuffled for each attempt.
* **Answer Mapping**: Accepts answers in A/B/C/D format or full text.
* **Performance Analysis**: Bar charts and detailed review after test submission.
* **Mobile-Friendly UI**: Optimized for both desktop and mobile.

---

## 📂 Project Structure

```bash
├── test.py           # Main Streamlit app file
├── questions.csv     # Default quiz data
└── uploaded_tests/   # Folder where uploaded CSV test files are stored
```

---

## 📥 Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/LifelessA/quiz.git
cd quiz
```

### 2️⃣ Install Dependencies

Make sure you have Python 3.8+ installed, then run:

```bash
pip install streamlit pandas
```

### 3️⃣ Run the App Locally

```bash
streamlit run test.py
```

The app will start locally at `http://localhost:8501/`.

---

## 📄 CSV File Format

Your uploaded CSV file must follow this structure:

| Question (English) | Question (Hindi) | Option A (English) | Option A (Hindi) | Option B (English) | Option B (Hindi) | Option C (English) | Option C (Hindi) | Option D (English) | Option D (Hindi) | Correct Answer (English) |
| ------------------ | ---------------- | ------------------ | ---------------- | ------------------ | ---------------- | ------------------ | ---------------- | ------------------ | ---------------- | ------------------------ |
| Sample Q?          | सैंपल प्रश्न?    | Option 1           | विकल्प 1         | Option 2           | विकल्प 2         | Option 3           | विकल्प 3         | Option 4           | विकल्प 4         | A                        |

**Notes:**

* `Correct Answer (English)` can be `A`, `B`, `C`, `D` or the full answer text.
* Both English and Hindi text are optional for options, but English is required for correctness mapping.

---

## 🚀 Usage Instructions

1. **Choose a Test** from the Home Screen.
2. **Upload New Tests** via the sidebar.
3. **Configure Quiz Settings** — set the timer and number of questions.
4. **Answer Questions** — navigate using `Previous` and `Next`.
5. **Submit Test** — results are displayed instantly with detailed feedback.

---

## 🎨 Themes & UI

* Toggle between **Light Mode** ☀️ and **Dark Mode** 🌙 from the sidebar.
* Mobile responsive layout with optimized button sizes.

---

## 📊 Results & Analysis

* Total questions, correct answers, and percentage score.
* Visual bar chart of performance.
* Detailed per-question review with correct/incorrect feedback.

---

## 💡 Future Enhancements

* User authentication & progress tracking.
* Support for image-based questions.
* Export results to PDF/Excel.

---

---

**Developed with ❤️ using ****[Streamlit](https://streamlit.io/)**** and ****[Pandas](https://pandas.pydata.org/)****.**
