from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os


def generate_pdf(
    transcript,
    similarity,
    features,
    final_score,
    feedback,
    output_path="reports/Concept_Report.pdf"
):

    # Create reports folder if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    c = canvas.Canvas(output_path, pagesize=letter)

    width, height = letter
    y = height - 50

    # -----------------------------
    # Title
    # -----------------------------
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, y, "Voice Based Concept Understanding Analyser")

    y -= 40

    # -----------------------------
    # Transcript
    # -----------------------------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Transcript")

    y -= 20

    c.setFont("Helvetica", 11)

    words = transcript.split()
    line = ""

    for word in words:
        if len(line + word) < 90:
            line += word + " "
        else:
            c.drawString(50, y, line)
            y -= 18
            line = word + " "

    c.drawString(50, y, line)

    y -= 40

    # -----------------------------
    # Evaluation
    # -----------------------------
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Evaluation")

    y -= 25

    c.setFont("Helvetica", 12)

    c.drawString(50, y, f"Semantic Similarity : {similarity:.2f}%")
    y -= 20

    c.drawString(50, y, f"Duration : {features['duration']} sec")
    y -= 20

    c.drawString(50, y, f"Speech Rate : {features['speech_rate']} WPM")
    y -= 20

    c.drawString(50, y, f"Energy : {features['energy']}")
    y -= 20

    c.drawString(50, y, f"Final Score : {final_score:.2f}")
    y -= 20

    c.drawString(50, y, f"Feedback : {feedback}")

    c.save()

    return output_path