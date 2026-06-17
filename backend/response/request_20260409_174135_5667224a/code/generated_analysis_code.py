
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
# Output: analysis_1775736737.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import warnings
warnings.filterwarnings("ignore")
try:
    from scipy import stats as scipy_stats
except ImportError:
    scipy_stats = None

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_174135_5667224a\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_174135_5667224a\graphs"

QUESTION = """Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly."""
base_name = "analysis_1775736737"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

# Load data
df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_174135_5667224a\data\amazon.csv')

# 1. Clean currency and numeric columns
df['actual_price'] = df['actual_price'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['discounted_price'] = df['discounted_price'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['rating_count'] = df['rating_count'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['discount_percentage'] = df['discount_percentage'].str.replace('%', '').astype(float)

# 2. Parse categories
df['cat_lvl1'] = df['category'].str.split('|').str[0]

# 3. Remove duplicates and handle nulls
df = df.drop_duplicates()
df = df.dropna(subset=['actual_price', 'discounted_price', 'rating', 'rating_count', 'cat_lvl1'])

# 4. Detect outliers using IQR on actual_price
Q1 = df['actual_price'].quantile(0.25)
Q3 = df['actual_price'].quantile(0.75)
IQR = Q3 - Q1
df_clean = df[df['actual_price'] <= Q3 + 1.5 * IQR]

# Advanced Analysis
spearman_corr = df[['actual_price', 'discount_percentage', 'rating']].corr(method='spearman')
category_stats = df.groupby('cat_lvl1')['actual_price'].agg(['mean', 'median', 'count', 'std']).reset_index()
top_5_cats = df['cat_lvl1'].value_counts().head(5).index.tolist()
df_top_5 = df[df['cat_lvl1'].isin(top_5_cats)]

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(f"Amazon Catalog Analysis: {QUESTION}", fontsize=16)

# Subplot 1: Top 5 Categories by Volume
sns.barplot(data=df_top_5['cat_lvl1'].value_counts().reset_index(), x='cat_lvl1', y='count', hue='cat_lvl1', ax=axes[0, 0], legend=False)
axes[0, 0].set_title('Top 5 Parent Categories by Volume')
axes[0, 0].set_ylabel('Product Count')
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].bar_label(axes[0, 0].containers[0])

# Subplot 2: Price Distribution (Log Scale)
sns.histplot(df['actual_price'], kde=True, ax=axes[0, 1])
axes[0, 1].set_yscale('log')
axes[0, 1].set_title('Distribution of Actual Price (Log Scale)')
axes[0, 1].set_xlabel('Price (₹)')

# Subplot 3: Correlation Heatmap
sns.heatmap(spearman_corr, annot=True, cmap='coolwarm', fmt=".2f", ax=axes[1, 0])
axes[1, 0].set_title('Spearman Correlation Matrix')

# Subplot 4: Rating vs Discount Percentage
sns.scatterplot(data=df, x='discount_percentage', y='rating', alpha=0.5, ax=axes[1, 1])
m, b = np.polyfit(df['discount_percentage'], df['rating'], 1)
axes[1, 1].plot(df['discount_percentage'], m * df['discount_percentage'] + b, color='red', lw=2)
axes[1, 1].set_title('Rating vs Discount % with Trend Line')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(graph_file, bbox_inches='tight', dpi=150)
plt.close('all')

# Stats Dictionary
stats = {
    'question': str(QUESTION),
    'total_records': int(len(df)),
    'avg_rating': float(df['rating'].mean()),
    'median_rating': float(df['rating'].median()),
    'avg_actual_price': float(df['actual_price'].mean()),
    'avg_discount_pct': float(df['discount_percentage'].mean()),
    'max_price': float(df['actual_price'].max()),
    'min_price': float(df['actual_price'].min()),
    'outlier_count_price': int(df['actual_price'].gt(Q3 + 1.5 * IQR).sum()),
    'price_skewness': float(df['actual_price'].skew()),
    'price_kurtosis': float(df['actual_price'].kurtosis()),
    'top_category_volume': str(df['cat_lvl1'].value_counts().idxmax()),
    'price_rating_corr': float(df['actual_price'].corr(df['rating'], method='spearman')),
    'discount_rating_corr': float(df['discount_percentage'].corr(df['rating'], method='spearman'))
}

with open(stats_file, 'w') as f:
    json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
# Fallback save - ensures files always get written
if not os.path.exists(graph_file):
    plt.savefig(graph_file, bbox_inches="tight", dpi=150)
    plt.close("all")
if not os.path.exists(stats_file):
    if "stats" not in dir():
        stats = {"question": QUESTION, "note": "No stats generated"}
    with open(stats_file, "w") as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)


