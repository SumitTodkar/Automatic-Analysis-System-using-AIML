
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

# Question 1: Analyze the overall financial performance of the pizza business. Calculate the total revenue, total number of orders, and the average order value (AOV). Show the distribution of order totals and detect any extreme price outliers using the IQR method.
# Output: analysis_1775679680.png
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_014354_54fdd877\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_014354_54fdd877\graphs"

QUESTION = """Analyze the overall financial performance of the pizza business. Calculate the total revenue, total number of orders, and the average order value (AOV). Show the distribution of order totals and detect any extreme price outliers using the IQR method."""
base_name = "analysis_1775679680"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

# Load data
df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_014354_54fdd877\data\pizza_sales.csv')

# Data Preprocessing
df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
df = df.drop_duplicates()
df = df.dropna(subset=['order_id', 'total_price', 'pizza_category', 'quantity'])
df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce')
df.dropna(subset=['order_date'], inplace=True)

# Outlier detection using IQR on total_price
Q1, Q3 = df['total_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_clean = df[df['total_price'] <= Q3 + 1.5 * IQR]

# Advanced Analysis
order_totals = df.groupby('order_id')['total_price'].sum()
total_revenue = float(df['total_price'].sum())
total_orders = int(df['order_id'].nunique())
aov = float(order_totals.mean())
skewness = float(df['total_price'].skew())
kurtosis = float(df['total_price'].kurtosis())
spearman_corr = float(df['unit_price'].corr(df['quantity'], method='spearman'))
top_cat = str(df.groupby('cat_lvl1')['total_price'].sum().idxmax())

# Stats Dictionary
stats = {
    'question': QUESTION,
    'total_records': int(len(df)),
    'total_revenue': float(total_revenue),
    'total_orders': int(total_orders),
    'average_order_value': float(aov),
    'mean_price': float(df['total_price'].mean()),
    'median_price': float(df['total_price'].median()),
    'std_price': float(df['total_price'].std()),
    'min_price': float(df['total_price'].min()),
    'max_price': float(df['total_price'].max()),
    'outlier_count': int(df['total_price'].gt(Q3 + 1.5 * IQR).sum()),
    'skewness': float(skewness),
    'kurtosis': float(kurtosis),
    'top_category': str(top_cat),
    'correlation_unit_price_qty': float(spearman_corr)
}

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(f"Financial Performance Analysis: {QUESTION}", fontsize=16)

# Subplot 1: Distribution of Total Price
sns.histplot(df_clean['total_price'], kde=True, ax=axes[0, 0], color='skyblue')
axes[0, 0].set_title('Distribution of Total Price (Cleaned)')
axes[0, 0].set_xlabel('Total Price')

# Subplot 2: Revenue by Category
cat_rev = df.groupby('cat_lvl1')['total_price'].sum().reset_index()
sns.barplot(data=cat_rev, x='cat_lvl1', y='total_price', hue='cat_lvl1', ax=axes[0, 1], palette='viridis', legend=False)
axes[0, 1].bar_label(axes[0, 1].containers[0], fmt='%.0f')
axes[0, 1].set_title('Total Revenue by Category')
axes[0, 1].set_xlabel('Category')
axes[0, 1].set_ylabel('Revenue')

# Subplot 3: Unit Price vs Total Price (Scatter with Trend Line)
sns.scatterplot(data=df.sample(min(1000, len(df))), x='unit_price', y='total_price', ax=axes[1, 0], alpha=0.5)
z = np.polyfit(df['unit_price'], df['total_price'], 1)
p = np.poly1d(z)
axes[1, 0].plot(df['unit_price'], p(df['unit_price']), "r--", lw=2)
axes[1, 0].set_title('Unit Price vs Total Price (Sampled)')
axes[1, 0].set_xlabel('Unit Price')
axes[1, 0].set_ylabel('Total Price')

# Subplot 4: Order Volume by Pizza Size
size_vol = df['pizza_size'].value_counts().reset_index()
sns.barplot(data=size_vol, x='pizza_size', y='count', hue='pizza_size', ax=axes[1, 1], palette='magma', legend=False)
axes[1, 1].bar_label(axes[1, 1].containers[0])
axes[1, 1].set_title('Order Volume by Pizza Size')
axes[1, 1].set_xlabel('Pizza Size')
axes[1, 1].set_ylabel('Count')

# Formatting
for ax in axes.flat:
    if len(ax.get_xticklabels()) > 5:
        ax.tick_params(axis='x', rotation=45)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Save outputs
plt.savefig(graph_file, bbox_inches='tight', dpi=150)
plt.close('all')

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


