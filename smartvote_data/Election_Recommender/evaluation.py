import sqlite3
import pandas as pd
from scipy.stats import ttest_ind


# Connect to SQLite database
connection = sqlite3.connect("staenderat.db")

# Query to fetch relevant data
query = """
SELECT 
	 ranks.ID_candidate,
	 Kandidat.full_name,
     Kandidat.party_short,
    g."name" AS gender, 
    alt.Alterations AS alterations, 
    ranks.[RANK] AS "rank", 
     (SELECT MAX(er.Rank)
     FROM ElectionRecommendation er 
     WHERE er.ID_election = ranks.ID_election AND er.ID_run = ranks.ID_run) AS max_rank
FROM 
    ElectionRecommendation ranks
LEFT JOIN 
    ElectionRun run ON run.Full_ID_Election = ranks.ID_election AND run.ID_run = ranks.ID_run
LEFT JOIN 
    CandidateAlterations alt ON alt.Variant_Key = run.Variant_Key
LEFT JOIN 
    Kandidat ON Kandidat.ID = ranks.ID_candidate
LEFT JOIN 
    Gender g ON g.gender = Kandidat.gender
WHERE Kandidat.canton = 1;
"""
# Load query results into pandas DataFrame
data = pd.read_sql_query(query, connection)
# Add a column for normalized rank
data['normalized_rank'] = 1 - (data['rank'] / data['max_rank'])
# Create the `Gender_by_Party` column by concatenating `Gender` and `Party`
data['Gender_by_Party'] = data['party_short'] + " " + data['gender']
sorted_categories = sorted(data['Gender_by_Party'].unique())
data['Gender_by_Party'] = pd.Categorical(data['Gender_by_Party'], categories=sorted_categories, ordered=True)


# Group by gender and alterations
grouped = data.groupby(['gender', 'alterations'])

# Compute statistics using normalized rank
statistics = grouped['normalized_rank'].agg(
    Avg_Normalized_Rank='mean',
    Variance='var',
    Std_Dev='std',
    Total_Recommendations='count'
).reset_index()

print(statistics)

# Separate data for two groups
group_a = data[data['alterations'] == '{"Alteration": "A"}']['normalized_rank']
group_b = data[data['alterations'] == '{"Alteration": "B"}']['normalized_rank']

# Perform independent t-test
t_stat, p_value = ttest_ind(group_a, group_b, equal_var=False)  # Use Welch’s t-test

print(f"T-Statistic: {t_stat}, P-Value: {p_value}")


import matplotlib.pyplot as plt
import seaborn as sns

# Boxplot for rank distribution by gender and alterations
plt.figure(figsize=(10, 6))
sns.boxplot(data=data, x='full_name', y='normalized_rank', hue='alterations')
plt.title('Rank Distribution by Gender and Alterations')
plt.xlabel('Kandidat')
plt.ylabel('Rank')
plt.legend(title='Alterations')
plt.show()

# Boxplot for rank distribution by gender and alterations
# Group by Gender_by_Party and alterations to count the data points
counts = data.groupby(['Gender_by_Party', 'alterations']).size().reset_index(name='count')

plt.figure(figsize=(10, 6))
ax = sns.boxplot(data=data, x='Gender_by_Party', y='normalized_rank', hue='alterations')
plt.title('Rank Distribution by Gender and Alterations')
plt.xlabel('Party')
plt.ylabel('Rank')
# Rotate y-axis labels
plt.xticks(rotation=45)
plt.legend(title='Alterations')
# Annotate data point counts directly on the plot
for group, alteration, count in zip(counts['Gender_by_Party'], counts['alterations'], counts['count']):
    # Find the x-tick position for this Gender_by_Party and hue level
    x_pos = (
        sorted(data['Gender_by_Party'].unique()).index(group)  # X position of the group
        + list(data['alterations'].unique()).index(alteration) * 0.2  # Offset for the hue level
    )
    y_pos = ax.get_ylim()[1] - 0.1  # Place label slightly below the top of the y-axis
    ax.text(x_pos, y_pos, f"{count}", ha='center', fontsize=9, color='black')

plt.show()

# Boxplot for rank distribution by gender and alterations
plt.figure(figsize=(10, 6))
sns.boxplot(data=data, x='gender', y='normalized_rank', hue='alterations')
plt.title('Rank Distribution by Gender and Alterations')
plt.xlabel('Gender')
plt.ylabel('Rank')
plt.legend(title='Alterations')
plt.show()
