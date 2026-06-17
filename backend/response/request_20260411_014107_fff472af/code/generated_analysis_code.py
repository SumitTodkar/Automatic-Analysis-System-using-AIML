
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

# Question 1: Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly
# Output: analysis_1775851890.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import warnings; warnings.filterwarnings("ignore")
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_014107_fff472af\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_014107_fff472af\graphs"

# ── Always use DATA_PATH to read the CSV ──
DATA_PATH = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_014107_fff472af\data\amazon.csv"
QUESTION = """Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly"""
base_name = "analysis_1775851890"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(DATA_PATH)

df['actual_price'] = pd.to_numeric(df['actual_price'].astype(str).str.replace('₹', '').str.replace(',', ''), errors='coerce')
df['discounted_price'] = pd.to_numeric(df['discounted_price'].astype(str).str.replace('₹', '').str.replace(',', ''), errors='coerce')
df['rating_count'] = pd.to_numeric(df['rating_count'].astype(str).str.replace(',', ''), errors='coerce')
df['discount_percentage'] = pd.to_numeric(df['discount_percentage'].astype(str).str.replace('%', ''), errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

df = df.dropna(subset=['actual_price', 'discounted_price', 'rating', 'discount_percentage'])

df['parent_category'] = df['category'].astype(str).str.split('|').str.get(0)

stats = {
    'question': QUESTION,
    'total': float(df['actual_price'].sum()),
    'mean': float(df['actual_price'].mean()),
    'median': float(df['actual_price'].median()),
    'std': float(df['actual_price'].std()),
    'min': float(df['actual_price'].min()),
    'max': float(df['actual_price'].max()),
    'count': int(len(df))
}

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

corr_matrix = df[['actual_price', 'discount_percentage', 'rating']].corr()
sns.heatmap(corr_matrix, annot=True, cmap='RdBu', ax=axes[0, 0])
axes[0, 0].set_title('Price, Discount, and Rating Correlation')

top_categories = df['parent_category'].value_counts().head(5)
top_categories.plot(kind='bar', ax=axes[0, 1], color='teal')
axes[0, 1].set_title('Top 5 Parent Categories by Volume')
axes[0, 1].set_ylabel('Product Count')

sns.boxplot(x=df['actual_price'], ax=axes[1, 0], color='coral')
axes[1, 0].set_title('Actual Price Distribution (Outlier Detection)')

sns.scatterplot(data=df, x='discount_percentage', y='rating', alpha=0.4, ax=axes[1, 1], color='purple')
axes[1, 1].set_title('Discount Percentage vs. Rating')

plt.tight_layout()

plt.savefig(graph_file, bbox_inches='tight', dpi=100)
plt.close()
with open(stats_file, 'w') as f: json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
# Fallback save - ensures files always get written
if not os.path.exists(graph_file):
    plt.savefig(graph_file, bbox_inches="tight", dpi=100)
    plt.close()
if not os.path.exists(stats_file):
    if "stats" not in dir():
        stats = {"question": QUESTION, "note": "No stats generated"}
    with open(stats_file, "w") as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)


