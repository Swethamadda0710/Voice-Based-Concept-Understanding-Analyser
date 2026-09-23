from modules.scoring import calculate_score

semantic_score = 84.01
speech_rate = 121.95
energy = 0.0666

score, feedback = calculate_score(
    semantic_score,
    speech_rate,
    energy
)

print("Final Score:", score)
print("Feedback:", feedback)