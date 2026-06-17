
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

# Question 1: Analyze the pricing strategy of the Amazon products. First, convert the discounted price and actual price into numbers. Calculate the average actual price and the average discounted price. What is the average discount percentage offered? Create a scatter plot comparing the actual price versus the discounted price to see if more expensive items get larger discounts.
# Output: analysis_1775718521.png
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_123343_6ad411be\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_123343_6ad411be\graphs"

QUESTION = """Analyze the pricing strategy of the Amazon products. First, convert the discounted price and actual price into numbers. Calculate the average actual price and the average discounted price. What is the average discount percentage offered? Create a scatter plot comparing the actual price versus the discounted price to see if more expensive items get larger discounts."""
base_name = "analysis_1775718521"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

# Load data
df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_123343_6ad411be\data\amazon.csv')

# Data Preprocessing
df['discounted_price'] = df['discounted_price'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['actual_price'] = df['actual_price'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['discount_percentage'] = df['discount_percentage'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['rating_count'] = df['rating_count'].str.replace('[^0-9.]', '', regex=True).astype(float)
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['cat_lvl1'] = df['category'].str.split('|').str[0]

# Remove duplicates and handle nulls
df = df.drop_duplicates()
key_columns = ['actual_price', 'discounted_price', 'discount_percentage', 'cat_lvl1']
df = df.dropna(subset=key_columns)

# Outlier detection using IQR for actual_price
Q1, Q3 = df['actual_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_clean = df[df['actual_price'] <= Q3 + 1.5 * IQR]

# Derived metrics
df['discount_amount'] = df['actual_price'] - df['discounted_price']
df['log_actual_price'] = np.log1p(df['actual_price'])

# Advanced Analysis
spearman_corr = df['actual_price'].corr(df['discounted_price'], method='spearman')
skewness = df['actual_price'].skew()
kurtosis = df['actual_price'].kurtosis()
outlier_count = int(df['actual_price'].gt(Q3 + 1.5 * IQR).sum())

# Category aggregation
cat_stats = df.groupby('cat_lvl1')['discount_percentage'].mean().reset_index().sort_values('discount_percentage', ascending=False)

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(QUESTION, fontsize=14)

# Subplot 1: Actual vs Discounted Price (Scatter with Trend Line)
axes[0, 0].scatter(df_clean['actual_price'], df_clean['discounted_price'], alpha=0.5, color='royalblue')
z = np.polyfit(df_clean['actual_price'], df_clean['discounted_price'], 1)
p = np.poly1d(z)
axes[0, 0].plot(df_clean['actual_price'], p(df_clean['actual_price']), "r--", lw=2)
axes[0, 0].set_title('Actual vs Discounted Price (Cleaned Data)')
axes[0, 0].set_xlabel('Actual Price')
axes[0, 0].set_ylabel('Discounted Price')

# Subplot 2: Avg Discount % by Category
sns.barplot(data=cat_stats, x='cat_lvl1', y='discount_percentage', hue='cat_lvl1', legend=False, ax=axes[0, 1])
axes[0, 1].set_title('Average Discount % by Category')
axes[0, 1].set_xlabel('Category')
axes[0, 1].set_ylabel('Avg Discount %')
axes[0, 1].tick_params(axis='x', rotation=45)
for container in axes[0, 1].containers:
    axes[0, 1].bar_label(container, fmt='%.1f%%')

# Subplot 3: Distribution of Discount Percentage
sns.histplot(df['discount_percentage'], kde=True, ax=axes[1, 0], color='teal')
axes[1, 0].set_title('Distribution of Discount Percentage')
axes[1, 0].set_xlabel('Discount %')

# Subplot 4: Actual Price by Category (Log Scale)
sns.boxplot(data=df, x='cat_lvl1', y='actual_price', hue='cat_lvl1', legend=False, ax=axes[1, 1])
axes[1, 1].set_yscale('log')
axes[1, 1].set_title('Actual Price Distribution by Category (Log Scale)')
axes[1, 1].set_xlabel('Category')
axes[1, 1].set_ylabel('Actual Price (Log)')
axes[1, 1].tick_params(axis='x', rotation=45)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig(graph_file, bbox_inches='tight', dpi=150)
plt.close('all')

# Stats Dictionary
stats = {
    'question': QUESTION,
    'total_records': int(len(df)),
    'mean_actual_price': float(df['actual_price'].mean()),
    'mean_discounted_price': float(df['discounted_price'].mean()),
    'avg_discount_percentage': float(df['discount_percentage'].mean()),
    'std_actual_price': float(df['actual_price'].std()),
    'min_actual_price': float(df['actual_price'].min()),
    'max_actual_price': float(df['actual_price'].max()),
    'outlier_count': int(outlier_count),
    'skewness_actual_price': float(skewness),
    'kurtosis_actual_price': float(kurtosis),
    'top_discount_category': str(cat_stats.iloc[0]['cat_lvl1']),
    'price_spearman_correlation': float(spearman_corr)
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


