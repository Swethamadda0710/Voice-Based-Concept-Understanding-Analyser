import pandas as pd


def get_dashboard_data(csv_path="data/results.csv"):

    df = pd.read_csv(csv_path)

    total = len(df)

    average = round(df["Final Score"].mean(), 2)

    highest = round(df["Final Score"].max(), 2)

    strong = len(df[df["Feedback"] == "Strong Understanding"])

    moderate = len(df[df["Feedback"] == "Moderate Understanding"])

    weak = len(df[df["Feedback"] == "Needs Improvement"])

    return {
        "total": total,
        "average": average,
        "highest": highest,
        "strong": strong,
        "moderate": moderate,
        "weak": weak,
        "df": df
    }