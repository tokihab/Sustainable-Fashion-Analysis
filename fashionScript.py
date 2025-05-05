import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Define the file path
file_path = r"D:\toki\testings\python\new\fashion(p).xlsx"
df = pd.read_excel(file_path)

# Display the first few rows and info about the DataFrame
print(df.head())
print(df.info())

# Checking for missing values
print("Missing values in each column:\n", df.isnull().sum())

# Removing duplicates
df.drop_duplicates(inplace=True)

# Removing extra column
df.drop(columns=['Brand_Name'], inplace=True)

# Filling in missing values with error handling
columns_to_fill = {
    'Carbon_Footprint_MT': df['Carbon_Footprint_MT'].mean(),
    'Waste_Production_KG': df['Waste_Production_KG'].median(),
    'Water_Usage_Liters': df['Water_Usage_Liters'].median(),
    'Average_Price_USD': df['Average_Price_USD'].mean(),
    'Certifications': "Not-Certified"
}

for column, value in columns_to_fill.items():
    if column in df.columns:
        df[column].fillna(value, inplace=True)

# Generating Brand_ID
df['Brand_ID'] = df['Brand_ID'].fillna(df.apply(lambda row: f"BRAND-{str(row.name).zfill(4)}", axis=1))

# Feature engineering #1: Net waste produced
recycle_est = 0.3
df['RecPrgBIN'] = df['Recycling_Programs'].map({'Yes': 1, 'No': 0})
df['Net_WastePD'] = df['Waste_Production_KG'] * (1 - df['RecPrgBIN'] * recycle_est)

# Feature engineering #2: Price ranges
price_bins = [20, 150, 300, 500]
price_labels = ['Low', 'Medium', 'High']
df['Price_Range'] = pd.cut(df['Average_Price_USD'], bins=price_bins, labels=price_labels)

# Feature engineering #3: Water usage per product line & water usage per dollar
df['Water_Usage_PER_line'] = df['Water_Usage_Liters'] / df['Product_Lines']
df['Water_Usage_PER_dollar'] = df['Water_Usage_Liters'] / df['Average_Price_USD']

# Round all relevant numeric columns to 2 decimal places
numeric_cols = ['Carbon_Footprint_MT', 'Waste_Production_KG', 'Water_Usage_Liters',
                'Average_Price_USD', 'Net_WastePD', 'Water_Usage_PER_line', 'Water_Usage_PER_dollar']

df[numeric_cols] = df[numeric_cols].round(2)

print(df.head())
print(df.info())

# Exploratory analysis #1: Average sustainability ratings by country
sus_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4}
df['Sustain_Score'] = df['Sustainability_Rating'].map(sus_map)
average_ratings = df.groupby('Country')['Sustain_Score'].mean().reset_index()
sorted_ratings = average_ratings.sort_values(by='Sustain_Score', ascending=False)
print("Average Sustainability Ratings by Country:\n", sorted_ratings)

# Exploratory analysis #2: Common materials used by brands with high sustainability ratings
df_pro = df[df['Sustain_Score'].isin([1, 2])]
material_groups = df_pro.groupby('Material_Type')['Brand_ID'].count().reset_index(name='Brand Count')
sorted_materials = material_groups.sort_values(by='Brand Count', ascending=False)
print("Common Materials Used by High Sustainability Brands:\n", sorted_materials)

# Exploratory analysis #3: Correlation between sustainability ratings and carbon footprint reduction
correlation = df['Sustain_Score'].corr(df['Carbon_Footprint_MT'])
print(f'Correlation between Sustainability Rating and Carbon Footprint Reduction: {correlation:.2f}')

# Exploratory analysis #4: Which certifications are most common among brands with growing market trends?
trend_map = {'Growing': 1.5, 'Stable': 1, 'Declining': -0.5}
df['Trend_Map'] = df['Market_Trend'].map(trend_map) 
df_grow = df[df['Trend_Map'] == 1.5]
df_stable = df[df['Trend_Map'] == 1]
df_decline = df[df['Trend_Map'] == -0.5]
certified_stableBrands = df_stable.groupby('Certifications')['Brand_ID'].count()
certified_growingBrands = df_grow.groupby('Certifications')['Brand_ID'].count()
certified_declineBrands = df_decline.groupby('Certifications')['Brand_ID'].count()
print(certified_growingBrands)
print(certified_stableBrands)
print(certified_declineBrands)

# Exploratory analysis #5: How have sustainability metrics evolved over time across the industry?
sustainability_metrics = ['Year', 'Carbon_Footprint_MT', 'Water_Usage_Liters', 'Waste_Production_KG']
sustainability_trends = df[sustainability_metrics].groupby('Year').mean().reset_index()
print(sustainability_trends)

# plt.figure(figsize=(10, 6))
# plt.plot(sustainability_trends['Year'], sustainability_trends['Carbon_Footprint_MT'], label='Carbon Footprint (MT)', marker='o')
# plt.plot(sustainability_trends['Year'], sustainability_trends['Water_Usage_Liters'], label='Water Usage (Liters)', marker='o')
# plt.plot(sustainability_trends['Year'], sustainability_trends['Waste_Production_KG'], label='Waste Production (KG)', marker='o')

# plt.xlabel('Year')
# plt.ylabel('Sustainability Metrics')
# plt.title('Evolution of Sustainability Metrics Over Time')
# plt.legend()
# plt.grid(True)
# plt.show()

# Establishing connection with sqlite3
conn = sqlite3.connect(r"D:\toki\testings\python\new\fashion(p).db")

# Move pandas DataFrame into SQLite
df.to_sql('brands', conn, if_exists='replace', index=False)

# Query the database
cursor = conn.cursor()
cursor.execute("SELECT * FROM brands LIMIT 5;")
rows = cursor.fetchall()
#for row in rows:
#   print(row)

# Save cleaned DataFrame to Excel (using full path if needed)
df.to_excel(r"D:\toki\testings\python\new\fashion(q).xlsx", index=False)

# Close the connection
conn.close()