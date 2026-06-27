from sentence_transformers import SentenceTransformer, util

# Load the model once
model = SentenceTransformer("all-MiniLM-L6-v2")


def compare_answers(expected_answer, student_answer):
    """
    Compare teacher answer with student's answer.
    Returns similarity percentage.
    """

    embedding1 = model.encode(expected_answer, convert_to_tensor=True)
    embedding2 = model.encode(student_answer, convert_to_tensor=True)

    similarity = util.cos_sim(embedding1, embedding2)

    score = float(similarity[0][0]) * 100

    return round(score, 2)