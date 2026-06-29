from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")


def calculate_similarity(reference_answer, transcript):
    embedding1 = model.encode(reference_answer, convert_to_tensor=True)
    embedding2 = model.encode(transcript, convert_to_tensor=True)

    similarity = util.cos_sim(embedding1, embedding2)

    return float(similarity[0][0]) * 100