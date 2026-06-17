import datetime
import json
import numpy as np
import pandas as pd
import os

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

# Question 1: "What is the total revenue generated, the total number of pizzas sold, and the total number of orders placed?
# Output: analysis_1775546042.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, datetime
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260407_124323_c30b660b\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260407_124323_c30b660b\graphs"
DATA_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260407_124323_c30b660b\data"

try:
    os.makedirs(STATS_DIR, exist_ok=True)
    os.makedirs(GRAPHS_DIR, exist_ok=True)
except Exception:
    pass

QUESTION = """"What is the total revenue generated, the total number of pizzas sold, and the total number of orders placed?"""
base_name = "analysis_1775546042"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")
csv_path = os.path.join(DATA_DIR, "pizza_sales.csv")

try:
    df = pd.read_csv(csv_path)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['quantity'] = df['quantity'].astype(float)
    df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
    df = df.drop_duplicates()
    df = df.dropna(subset=['total_price', 'quantity', 'order_id', 'pizza_category'])

    Q1, Q3 = df['total_price'].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    df_clean = df[df['total_price'] <= Q3 + 1.5 * IQR]

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.suptitle(f"Analysis: {QUESTION}", fontsize=16)

    cat_rev = df.groupby('cat_lvl1')['total_price'].sum().reset_index()
    sns.barplot(data=cat_rev, x='cat_lvl1', y='total_price', hue='cat_lvl1', legend=False, ax=axes[0, 0])
    axes[0, 0].set_title('Total Revenue by Category')
    if len(axes[0, 0].containers) > 0:
        axes[0, 0].bar_label(axes[0, 0].containers[0], fmt='%.2f')
    axes[0, 0].set_ylabel('Revenue')

    sns.histplot(df['total_price'], kde=True, ax=axes[0, 1])
    axes[0, 1].set_title('Distribution of Total Price')
    axes[0, 1].set_yscale('log')

    scatter_data = df.groupby('order_id').agg({'quantity': 'sum', 'total_price': 'sum'}).reset_index()
    axes[1, 0].scatter(scatter_data['quantity'], scatter_data['total_price'], alpha=0.5)
    if len(scatter_data) > 1:
        m, b = np.polyfit(scatter_data['quantity'], scatter_data['total_price'], 1)
        axes[1, 0].plot(scatter_data['quantity'], m * scatter_data['quantity'] + b, color='red')
    axes[1, 0].set_title('Quantity vs Total Price (per Order)')
    axes[1, 0].set_xlabel('Total Quantity')
    axes[1, 0].set_ylabel('Total Price')

    top_pizzas = df.groupby('pizza_name')['total_price'].sum().nlargest(5).reset_index()
    sns.barplot(data=top_pizzas, x='total_price', y='pizza_name', hue='pizza_name', legend=False, ax=axes[1, 1])
    axes[1, 1].set_title('Top 5 Pizzas by Revenue')
    axes[1, 1].set_xlabel('Revenue')
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    stats = {
        'question': str(QUESTION),
        'total_revenue': float(df['total_price'].sum()),
        'total_pizzas_sold': int(df['quantity'].sum()),
        'total_orders': int(df['order_id'].nunique()),
        'mean_order_value': float(df.groupby('order_id')['total_price'].sum().mean()),
        'median_order_value': float(df.groupby('order_id')['total_price'].sum().median()),
        'std_revenue': float(df['total_price'].std()),
        'min_price': float(df['total_price'].min()),
        'max_price': float(df['total_price'].max()),
        'outlier_count': int(df['total_price'].gt(Q3 + 1.5 * IQR).sum()),
        'skewness': float(df['total_price'].skew()),
        'kurtosis': float(df['total_price'].kurtosis()),
        'top_category': str(df.groupby('cat_lvl1')['total_price'].sum().idxmax()) if not df.empty else "",
        'spearman_corr_qty_price': float(df['quantity'].corr(df['total_price'], method='spearman'))
    }

    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception:
        pass
    plt.close('all')

    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass

except Exception as e:
    print(f"Error in Question 1: {e}")
    plt.close('all')

# Question 2: What is the average amount spent per order? Are there any outliers in order totals using the IQR method?
# Output: analysis_1775546274.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, datetime
import warnings
warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

QUESTION = """What is the average amount spent per order? Are there any outliers in order totals using the IQR method?"""
base_name = "analysis_1775546274"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    df = pd.read_csv(csv_path)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
    df = df.drop_duplicates()
    df = df.dropna(subset=['order_id', 'total_price', 'quantity', 'pizza_category'])

    order_data = df.groupby('order_id').agg({
        'total_price': 'sum',
        'quantity': 'sum'
    }).reset_index()

    Q1 = order_data['total_price'].quantile(0.25)
    Q3 = order_data['total_price'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    outlier_count = int(order_data['total_price'].gt(upper_bound).sum())

    stats = {
        'question': str(QUESTION),
        'total_orders': int(len(order_data)),
        'avg_spent_per_order': float(order_data['total_price'].mean()),
        'median_spent_per_order': float(order_data['total_price'].median()),
        'std_spent_per_order': float(order_data['total_price'].std()),
        'min_order_total': float(order_data['total_price'].min()),
        'max_order_total': float(order_data['total_price'].max()),
        'outlier_count_iqr': int(outlier_count),
        'skewness_order_totals': float(order_data['total_price'].skew()),
        'kurtosis_order_totals': float(order_data['total_price'].kurtosis()),
        'top_category_by_revenue': str(df.groupby('cat_lvl1')['total_price'].sum().idxmax()) if not df.empty else "",
        'quantity_price_correlation': float(df['quantity'].corr(df['total_price'], method='spearman'))
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.suptitle(QUESTION, fontsize=16, fontweight='bold')

    sns.histplot(order_data['total_price'], kde=True, ax=axes[0, 0], color='teal')
    axes[0, 0].set_title('Distribution of Order Totals')

    sns.boxplot(x=order_data['total_price'], ax=axes[0, 1], color='salmon')
    axes[0, 1].set_title('Order Total Boxplot')

    cat_stats = df.groupby('cat_lvl1')['total_price'].agg(['mean']).reset_index()
    sns.barplot(data=cat_stats, x='cat_lvl1', y='mean', hue='cat_lvl1', ax=axes[1, 0], palette='viridis', legend=False)
    axes[1, 0].set_title('Avg Spend per Item by Category')
    if len(axes[1, 0].containers) > 0:
        axes[1, 0].bar_label(axes[1, 0].containers[0], fmt='%.2f')

    sns.scatterplot(data=order_data, x='quantity', y='total_price', ax=axes[1, 1], alpha=0.5)
    if len(order_data) > 1:
        m, b = np.polyfit(order_data['quantity'], order_data['total_price'], 1)
        axes[1, 1].plot(order_data['quantity'], m * order_data['quantity'] + b, color='red', linestyle='--')
    axes[1, 1].set_title('Order Quantity vs Order Total')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception:
        pass
    plt.close('all')

    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass
except Exception as e:
    print(f"Error in Question 2: {e}")
    plt.close('all')

# Question 3: What are the top 5 and bottom 5 pizzas based on total revenue and quantity sold?
# Output: analysis_1775546329.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, datetime
import warnings
warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

QUESTION = """What are the top 5 and bottom 5 pizzas based on total revenue and quantity sold?"""
base_name = "analysis_1775546329"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    df = pd.read_csv(csv_path)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df = df.drop_duplicates().dropna(subset=['pizza_name', 'total_price', 'quantity'])

    Q1, Q3 = df['total_price'].quantile([0.25, 0.75])
    IQR = Q3 - Q1
    df_clean = df[df['total_price'] <= Q3 + 1.5 * IQR]

    pizza_stats = df_clean.groupby('pizza_name').agg({'total_price': 'sum', 'quantity': 'sum'}).reset_index()
    top_5_rev = pizza_stats.nlargest(5, 'total_price')
    bot_5_rev = pizza_stats.nsmallest(5, 'total_price')
    top_5_qty = pizza_stats.nlargest(5, 'quantity')
    bot_5_qty = pizza_stats.nsmallest(5, 'quantity')

    stats = {
        'question': str(QUESTION),
        'total_records': int(len(df_clean)),
        'mean_revenue_per_line': float(df_clean['total_price'].mean()),
        'top_revenue_pizza': str(pizza_stats.loc[pizza_stats['total_price'].idxmax(), 'pizza_name']) if not pizza_stats.empty else "",
        'bottom_revenue_pizza': str(pizza_stats.loc[pizza_stats['total_price'].idxmin(), 'pizza_name']) if not pizza_stats.empty else "",
        'spearman_correlation_qty_rev': float(pizza_stats['quantity'].corr(pizza_stats['total_price'], method='spearman'))
    }

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    plt.suptitle(QUESTION, fontsize=18, fontweight='bold')

    rev_plot_data = pd.concat([top_5_rev, bot_5_rev])
    sns.barplot(data=rev_plot_data, x='total_price', y='pizza_name', hue='pizza_name', ax=axes[0, 0], palette='viridis', legend=False)
    axes[0, 0].set_title('Top & Bottom 5 Pizzas by Revenue')

    qty_plot_data = pd.concat([top_5_qty, bot_5_qty])
    sns.barplot(data=qty_plot_data, x='quantity', y='pizza_name', hue='pizza_name', ax=axes[0, 1], palette='magma', legend=False)
    axes[0, 1].set_title('Top & Bottom 5 Pizzas by Quantity')

    axes[1, 0].scatter(pizza_stats['quantity'], pizza_stats['total_price'], alpha=0.6, color='teal')
    if len(pizza_stats) > 1:
        z = np.polyfit(pizza_stats['quantity'], pizza_stats['total_price'], 1)
        p = np.poly1d(z)
        axes[1, 0].plot(pizza_stats['quantity'], p(pizza_stats['quantity']), "r--")
    axes[1, 0].set_title('Quantity vs Revenue Correlation')

    sns.histplot(df_clean['total_price'], kde=True, ax=axes[1, 1], color='coral')
    axes[1, 1].set_title('Revenue Distribution (Cleaned)')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception:
        pass
    plt.close('all')

    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass
except Exception as e:
    print(f"Error in Question 3: {e}")
    plt.close('all')

# Question 4: Which days of the week and which hours of the day see the highest volume of orders?
# Output: analysis_1775546604.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, datetime
import warnings
warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

QUESTION = """Which days of the week and which hours of the day see the highest volume of orders? (This helps with staffing)."""
base_name = "analysis_1775546604"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    df = pd.read_csv(csv_path)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df = df.drop_duplicates().dropna(subset=['order_date', 'order_time', 'quantity'])
    
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['day_name'] = df['order_date'].dt.day_name()
    df['hour'] = pd.to_datetime(df['order_time'], format='%H:%M:%S').dt.hour

    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    daily_stats = df.groupby('day_name')['quantity'].sum().reindex(day_order).reset_index()
    hourly_stats = df.groupby('hour')['quantity'].sum().reset_index()

    stats = {
        'question': str(QUESTION),
        'peak_day': str(df.groupby('day_name')['quantity'].sum().idxmax()) if not df.empty else "",
        'peak_hour': int(df.groupby('hour')['quantity'].sum().idxmax()) if not df.empty else 0,
        'mean_quantity': float(df['quantity'].mean())
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.suptitle("Staffing Analysis: Order Volume", fontsize=16)

    sns.barplot(data=daily_stats, x='day_name', y='quantity', hue='day_name', legend=False, ax=axes[0, 0], palette='viridis')
    axes[0, 0].set_title('Volume by Day')
    axes[0, 0].tick_params(axis='x', rotation=45)

    sns.barplot(data=hourly_stats, x='hour', y='quantity', hue='hour', legend=False, ax=axes[0, 1], palette='magma')
    axes[0, 1].set_title('Volume by Hour')

    hourly_avg = df.groupby('hour')['quantity'].mean().reset_index()
    axes[1, 0].plot(hourly_avg['hour'], hourly_avg['quantity'], marker='o', color='teal')
    axes[1, 0].set_title('Avg Order Size by Hour')

    sns.boxplot(data=df, x='pizza_category', y='total_price', hue='pizza_category', legend=False, ax=axes[1, 1])
    axes[1, 1].set_title('Price by Category')
    axes[1, 1].tick_params(axis='x', rotation=45)

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception:
        pass
    plt.close('all')

    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass
except Exception as e:
    print(f"Error in Question 4: {e}")
    plt.close('all')

# Question 5: How does revenue fluctuate month-to-month?
# Output: analysis_1775546803.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, datetime
import warnings
warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

QUESTION = """How does revenue fluctuate month-to-month? Are there specific months with significant sales spikes?"""
base_name = "analysis_1775546803"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    df = pd.read_csv(csv_path)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['order_date'] = pd.to_datetime(df['order_date'])
    df['month'] = df['order_date'].dt.month
    df['month_name'] = df['order_date'].dt.month_name()
    df = df.dropna(subset=['total_price', 'order_date'])

    monthly_data = df.groupby(['month', 'month_name'])['total_price'].sum().reset_index().sort_values('month')

    stats = {
        'question': QUESTION,
        'total_revenue': float(df['total_price'].sum()),
        'top_month': str(monthly_data.loc[monthly_data['total_price'].idxmax(), 'month_name']) if not monthly_data.empty else "",
        'bottom_month': str(monthly_data.loc[monthly_data['total_price'].idxmin(), 'month_name']) if not monthly_data.empty else ""
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.suptitle("Monthly Revenue Analysis", fontsize=16)

    axes[0, 0].plot(monthly_data['month_name'], monthly_data['total_price'], marker='o', color='#2ecc71')
    axes[0, 0].set_title("Monthly Revenue Trend")
    axes[0, 0].tick_params(axis='x', rotation=45)

    sns.histplot(df['total_price'], kde=True, ax=axes[0, 1], color='#3498db')
    axes[0, 1].set_yscale('log')
    axes[0, 1].set_title("Revenue Distribution (Log)")

    cat_rev = df.groupby('pizza_category')['total_price'].sum().nlargest(5).reset_index()
    sns.barplot(data=cat_rev, x='pizza_category', y='total_price', hue='pizza_category', ax=axes[1, 0], legend=False)
    axes[1, 0].set_title("Top 5 Categories")
    axes[1, 0].tick_params(axis='x', rotation=45)

    axes[1, 1].scatter(df['quantity'], df['total_price'], alpha=0.3, color='#e74c3c')
    axes[1, 1].set_title("Qty vs Price")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception:
        pass
    plt.close('all')

    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass
except Exception as e:
    print(f"Error in Question 5: {e}")
    plt.close('all')

# Question 6: What is the distribution of the number of pizzas per order?
# Output: analysis_1775546996.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns, datetime
import warnings
warnings.filterwarnings("ignore")

plt.style.use("seaborn-v0_8-whitegrid")
sns.set_palette("husl")
plt.ioff()

QUESTION = """What is the distribution of the number of pizzas per order? Do people tend to buy more on weekends compared to weekdays"""
base_name = "analysis_1775546996"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    df = pd.read_csv(csv_path)
    df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
    df['order_date'] = pd.to_datetime(df['order_date'])
    
    order_agg = df.groupby('order_id').agg({'quantity': 'sum', 'order_date': 'first', 'total_price': 'sum'}).reset_index()
    order_agg['is_weekend'] = order_agg['order_date'].dt.dayofweek.isin([5, 6]).astype(int)
    order_agg['day_name'] = order_agg['order_date'].dt.day_name()

    stats = {
        'question': QUESTION,
        'mean_pizzas_per_order': float(order_agg['quantity'].mean()),
        'weekend_avg': float(order_agg[order_agg['is_weekend'] == 1]['quantity'].mean()) if not order_agg[order_agg['is_weekend'] == 1].empty else 0,
        'weekday_avg': float(order_agg[order_agg['is_weekend'] == 0]['quantity'].mean()) if not order_agg[order_agg['is_weekend'] == 0].empty else 0
    }

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.suptitle("Order Size Distribution", fontsize=16)

    sns.histplot(order_agg['quantity'], kde=True, ax=axes[0, 0], color='skyblue')
    axes[0, 0].set_title('Pizzas per Order')

    sns.barplot(x=['Weekday', 'Weekend'], y=[stats['weekday_avg'], stats['weekend_avg']], ax=axes[0, 1], palette='viridis')
    axes[0, 1].set_title('Avg Pizzas: Weekday vs Weekend')

    sns.boxplot(data=order_agg, x='day_name', y='quantity', ax=axes[1, 0])
    axes[1, 0].tick_params(axis='x', rotation=45)

    sns.scatterplot(data=order_agg.sample(min(500, len(order_agg))), x='quantity', y='total_price', ax=axes[1, 1])
    axes[1, 1].set_title('Qty vs Total Price')

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception:
        pass
    plt.close('all')

    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass
except Exception as e:
    print(f"Error in Question 6: {e}")
    plt.close('all')