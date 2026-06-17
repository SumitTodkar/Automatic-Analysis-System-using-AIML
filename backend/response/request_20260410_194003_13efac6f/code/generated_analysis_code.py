
import json
import numpy as np
import pandas as pd

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        elif isinstance(obj, (pd.Series, pd.DataFrame)):
            return obj.to_dict()
        return super().default(obj)

# Question 1: Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly.
# Output: analysis_1775830520.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260410_194003_13efac6f\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260410_194003_13efac6f\graphs"

QUESTION = """Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly."""
base_name = "analysis_1775830520"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260410_194003_13efac6f\data\amazon.csv')

df['actual_price'] = df['actual_price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
df['discounted_price'] = df['discounted_price'].str.replace(r'[^\d.]', '', regex=True).astype(float)
df['rating_count'] = df['rating_count'].str.replace(r'[^\d.]', '', regex=True).astype(float)
df['discount_percentage'] = df['discount_percentage'].str.replace(r'[^\d.]', '', regex=True).astype(float)
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['parent_category'] = df['category'].str.split('|').str[0]
df = df.drop_duplicates()
df = df.dropna(subset=['actual_price', 'rating', 'discount_percentage'])

Q1, Q3 = df['actual_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1

stats = {
    'question': QUESTION,
    'total_records': int(len(df)),
    'mean': float(df['actual_price'].mean()),
    'median': float(df['actual_price'].median()),
    'std': float(df['actual_price'].std()),
    'min': float(df['actual_price'].min()),
    'max': float(df['actual_price'].max()),
    'outlier_count': int(df['actual_price'].gt(Q3 + 1.5 * IQR).sum()),
    'skewness': float(df['actual_price'].skew()),
    'top_category': str(df.groupby('parent_category')['actual_price'].count().idxmax())
}

with open(stats_file, 'w') as f:
    json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(QUESTION, fontsize=13, fontweight='bold')

sns.histplot(df['actual_price'], kde=True, ax=axes[0, 0])
axes[0, 0].set_xscale('log')
axes[0, 0].set_title('Distribution of Actual Price (Log Scale)')
axes[0, 0].set_xlabel('Actual Price (INR)')
axes[0, 0].set_ylabel('Frequency')

top_cats = df['parent_category'].value_counts().head(5)
sns.barplot(x=top_cats.values, y=top_cats.index, ax=axes[0, 1], hue=top_cats.index, palette='viridis', legend=False)
axes[0, 1].set_title('Top 5 Parent Categories by Volume')
axes[0, 1].set_xlabel('Product Count')
axes[0, 1].set_ylabel('Parent Category')

corr = df[['actual_price', 'discount_percentage', 'rating']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', ax=axes[1, 0])
axes[1, 0].set_title('Correlation Matrix: Price, Discount, Rating')

sns.scatterplot(data=df, x='discount_percentage', y='rating', alpha=0.4, ax=axes[1, 1])
axes[1, 1].set_title('Rating vs Discount Percentage')
axes[1, 1].set_xlabel('Discount Percentage (%)')
axes[1, 1].set_ylabel('Rating')

plt.tight_layout()
plt.savefig(graph_file, bbox_inches='tight', dpi=150)
plt.close('all')
# Fallback save - ensures files always get written
if not os.path.exists(graph_file):
    plt.savefig(graph_file, bbox_inches="tight", dpi=100)
    plt.close()
if not os.path.exists(stats_file):
    if "stats" not in dir():
        stats = {"question": QUESTION, "note": "No stats generated"}
    with open(stats_file, "w") as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)


