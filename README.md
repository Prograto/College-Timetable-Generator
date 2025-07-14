# 🕒 College Timetable Generator

A Python-based intelligent timetable generator that allocates subjects, labs, and fixed activities (like Training, Sports, Counseling, etc.) across multiple class sections. It ensures fair distribution of periods and prevents scheduling conflicts such as teacher overlaps or subject repetition within a day.

---

## 🚀 Features

- ✅ Automatically assigns:
  - 📘 Theory subjects based on priority
  - 🔬 Labs in 3 consecutive-period blocks
  - 🎯 Fixed subjects like Training, Sports, Counseling, Library, etc.
- 🧠 Logic-based placement:
  - Labs never occur on back-to-back days
  - Library and Sports are always placed in the last periods of the day
  - Double-period subjects are scheduled together (e.g., Training)
- 👩‍🏫 Dynamically assigns teachers to subjects and sections
- 🔒 Avoids:
  - Subject repetition in the same day
  - Overlapping teacher schedules
  - Empty timetable cells

---

## 📐 Structure & Logic

- **Working days**: 6 (Monday to Saturday)
- **Periods per day**: 7
- **Total periods per week per section**: 42
- **Subjects include**:
  - Priority 1 subjects: 5 periods/week
  - Priority 2 subjects: 4 periods/week
  - Labs: 6 periods/week (3x2 days)
- **Fixed Subjects** (assigned once per week):
  ```python
  self.fixed_subjects = {
      "Training": 2,
      "Training Exam": 2,
      "Sports": 2,
      "Counseling": 1,
      "Library": 1,
      "skills": 1
  }
🛠 Technologies Used
Python 3.x

Built-in libraries: random, collections

📁 File Structure
php
Copy
Edit
timetable-generator/
├── final.py         # Main code file for timetable logic
├── README.md        # Documentation
🧪 How to Run
Make sure you have Python 3 installed.

Run the script:

bash
Copy
Edit
python final.py
Output will display the timetable for each section like:

sql
Copy
Edit
Timetable for CSE-A
Day 1:
  Period 1: DSA (Teacher0)
  Period 2: NLP (Teacher2)
  ...
📝 Sample Subject Configuration
python
Copy
Edit
subjects = [
    Subject("DSA", 1),
    Subject("NLP", 1),
    Subject("ML", 1),
    Subject("UHV", 2),
    Subject("PLC", 2),
    Subject("IGPS", 2),
    Subject("AI Lab", 1, 'lab'),
]
📌 Constraints Handled
🔁 No subject occurs more than once per day in the same section

⏳ Labs span 3 consecutive periods and are spaced out during the week

🎓 Teachers are not double-booked across sections

📚 Sports and Library are always placed at the end of the day

🧩 Fixed subjects occur once per week as per their total period count

🌟 Future Improvements
Export timetables to PDF/Excel

Web UI with drag-and-drop editing

Teacher availability/preference input

Integration with academic calendar

Conflict-resolution suggestions

📄 License
This project is licensed under the MIT License. Feel free to use and modify.

🤝 Contributing
Pull requests and suggestions are welcome! For major changes, please open an issue first.

📬 Contact
For questions or improvements, contact: [chanduarasavalli95@gmail.com]

vbnet
Copy
Edit

Let me know if you'd like to auto-generate this into a downloadable file or turn it
