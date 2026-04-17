# Vector Match 🚀

**Vector Match** is an AI-driven research ecosystem designed to bridge the gap between students and faculty mentors. By leveraging Natural Language Processing (NLP) and Optical Character Recognition (OCR), the platform automates the process of matching student expertise with faculty research domains.

## 🌟 Key Features

* **AI-Powered Matching:** Uses **TF-IDF Vectorization** and **Cosine Similarity** to calculate a "Match Score" between student resumes and faculty research interests.
* **Resume Parsing (OCR):** Integrated **Tesseract OCR** to extract technical skills and data from non-searchable PDF resumes.
* **Dual-Role Portals:** * **Students:** Upload resumes, track application status, and view suggested mentors.
    * **Professors:** Manage research domains, view matched student profiles, and review parsed resumes.
* **Persistent Storage:** Built with a **SQLite** database for secure role-based authentication and real-time data persistence.
* **Interactive UI:** Developed using **Streamlit** for a clean, professional, and data-driven user experience.

## 🛠️ Tech Stack

* **Language:** Python
* **Frontend:** Streamlit
* **Database:** SQLite
* **AI/NLP:** Scikit-learn (TF-IDF), Tesseract OCR, PyMuPDF
* **Version Control:** Git

## 📂 Project Structure

```text
├── app.py              # Main Streamlit application
├── database.py         # SQLite database configurations
├── utils.py            # OCR and NLP matching logic
├── requirements.txt    # List of dependencies
├── data/               # SQLite database file
└── README.md           # Project documentation
