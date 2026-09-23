import os
import csv
from datetime import datetime


def save_result(
    student_name,
    roll_number,
    subject,
    similarity,
    final_score,
    feedback
):

    os.makedirs("data", exist_ok=True)

    csv_path = "data/results.csv"

    file_exists = os.path.isfile(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        if not file_exists:

            writer.writerow([
                "Date",
                "Student Name",
                "Roll Number",
                "Subject",
                "Similarity",
                "Final Score",
                "Feedback"
            ])

        writer.writerow([
            datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            student_name,
            roll_number,
            subject,
            similarity,
            final_score,
            feedback
        ])