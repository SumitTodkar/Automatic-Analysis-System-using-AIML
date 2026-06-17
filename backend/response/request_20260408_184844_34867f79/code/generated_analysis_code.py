
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

# Question 1: What is the total revenue generated, the total number of pizzas sold, and the total number of orders placed?
# Output: analysis_1775654573.png
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\graphs"

QUESTION = """What is the total revenue generated, the total number of pizzas sold, and the total number of orders placed?"""
base_name = "analysis_1775654573"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

# Load data
df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\data\pizza_sales.csv')

# Preprocessing
df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['quantity'] = df['quantity'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
df = df.drop_duplicates()
key_columns = ['total_price', 'quantity', 'order_id', 'pizza_category', 'pizza_size']
df = df.dropna(subset=key_columns)

# Outlier detection
Q1, Q3 = df['total_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_clean = df[df['total_price'] <= Q3 + 1.5 * IQR]

# Advanced Analysis
total_revenue = float(df['total_price'].sum())
total_pizzas_sold = int(df['quantity'].sum())
total_orders = int(df['order_id'].nunique())
avg_order_value = float(df.groupby('order_id')['total_price'].sum().mean())
spearman_corr = float(df['unit_price'].corr(df['quantity'], method='spearman'))
skewness = float(df['total_price'].skew())
kurtosis = float(df['total_price'].kurtosis())
outlier_count = int(df['total_price'].gt(Q3 + 1.5 * IQR).sum())

# Stats Dictionary
stats = {
    'question': str(QUESTION),
    'total_revenue': float(total_revenue),
    'total_pizzas_sold': int(total_pizzas_sold),
    'total_orders': int(total_orders),
    'avg_order_value': float(avg_order_value),
    'mean_unit_price': float(df['unit_price'].mean()),
    'median_unit_price': float(df['unit_price'].median()),
    'std_total_price': float(df['total_price'].std()),
    'min_total_price': float(df['total_price'].min()),
    'max_total_price': float(df['total_price'].max()),
    'outlier_count': int(outlier_count),
    'skewness': float(skewness),
    'kurtosis': float(kurtosis),
    'spearman_price_quantity': float(spearman_corr),
    'top_category_by_revenue': str(df.groupby('pizza_category')['total_price'].sum().idxmax())
}

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(f"Pizza Sales Performance Analysis\n{QUESTION}", fontsize=16)

# Subplot 1: Revenue by Category
cat_rev = df.groupby('pizza_category')['total_price'].sum().reset_index()
sns.barplot(data=cat_rev, x='pizza_category', y='total_price', hue='pizza_category', legend=False, ax=axes[0, 0])
axes[0, 0].bar_label(axes[0, 0].containers[0], fmt='%.0f')
axes[0, 0].set_title('Total Revenue by Pizza Category')
axes[0, 0].set_ylabel('Revenue ($)')

# Subplot 2: Distribution of Total Price
sns.histplot(df['total_price'], kde=True, ax=axes[0, 1], color='teal')
if skewness > 1:
    axes[0, 1].set_yscale('log')
axes[0, 1].set_title('Distribution of Total Price (Log Scale if Skewed)')

# Subplot 3: Quantity vs Unit Price (Scatter with Trend Line)
sns.scatterplot(data=df, x='unit_price', y='quantity', alpha=0.5, ax=axes[1, 0])
z = np.polyfit(df['unit_price'], df['quantity'], 1)
p = np.poly1d(z)
axes[1, 0].plot(df['unit_price'], p(df['unit_price']), "r--", lw=2)
axes[1, 0].set_title('Quantity vs Unit Price Correlation')

# Subplot 4: Quantity by Pizza Size
size_qty = df.groupby('pizza_size')['quantity'].sum().reset_index()
sns.barplot(data=size_qty, x='pizza_size', y='quantity', hue='pizza_size', legend=False, ax=axes[1, 1])
axes[1, 1].bar_label(axes[1, 1].containers[0], fmt='%.0f')
axes[1, 1].set_title('Total Quantity Sold by Pizza Size')

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


# Question 2: What is the average amount spent per order? Are there any outliers in order totals using the IQR method?
# Output: analysis_1775654829.png
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\graphs"

QUESTION = """What is the average amount spent per order? Are there any outliers in order totals using the IQR method?"""
base_name = "analysis_1775654829"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

# Load data
df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\data\pizza_sales.csv')

# Preprocessing
df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]
df = df.drop_duplicates()
df = df.dropna(subset=['order_id', 'total_price', 'quantity'])

# Aggregate by order_id
order_data = df.groupby('order_id').agg({
    'total_price': 'sum',
    'quantity': 'sum'
}).reset_index()

# Outlier detection using IQR on order totals
Q1, Q3 = order_data['total_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1
upper_bound = Q3 + 1.5 * IQR
lower_bound = Q1 - 1.5 * IQR
outlier_count = int(order_data['total_price'].gt(upper_bound).sum() + order_data['total_price'].lt(lower_bound).sum())
order_data_clean = order_data[order_data['total_price'] <= upper_bound]

# Category analysis
cat_revenue = df.groupby('cat_lvl1')['total_price'].agg(['mean', 'median', 'count', 'std']).reset_index()

# Spearman Correlation
spearman_corr = float(df['quantity'].corr(df['total_price'], method='spearman'))

# Stats dictionary
stats = {
    'question': str(QUESTION),
    'total_orders': int(len(order_data)),
    'average_order_value': float(order_data['total_price'].mean()),
    'median_order_value': float(order_data['total_price'].median()),
    'std_order_value': float(order_data['total_price'].std()),
    'min_order_value': float(order_data['total_price'].min()),
    'max_order_value': float(order_data['total_price'].max()),
    'outlier_count_iqr': int(outlier_count),
    'skewness_order_value': float(order_data['total_price'].skew()),
    'kurtosis_order_value': float(order_data['total_price'].kurtosis()),
    'top_category_by_revenue': str(df.groupby('cat_lvl1')['total_price'].sum().idxmax()),
    'quantity_price_correlation': float(spearman_corr)
}

# Visualization
fig, axes = plt.subplots(2, 2, figsize=(16, 12))
plt.suptitle('Pizza Order Analysis: Spending and Outliers', fontsize=18)

# Subplot 1: Distribution of Order Totals
sns.histplot(order_data['total_price'], kde=True, ax=axes[0, 0], color='skyblue')
axes[0, 0].set_title('Distribution of Order Totals')
axes[0, 0].set_xlabel('Order Total ($)')

# Subplot 2: Boxplot for Outlier Visualization
sns.boxplot(x=order_data['total_price'], ax=axes[0, 1], color='lightcoral')
axes[0, 1].set_title('Order Total Boxplot (Outlier Detection)')
axes[0, 1].set_xlabel('Order Total ($)')

# Subplot 3: Average Revenue by Category
sns.barplot(data=cat_revenue, x='cat_lvl1', y='mean', hue='cat_lvl1', ax=axes[1, 0], palette='viridis', legend=False)
axes[1, 0].bar_label(axes[1, 0].containers[0], fmt='%.2f')
axes[1, 0].set_title('Average Revenue per Pizza by Category')
axes[1, 0].set_xlabel('Category')
axes[1, 0].set_ylabel('Mean Price ($)')
if len(cat_revenue) > 5:
    axes[1, 0].tick_params(axis='x', rotation=45)

# Subplot 4: Quantity vs Total Price Scatter
sns.scatterplot(data=df, x='quantity', y='total_price', ax=axes[1, 1], alpha=0.5)
m, b = np.polyfit(df['quantity'], df['total_price'], 1)
axes[1, 1].plot(df['quantity'], m*df['quantity'] + b, color='red', lw=2)
axes[1, 1].set_title('Quantity vs Total Price (with Trendline)')
axes[1, 1].set_xlabel('Quantity')
axes[1, 1].set_ylabel('Total Price ($)')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
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


# Question 3: What are the top 5 and bottom 5 pizzas based on total revenue and quantity sold?
# Output: analysis_1775655247.png
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
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\graphs"

QUESTION = """What are the top 5 and bottom 5 pizzas based on total revenue and quantity sold?"""
base_name = "analysis_1775655247"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

# Load data
df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260408_184844_34867f79\data\pizza_sales.csv')

# DATA PREPROCESSING
# 1. Clean currency/rupee symbols
df['unit_price'] = df['unit_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)
df['total_price'] = df['total_price'].astype(str).str.replace('[^0-9.]', '', regex=True).astype(float)

# 2. Parse pipe-delimited categories
df['cat_lvl1'] = df['pizza_category'].str.split('|').str[0]

# 3. Remove duplicates
df = df.drop_duplicates()

# 4. Handle nulls
key_columns = ['pizza_name', 'total_price', 'quantity', 'pizza_category']
df = df.dropna(subset=key_columns)

# 5. Detect outliers using IQR for total_price
Q1, Q3 = df['total_price'].quantile([0.25, 0.75])
IQR = Q3 - Q1
df_clean = df[df['total_price'] <= Q3 + 1.5 * IQR]

# ADVANCED ANALYSIS
# Group-by aggregations
pizza_stats = df.groupby('pizza_name').agg({
    'total_price': 'sum',
    'quantity': 'sum'
}).reset_index()

# Top 5 / Bottom 5 rankings
top_5_rev = pizza_stats.nlargest(5, 'total_price')
bottom_5_rev = pizza_stats.nsmallest(5, 'total_price')
top_5_qty = pizza_stats.nlargest(5, 'quantity')
bottom_5_qty = pizza_stats.nsmallest(5, 'quantity')

# Derived metrics
df['avg_price_per_unit'] = df['total_price'] / df['quantity']
category_revenue = df.groupby('cat_lvl1')['total_price'].sum()
category_perc = (category_revenue / category_revenue.sum()) * 100

# Distribution analysis
skew_val = df['total_price'].skew()
kurt_val = df['total_price'].kurtosis()

# Spearman correlation
corr_val, _ = scipy_stats.spearmanr(df['quantity'], df['total_price'])

# CHARTING
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plt.suptitle(f"Analysis: {QUESTION}", fontsize=16, fontweight='bold')

# Subplot 1: Top 5 Pizzas by Revenue
sns.barplot(data=top_5_rev, x='total_price', y='pizza_name', hue='pizza_name', ax=axes[0, 0], palette='viridis', legend=False)
axes[0, 0].set_title('Top 5 Pizzas by Total Revenue')
axes[0, 0].set_xlabel('Total Revenue')
axes[0, 0].set_ylabel('Pizza Name')
axes[0, 0].bar_label(axes[0, 0].containers[0], fmt='%.2f', padding=3)

# Subplot 2: Bottom 5 Pizzas by Revenue
sns.barplot(data=bottom_5_rev, x='total_price', y='pizza_name', hue='pizza_name', ax=axes[0, 1], palette='magma', legend=False)
axes[0, 1].set_title('Bottom 5 Pizzas by Total Revenue')
axes[0, 1].set_xlabel('Total Revenue')
axes[0, 1].set_ylabel('Pizza Name')
axes[0, 1].bar_label(axes[0, 1].containers[0], fmt='%.2f', padding=3)

# Subplot 3: Top 5 Pizzas by Quantity
sns.barplot(data=top_5_qty, x='quantity', y='pizza_name', hue='pizza_name', ax=axes[1, 0], palette='rocket', legend=False)
axes[1, 0].set_title('Top 5 Pizzas by Quantity Sold')
axes[1, 0].set_xlabel('Quantity Sold')
axes[1, 0].set_ylabel('Pizza Name')
axes[1, 0].bar_label(axes[1, 0].containers[0], fmt='%.0f', padding=3)

# Subplot 4: Quantity vs Revenue Scatter with Trendline
axes[1, 1].scatter(df['quantity'], df['total_price'], alpha=0.5, color='teal')
z = np.polyfit(df['quantity'], df['total_price'], 1)
p = np.poly1d(z)
axes[1, 1].plot(df['quantity'], p(df['quantity']), "r--", alpha=0.8)
axes[1, 1].set_title('Quantity vs Total Price Correlation')
axes[1, 1].set_xlabel('Quantity')
axes[1, 1].set_ylabel('Total Price')
if skew_val > 1:
    axes[1, 1].set_yscale('log')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# STATS DICT
stats = {
    'question': str(QUESTION),
    'total_records': int(len(df)),
    'mean_revenue': float(df['total_price'].mean()),
    'median_revenue': float(df['total_price'].median()),
    'std_revenue': float(df['total_price'].std()),
    'min_revenue': float(df['total_price'].min()),
    'max_revenue': float(df['total_price'].max()),
    'outlier_count': int(df['total_price'].gt(Q3 + 1.5 * IQR).sum()),
    'skewness': float(skew_val),
    'kurtosis': float(kurt_val),
    'spearman_correlation': float(corr_val),
    'top_revenue_pizza': str(top_5_rev.iloc[0]['pizza_name']),
    'bottom_revenue_pizza': str(bottom_5_rev.iloc[0]['pizza_name']),
    'top_quantity_pizza': str(top_5_qty.iloc[0]['pizza_name']),
    'bottom_quantity_pizza': str(bottom_5_qty.iloc[0]['pizza_name']),
    'top_category_by_revenue': str(category_revenue.idxmax())
}

# SAVE OUTPUTS
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


