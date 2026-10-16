"""Generate a new synthetic academic_records.csv. This overwrites the current dataset."""
from pathlib import Path
import random
import pandas as pd

random.seed(481203)
OUTPUT = Path(__file__).with_name("academic_records.csv")
COUNT = 120
first_names = ["Aditi", "Ananya", "Arjun", "Dev", "Esha", "Ira", "Kabir", "Karan", "Meera", "Naman",
               "Nisha", "Parth", "Reva", "Rohan", "Sahil", "Tanvi", "Ved", "Yamini", "Zara", "Aman"]
last_names = ["Bhat", "Chauhan", "Dave", "Gohil", "Kapoor", "Lal", "Mistry", "Nair", "Pandya", "Rana",
              "Raval", "Soni", "Thakkar", "Upadhyay"]
programs = ["BCA", "B.Sc. IT", "B.Tech CSE", "B.Com. IT", "B.Voc. IT"]
rows = []
for rid in range(2001, 2001 + COUNT):
    quiz = round(random.uniform(2, 10), 1)
    assignment = round(random.uniform(8, 30), 1)
    exam = round(random.uniform(15, 60), 1)
    total = round(quiz + assignment + exam, 1)
    grade = "A" if total >= 85 else "B" if total >= 70 else "C" if total >= 55 else "D" if total >= 40 else "F"
    rows.append({
        "record_id": rid,
        "student_name": f"{random.choice(first_names)} {random.choice(last_names)}",
        "program": random.choice(programs),
        "semester": random.choice([1, 2, 3, 4, 5, 6]),
        "attendance_pct": round(random.uniform(48, 100), 1),
        "quiz_score": quiz, "assignment_score": assignment, "exam_score": exam,
        "total_score": total, "status": "Pass" if total >= 40 else "Fail", "grade": grade
    })
pd.DataFrame(rows).to_csv(OUTPUT, index=False)
print(f"Created {COUNT} records at {OUTPUT}")
