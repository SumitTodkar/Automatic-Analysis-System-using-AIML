
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

# Question 1: Perform a comprehensive business analysis of the pizza sales. First, calculate key metrics including total revenue, total orders, and average order value. Second, analyze temporal trends by showing the busiest days of the week and peak hours of the day. Third, break down revenue by pizza category and size. Finally, identify the top 5 best-selling pizzas and check for any extreme order-value outliers using IQR. Use multi-panel subplots to visualize these trends clearly.
# Output: analysis_1775716615.png
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_120438_706d3318\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_120438_706d3318\graphs"

QUESTION = """Perform a comprehensive business analysis of the pizza sales. First, calculate key metrics including total revenue, total orders, and average order value. Second, analyze temporal trends by showing the busiest days of the week and peak hours of the day. Third, break down revenue by pizza category and size. Finally, identify the top 5 best-selling pizzas and check for any extreme order-value outliers using IQR. Use multi-panel subplots to visualize these trends clearly."""
base_name = "analysis_1775716615"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_120438_706d3318\data\pizza_sales.csv')

df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
df = df.drop_duplicates()
df = df.dropna(subset=['total_price', 'order_id', 'pizza_category', 'pizza_size'])

df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce')
df = df.dropna(subset=['order_date'])
df['order_hour'] = pd.to_datetime(df['order_time'], errors='coerce').dt.hour
df['day_of_week'] = df['order_date'].dt.day_name()

Q1, Q3 = df['total_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_clean = df[df['total_price'] <= Q3 + 1.5 * IQR]

order_totals = df.groupby('order_id')['total_price'].sum()
total_revenue = df['total_price'].sum()
total_orders = df['order_id'].nunique()
aov = total_revenue / total_orders

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(f"Business Analysis: {QUESTION}", fontsize=16, fontweight='bold')

cat_revenue = df.groupby('pizza_category')['total_price'].sum().reset_index().sort_values('total_price', ascending=False)
sns.barplot(data=cat_revenue, x='pizza_category', y='total_price', hue='pizza_category', ax=axes[0, 0], palette='viridis', legend=False)
axes[0, 0].set_title('Revenue by Pizza Category')
axes[0, 0].bar_label(axes[0, 0].containers[0], fmt='%.0f')

hourly_sales = df.groupby('order_hour')['total_price'].sum().reset_index()
axes[0, 1].plot(hourly_sales['order_hour'], hourly_sales['total_price'], marker='o', linestyle='-', color='tab:red')
axes[0, 1].set_title('Peak Sales Hours')
axes[0, 1].set_xlabel('Hour of Day')
axes[0, 1].set_ylabel('Total Revenue')

size_revenue = df.groupby('pizza_size')['total_price'].sum().reset_index().sort_values('total_price', ascending=False)
sns.barplot(data=size_revenue, x='pizza_size', y='total_price', hue='pizza_size', ax=axes[1, 0], palette='magma', legend=False)
axes[1, 0].set_title('Revenue by Pizza Size')
axes[1, 0].bar_label(axes[1, 0].containers[0], fmt='%.0f')

top_5_pizzas = df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
sns.barplot(data=top_5_pizzas, x='total_price', y='pizza_name', hue='pizza_name', ax=axes[1, 1], palette='rocket', legend=False)
axes[1, 1].set_title('Top 5 Best-Selling Pizzas')
axes[1, 1].bar_label(axes[1, 1].containers[0], fmt='%.0f')

for ax in axes.flat:
    if len(ax.get_xticklabels()) > 5:
        ax.tick_params(axis='x', rotation=45)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

stats = {
    'question': str(QUESTION),
    'total_revenue': float(df['total_price'].sum()),
    'total_orders': int(df['order_id'].nunique()),
    'average_order_value': float(df.groupby('order_id')['total_price'].sum().mean()),
    'median_order_value': float(df.groupby('order_id')['total_price'].sum().median()),
    'std_dev_price': float(df['total_price'].std()),
    'max_item_price': float(df['total_price'].max()),
    'min_item_price': float(df['total_price'].min()),
    'outlier_count_iqr': int(df['total_price'].gt(Q3 + 1.5 * IQR).sum()),
    'skewness_revenue': float(df['total_price'].skew()),
    'kurtosis_revenue': float(df['total_price'].kurtosis()),
    'top_category': str(df.groupby('pizza_category')['total_price'].sum().idxmax()),
    'busiest_day': str(df.groupby('day_of_week')['order_id'].nunique().idxmax()),
    'peak_hour': int(df.groupby('order_hour')['order_id'].nunique().idxmax()),
    'spearman_corr_qty_price': float(df['quantity'].corr(df['unit_price'], method='spearman'))
}

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


