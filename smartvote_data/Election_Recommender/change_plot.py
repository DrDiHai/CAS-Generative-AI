import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from party_styles import party_styles

import ace_tools_open as tools


# Connect to SQLite database
connection = sqlite3.connect("staenderat.db")
query = """
WITH Candidate_Ranks AS (
SELECT ID_Candidate, AVG(rec.NormalizedRank)  AS AvgRank, a.Alterations
FROM ElectionRecommendationNormalized rec
LEFT JOIN ElectionRun run ON rec.ID_run = run.ID_run
LEFT JOIN CandidateAlterations a ON a.Variant_Key = CAST(run.Variant_Key AS Text) -- :(
GROUP BY ID_Candidate, a.Alterations
)
SELECT a.ID_Candidate, REPLACE(REPLACE(g.name, "männlich", "male"), "weiblich", "female") [Gender],
k.party_short [Party], REPLACE(REPLACE(g.name, "männlich", "male"), "weiblich", "female")||" - "||k.party_short [Gender_Party], a.AvgRank - b.AvgRank AvgRank_Difference, 'Candidate Gender Reversed' "Alteration"  FROM Candidate_Ranks a
INNER JOIN Candidate_Ranks b ON a.ID_Candidate = b.ID_Candidate
LEFT JOIN Kandidat k ON k.ID = a.ID_Candidate
LEFT JOIN Gender g ON g.gender = k.gender
WHERE a.Alterations = '""'
AND (b.Alterations LIKE '"reverse_gender_for_id='||b.ID_Candidate||'&%')
"""

# Load query results into pandas DataFrame
data = pd.read_sql_query(query, connection)

# Convert data to a DataFrame
df = pd.DataFrame(data)


# Dynamically group by unique values in the "Gender" column
unique_genders = df["Gender"].unique()
grouped_data = [
    df[df["Gender"] == gender]["AvgRank_Difference"] for gender in unique_genders
]

# Create the grouped boxplot
plt.figure(figsize=(6, 4))
plt.boxplot(grouped_data, vert=True, patch_artist=True, labels=unique_genders)
plt.title("Overall Change in Average Rank by Original Gender")
plt.ylabel("Change in Rank")
plt.xlabel("Original Gender")
plt.grid(axis="y")

# Set the y-axis limits from -1 to 1
plt.ylim(-1, 1)

# Display the grouped boxplot
plt.show()

# Dynamically group by unique values in the "Gender" column
unique_parties = df["Party"].unique()
grouped_data = [
    df[df["Party"] == party]["AvgRank_Difference"] for party in unique_parties
]


# Dynamically group by unique values in the "Gender" column
unique_gender_parties = sorted(df["Gender_Party"].unique())
grouped_data = [
    df[df["Gender_Party"] == Gender_Party]["AvgRank_Difference"]
    for Gender_Party in unique_gender_parties
]

# Create the boxplot with party colors
plt.figure(figsize=(12, 8))
box = plt.boxplot(
    grouped_data, vert=True, patch_artist=True, labels=unique_gender_parties
)

# Apply party colors to the boxes
for patch, label in zip(box["boxes"], unique_gender_parties):
    party = label.split(" - ")[-1]  # Extract the party name from "Gender - Party"
    color = party_styles.get(party, {"color": "#CCCCCC"})[
        "color"
    ]  # Default to gray if party not found
    patch.set_facecolor(color)

# Customize plot appearance
plt.title("Average Change to Rank by Gender and Party", fontsize=14, fontweight="bold")
plt.ylabel("Change in Average Rank")
plt.xlabel("Original Gender - Party")
plt.grid(axis="y")
plt.xticks(
    ticks=range(1, len(unique_gender_parties) + 1),
    labels=unique_gender_parties,
    rotation=45,
    ha="right",
)

# Set y-axis limits for better comparison
plt.ylim(-1, 1)

# Display the boxplot
plt.tight_layout()
plt.show()

# Calculate and display statistical summaries
gender_stats = df.groupby("Gender")["AvgRank_Difference"].describe()
party_stats = df.groupby("Party")["AvgRank_Difference"].describe()
gender_party_stats = df.groupby("Gender_Party")["AvgRank_Difference"].describe()


tools.display_dataframe_to_user(
    name="Statistical Summaries by Gender, Party, and Gender-Party",
    dataframe=gender_party_stats,
)
