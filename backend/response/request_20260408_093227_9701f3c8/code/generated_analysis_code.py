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

# Question 1: Perform a full analysis of the pizza sales. Calculate total revenue, total orders, and average order value. Identify the top 5 best-selling pizzas. Show the hourly and daily trend of orders using subplots. Finally, analyze the sales distribution by pizza category and size, and check for price outliers using IQR.
# Output: analysis_1775621186.png

warnings.filterwarnings("ignore")
try:
    from scipy import stats as scipy_stats
except ImportError:
    scipy_stats = None

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

# Path Configurations
RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_093227_9701f3c8\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_093227_9701f3c8\graphs"
DATA_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_093227_9701f3c8\data"

# Ensure directories exist
for directory in [STATS_DIR, GRAPHS_DIR]:
    try:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    except Exception as e:
        print(f"Error creating directory {directory}: {e}")

QUESTION = """Perform a full analysis of the pizza sales. Calculate total revenue, total orders, and average order value. Identify the top 5 best-selling pizzas. Show the hourly and daily trend of orders using subplots. Finally, analyze the sales distribution by pizza category and size, and check for price outliers using IQR."""
base_name = "analysis_1775621186"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    # Load data
    csv_path = os.path.join(DATA_DIR, "pizza_sales.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found at {csv_path}")
    
    df = pd.read_csv(csv_path)

    # Data Preprocessing
    df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).replace('', '0').astype(float)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).replace('', '0').astype(float)
    df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
    df = df.drop_duplicates()
    key_columns = ['pizza_id', 'order_id', 'total_price', 'pizza_category', 'quantity', 'unit_price']
    df = df.dropna(subset=[col for col in key_columns if col in df.columns])

    # Outlier detection using IQR
    Q1 = df['total_price'].quantile(0.25)
    Q3 = df['total_price'].quantile(0.75)
    IQR = Q3 - Q1
    outlier_threshold = Q3 + 1.5 * IQR
    df_clean = df[df['total_price'] <= outlier_threshold]

    # Feature Engineering
    df['order_date'] = pd.to_datetime(df['order_date'], dayfirst=True, errors='coerce')
    df['day'] = df['order_date'].dt.day_name()
    df['order_time_hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S', errors='coerce').dt.hour

    # Aggregations for Charts
    df_hourly = df.groupby('order_time_hour')['order_id'].nunique().reset_index()
    df_daily = df.groupby('day')['order_id'].nunique().reset_index()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_daily['day'] = pd.Categorical(df_daily['day'], categories=day_order, ordered=True)
    df_daily = df_daily.sort_values('day')

    df_top5 = df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
    df_cat = df.groupby('cat_lvl1')['total_price'].sum().reset_index()

    # Advanced Analysis Stats
    stats = {
        'question': str(QUESTION),
        'total_records': int(len(df)),
        'total_revenue': float(df['total_price'].sum()) if not df.empty else 0.0,
        'total_orders': int(df['order_id'].nunique()) if not df.empty else 0,
        'avg_order_value': float(df.groupby('order_id')['total_price'].sum().mean()) if not df.empty else 0.0,
        'mean_unit_price': float(df['unit_price'].mean()) if not df.empty else 0.0,
        'median_unit_price': float(df['unit_price'].median()) if not df.empty else 0.0,
        'std_total_price': float(df['total_price'].std()) if not df.empty else 0.0,
        'min_total_price': float(df['total_price'].min()) if not df.empty else 0.0,
        'max_total_price': float(df['total_price'].max()) if not df.empty else 0.0,
        'outlier_count': int(df['total_price'].gt(outlier_threshold).sum()) if not df.empty else 0,
        'skewness': float(df['total_price'].skew()) if len(df) > 1 else 0.0,
        'kurtosis': float(df['total_price'].kurtosis()) if len(df) > 1 else 0.0,
        'top_category': str(df.groupby('cat_lvl1')['total_price'].sum().idxmax()) if not df.empty else "N/A",
        'spearman_corr_qty_price': float(df['quantity'].corr(df['unit_price'], method='spearman')) if len(df) > 1 else 0.0
    }

    # Visualization
    if not df.empty:
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        plt.suptitle(f"Comprehensive Pizza Sales Analysis\n{QUESTION[:100]}...", fontsize=14)

        # Subplot 1: Hourly Trend
        if not df_hourly.empty:
            sns.lineplot(data=df_hourly, x='order_time_hour', y='order_id', ax=axes[0, 0], marker='o', color='teal')
            if len(df_hourly) > 1:
                z = np.polyfit(df_hourly['order_time_hour'], df_hourly['order_id'], 1)
                p = np.poly1d(z)
                axes[0, 0].plot(df_hourly['order_time_hour'], p(df_hourly['order_time_hour']), "r--", alpha=0.8, label='Trend')
        axes[0, 0].set_title('Hourly Trend of Unique Orders')
        axes[0, 0].set_xlabel('Hour of Day')
        axes[0, 0].set_ylabel('Order Count')

        # Subplot 2: Daily Trend
        if not df_daily.empty:
            sns.barplot(data=df_daily, x='day', y='order_id', hue='day', ax=axes[0, 1], palette='viridis', legend=False)
            if axes[0, 1].containers:
                axes[0, 1].bar_label(axes[0, 1].containers[0])
        axes[0, 1].set_title('Daily Trend of Unique Orders')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].set_xlabel('Day of Week')
        axes[0, 1].set_ylabel('Order Count')

        # Subplot 3: Top 5 Pizzas by Revenue
        if not df_top5.empty:
            sns.barplot(data=df_top5, x='total_price', y='pizza_name', hue='pizza_name', ax=axes[1, 0], palette='magma', legend=False)
            if axes[1, 0].containers:
                axes[1, 0].bar_label(axes[1, 0].containers[0], fmt='%.2f')
        axes[1, 0].set_title('Top 5 Best Selling Pizzas (Revenue)')
        axes[1, 0].set_xlabel('Total Revenue')
        axes[1, 0].set_ylabel('Pizza Name')

        # Subplot 4: Revenue by Category
        if not df_cat.empty:
            sns.barplot(data=df_cat, x='cat_lvl1', y='total_price', hue='cat_lvl1', ax=axes[1, 1], palette='rocket', legend=False)
            if axes[1, 1].containers:
                axes[1, 1].bar_label(axes[1, 1].containers[0], fmt='%.2f')
        axes[1, 1].set_title('Total Revenue by Pizza Category')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].set_xlabel('Category')
        axes[1, 1].set_ylabel('Total Revenue')

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        try:
            plt.savefig(graph_file, bbox_inches='tight', dpi=150)
        except Exception as e:
            print(f"Error saving graph: {e}")
        plt.close('all')
    else:
        print("DataFrame is empty after processing.")

    # Save Stats
    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")

except Exception as e:
    print(f"An error occurred during execution: {e}")
    # Fallback for stats if main logic fails
    error_stats = {"question": QUESTION, "error": str(e)}
    try:
        with open(stats_file, "w") as f:
            json.dump(error_stats, f, cls=NumpyJSONEncoder, indent=4)
    except:
        pass

# Final check for file existence as per original structure
if not os.path.exists(graph_file):
    try:
        plt.figure(figsize=(5,5))
        plt.text(0.5, 0.5, "Graph generation failed or no data", ha='center')
        plt.savefig(graph_file, bbox_inches="tight", dpi=150)
        plt.close("all")
    except:
        pass

if not os.path.exists(stats_file):
    try:
        final_stats = {"question": QUESTION, "note": "No stats generated due to error"}
        with open(stats_file, "w") as f:
            json.dump(final_stats, f, cls=NumpyJSONEncoder, indent=4)
    except:
        pass