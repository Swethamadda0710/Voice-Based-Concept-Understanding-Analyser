from modules.semantic_analysis import compare_answers

teacher = """
Artificial Intelligence is the simulation of human intelligence by machines.
Machine Learning is a subset of Artificial Intelligence.
"""

student = """
Artificial Intelligence enables machines to perform intelligent tasks.
Machine Learning is a branch of AI where computers learn from data.
"""

score = compare_answers(teacher, student)

print(f"Similarity Score: {score}%")