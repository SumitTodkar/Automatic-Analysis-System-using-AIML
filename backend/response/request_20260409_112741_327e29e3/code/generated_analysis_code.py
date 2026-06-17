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
# Output: analysis_1775714518.png

warnings.filterwarnings("ignore")
try:
    from scipy import stats as scipy_stats
except ImportError:
    scipy_stats = None

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

# Path configurations
RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_112741_327e29e3\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_112741_327e29e3\graphs"

QUESTION = """Perform a comprehensive business analysis of the pizza sales. First, calculate key metrics including total revenue, total orders, and average order value. Second, analyze temporal trends by showing the busiest days of the week and peak hours of the day. Third, break down revenue by pizza category and size. Finally, identify the top 5 best-selling pizzas and check for any extreme order-value outliers using IQR. Use multi-panel subplots to visualize these trends clearly."""
base_name = "analysis_1775714518"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    # Load data
    data_path = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260409_112741_327e29e3\data\pizza_sales.csv"
    df = pd.read_csv(data_path)
    df = df.drop_duplicates().dropna()

    # Preprocessing
    df['order_date'] = pd.to_datetime(df['order_date'])
    # Handle time format variations
    df['order_time'] = pd.to_datetime(df['order_time'], errors='coerce').dt.hour
    df['day_of_week'] = df['order_date'].dt.day_name()
    
    # 1. Key Metrics
    total_revenue = df['total_price'].sum()
    total_orders = df['order_id'].nunique()
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    # 2. Temporal Trends
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    busiest_days = df.groupby('day_of_week')['order_id'].nunique().reindex(days_order)
    peak_hours = df.groupby('order_time')['order_id'].nunique()

    # 3. Revenue Breakdown
    rev_by_category = df.groupby('pizza_category')['total_price'].sum()
    rev_by_size = df.groupby('pizza_size')['total_price'].sum()

    # 4. Top 5 Best Sellers
    top_5_pizzas = df.groupby('pizza_name')['quantity'].sum().sort_values(ascending=False).head(5)

    # 5. Outliers using IQR
    q1 = df['total_price'].quantile(0.25)
    q3 = df['total_price'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = df[(df['total_price'] < lower_bound) | (df['total_price'] > upper_bound)]

    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    plt.suptitle("Comprehensive Pizza Sales Business Analysis", fontsize=16, fontweight="bold", y=0.95)

    # Plot 1: Busiest Days
    sns.barplot(x=busiest_days.index, y=busiest_days.values, ax=axes[0, 0], palette="viridis")
    axes[0, 0].set_title("Busiest Days of the Week (Total Orders)")
    axes[0, 0].tick_params(axis='x', rotation=45)

    # Plot 2: Peak Hours
    sns.lineplot(x=peak_hours.index, y=peak_hours.values, ax=axes[0, 1], marker='o', color='red')
    axes[0, 1].set_title("Peak Hours of the Day (Total Orders)")
    axes[0, 1].set_xticks(range(0, 24))

    # Plot 3: Revenue by Category
    axes[1, 0].pie(rev_by_category, labels=rev_by_category.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette("pastel"))
    axes[1, 0].set_title("Revenue Breakdown by Pizza Category")

    # Plot 4: Top 5 Best Selling Pizzas
    sns.barplot(x=top_5_pizzas.values, y=top_5_pizzas.index, ax=axes[1, 1], palette="magma")
    axes[1, 1].set_title("Top 5 Best-Selling Pizzas (Quantity)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    try:
        plt.savefig(graph_file, bbox_inches="tight", dpi=150)
    except Exception as e:
        print(f"Error saving graph: {e}")
    finally:
        plt.close("all")

    # Prepare stats
    stats = {
        "metrics": {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "average_order_value": avg_order_value
        },
        "temporal_analysis": {
            "busiest_day": busiest_days.idxmax(),
            "peak_hour": int(peak_hours.idxmax())
        },
        "revenue_breakdown": {
            "by_category": rev_by_category.to_dict(),
            "by_size": rev_by_size.to_dict()
        },
        "top_5_pizzas": top_5_pizzas.to_dict(),
        "outlier_analysis": {
            "iqr": iqr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
            "outlier_count": len(outliers)
        },
        "total_records_processed": len(df)
    }

    try:
        with open(stats_file, "w") as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")

except Exception as e:
    # Fallback error handling
    error_stats = {"error": str(e), "note": "Analysis failed during execution"}
    try:
        with open(stats_file, "w") as f:
            json.dump(error_stats, f, indent=4)
    except:
        pass