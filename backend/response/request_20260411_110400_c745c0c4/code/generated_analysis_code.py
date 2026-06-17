
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
# Output: analysis_1775885665.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import warnings; warnings.filterwarnings("ignore")
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_110400_c745c0c4\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_110400_c745c0c4\graphs"

# ── Always use DATA_PATH to read the CSV ──
DATA_PATH = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_110400_c745c0c4\data\amazon.csv"
QUESTION = """Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly"""
base_name = "analysis_1775885665"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(DATA_PATH)

df['actual_price'] = pd.to_numeric(df['actual_price'].astype(str).str.replace('₹', '').str.replace(',', ''), errors='coerce')
df['discounted_price'] = pd.to_numeric(df['discounted_price'].astype(str).str.replace('₹', '').str.replace(',', ''), errors='coerce')
df['rating_count'] = pd.to_numeric(df['rating_count'].astype(str).str.replace(',', ''), errors='coerce')
df['discount_percentage'] = pd.to_numeric(df['discount_percentage'].astype(str).str.replace('%', ''), errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

df = df.dropna(subset=['actual_price', 'discounted_price', 'rating', 'discount_percentage'])

df['Parent Category'] = df['category'].astype(str).str.split('|').str[0]

q1 = float(df['actual_price'].quantile(0.25))
q3 = float(df['actual_price'].quantile(0.75))
iqr = q3 - q1
upper_bound = q3 + 1.5 * iqr

top_5_cats = df['Parent Category'].value_counts().head(5)
corr_matrix = df[['actual_price', 'discount_percentage', 'rating']].corr()

fig, axes = plt.subplots(1, 3, figsize=(20, 6))

sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", ax=axes[0])
axes[0].set_title('Price, Discount & Rating Correlation')

top_5_cats.plot(kind='bar', ax=axes[1], color='skyblue')
axes[1].set_title('Top 5 Parent Categories by Volume')
axes[1].set_ylabel('Product Count')

sns.boxplot(x=df['actual_price'], ax=axes[2], color='lightcoral')
axes[2].set_title('Actual Price Distribution & Outliers')
axes[2].set_xlabel('Actual Price (₹)')

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


