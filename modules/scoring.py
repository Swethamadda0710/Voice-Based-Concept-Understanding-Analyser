def calculate_score(semantic_score, speech_rate, energy):
    """
    Calculate overall understanding score.
    """

    # Semantic similarity (80%)
    semantic_weight = semantic_score * 0.8

    # Speech rate score (10%)
    if 100 <= speech_rate <= 160:
        speech_score = 10
    elif 80 <= speech_rate < 100 or 160 < speech_rate <= 180:
        speech_score = 7
    else:
        speech_score = 4

    # Energy score (10%)
    if energy >= 0.05:
        energy_score = 10
    elif energy >= 0.02:
        energy_score = 7
    else:
        energy_score = 4

    final_score = semantic_weight + speech_score + energy_score

    if final_score >= 85:
        feedback = "Strong Understanding"
    elif final_score >= 65:
        feedback = "Moderate Understanding"
    else:
        feedback = "Needs Improvement"

    return round(final_score, 2), feedback