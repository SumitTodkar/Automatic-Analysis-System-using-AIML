import json
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

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
# Output: analysis_1775715052.png

warnings.filterwarnings("ignore")
try:
    from scipy import stats as scipy_stats
except ImportError:
    scipy_stats = None

try:
    plt.style.use("seaborn-v0_8-whitegrid")
except:
    plt.style.use("ggplot")
sns.set_palette("husl")
plt.ioff()

# Path Configurations
BASE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_113702_57ddc8d8"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_113702_57ddc8d8\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_113702_57ddc8d8\graphs"

# Ensure directories exist
try:
    os.makedirs(STATS_DIR, exist_ok=True)
    os.makedirs(GRAPHS_DIR, exist_ok=True)
except Exception as e:
    print(f"Error creating directories: {e}")

QUESTION = """Perform a comprehensive business analysis of the pizza sales. First, calculate key metrics including total revenue, total orders, and average order value. Second, analyze temporal trends by showing the busiest days of the week and peak hours of the day. Third, break down revenue by pizza category and size. Finally, identify the top 5 best-selling pizzas and check for any extreme order-value outliers using IQR. Use multi-panel subplots to visualize these trends clearly."""
base_name = "analysis_1775715052"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")
data_path = os.path.join(BASE_DIR, "data", "pizza_sales.csv")

# Load data
try:
    df = pd.read_csv(data_path)
except Exception as e:
    print(f"Error loading data: {e}")
    df = pd.DataFrame()

if not df.empty:
    # Preprocessing
    df['total_price'] = pd.to_numeric(df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce')
    df['unit_price'] = pd.to_numeric(df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True), errors='coerce')
    df['cat_lvl1'] = df['pizza_category'].astype(str).str.split('|').str[0]
    df = df.drop_duplicates()
    df = df.dropna(subset=['total_price', 'order_id', 'pizza_category', 'pizza_size'])

    # Date and Time Parsing
    df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['order_date'])
    df['order_hour'] = pd.to_datetime(df['order_time'], errors='coerce').dt.hour
    df = df.dropna(subset=['order_hour'])
    df['day_of_week'] = df['order_date'].dt.day_name()

    # Outlier Detection (IQR)
    Q1 = df['total_price'].quantile(0.25)
    Q3 = df['total_price'].quantile(0.75)
    IQR = Q3 - Q1
    df_clean = df[df['total_price'] <= (Q3 + 1.5 * IQR)]

    # Analysis Metrics
    total_revenue = float(df['total_price'].sum())
    total_orders = int(df['order_id'].nunique())
    aov = float(total_revenue / total_orders) if total_orders > 0 else 0.0
    outlier_count = int(df['total_price'].gt(Q3 + 1.5 * IQR).sum())
    spearman_corr = float(df['quantity'].corr(df['total_price'], method='spearman'))
    skewness = float(df['total_price'].skew())
    kurtosis = float(df['total_price'].kurtosis())

    # Grouped Aggregations
    cat_stats = df.groupby('pizza_category')['total_price'].agg(['mean', 'median', 'count', 'std']).reset_index()
    top_pizza = str(df.groupby('pizza_name')['total_price'].sum().idxmax()) if not df.empty else "N/A"

    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.suptitle(f"Business Analysis: Pizza Sales Trends & Metrics\n{QUESTION[:100]}...", fontsize=14)

    # Subplot 1: Revenue by Category
    cat_rev = df.groupby('pizza_category')['total_price'].sum().reset_index()
    sns.barplot(data=cat_rev, x='pizza_category', y='total_price', hue='pizza_category', legend=False, ax=axes[0, 0])
    axes[0, 0].set_title('Total Revenue by Category')
    if axes[0, 0].containers:
        axes[0, 0].bar_label(axes[0, 0].containers[0], fmt='%.0f')

    # Subplot 2: Hourly Order Distribution
    hourly_orders = df.groupby('order_hour')['order_id'].nunique().reset_index()
    axes[0, 1].plot(hourly_orders['order_hour'], hourly_orders['order_id'], marker='o', color='teal', linewidth=2)
    axes[0, 1].set_title('Peak Order Hours')
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].set_ylabel('Unique Orders')
    axes[0, 1].set_xticks(range(0, 24))

    # Subplot 3: Revenue by Pizza Size
    size_rev = df.groupby('pizza_size')['total_price'].sum().sort_values(ascending=False).reset_index()
    sns.barplot(data=size_rev, x='pizza_size', y='total_price', hue='pizza_size', legend=False, ax=axes[1, 0])
    axes[1, 0].set_title('Revenue Breakdown by Size')
    if axes[1, 0].containers:
        axes[1, 0].bar_label(axes[1, 0].containers[0], fmt='%.0f')

    # Subplot 4: Top 5 Pizzas by Revenue
    top_5 = df.groupby('pizza_name')['total_price'].sum().sort_values(ascending=False).head(5).reset_index()
    sns.barplot(data=top_5, x='total_price', y='pizza_name', hue='pizza_name', legend=False, ax=axes[1, 1])
    axes[1, 1].set_title('Top 5 Best Selling Pizzas')
    if axes[1, 1].containers:
        axes[1, 1].bar_label(axes[1, 1].containers[0], fmt='%.0f')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception as e:
        print(f"Error saving graph: {e}")
    plt.close('all')

    # Stats Dictionary
    stats = {
        'question': str(QUESTION),
        'total_revenue': float(total_revenue),
        'total_orders': int(total_orders),
        'average_order_value': float(aov),
        'outlier_count': int(outlier_count),
        'spearman_correlation_qty_price': float(spearman_corr) if not np.isnan(spearman_corr) else 0.0,
        'price_skewness': float(skewness) if not np.isnan(skewness) else 0.0,
        'price_kurtosis': float(kurtosis) if not np.isnan(kurtosis) else 0.0,
        'top_selling_pizza': str(top_pizza),
        'busiest_hour': int(hourly_orders.loc[hourly_orders['order_id'].idxmax(), 'order_hour']) if not hourly_orders.empty else 0,
        'max_category_revenue': float(cat_rev['total_price'].max()) if not cat_rev.empty else 0.0,
        'min_category_revenue': float(cat_rev['total_price'].min()) if not cat_rev.empty else 0.0,
        'busiest_day': str(df['day_of_week'].mode()[0]) if not df.empty else "N/A"
    }
else:
    stats = {"question": QUESTION, "note": "No data available for analysis"}

# Save Stats
try:
    with open(stats_file, 'w') as f:
        json