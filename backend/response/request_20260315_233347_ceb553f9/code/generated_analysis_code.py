
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

# Question 1: What is the average discount percentage by category?
# Output: analysis_1773598100.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\graphs"

QUESTION = """What is the average discount percentage by category?"""
base_name = "analysis_1773598100"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\data\amazon.csv')
df['discount_percentage'] = pd.to_numeric(df['discount_percentage'].str.replace('%', ''), errors='coerce')
df = df.dropna(subset=['discount_percentage', 'category'])
df['main_category'] = df['category'].str.split('|').str[0]

stats = {
    'question': QUESTION,
    'total': float(df['discount_percentage'].sum()),
    'mean': float(df['discount_percentage'].mean()),
    'median': float(df['discount_percentage'].median()),
    'std': float(df['discount_percentage'].std()),
    'min': float(df['discount_percentage'].min()),
    'max': float(df['discount_percentage'].max()),
    'count': int(len(df))
}

grouped = df.groupby('main_category')['discount_percentage'].mean().sort_values(ascending=False).reset_index()

plt.figure(figsize=(12, 8))
sns.barplot(data=grouped, x='discount_percentage', y='main_category', palette='viridis')
plt.title(QUESTION)
plt.xlabel('Average Discount Percentage (%)')
plt.ylabel('Category')

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


# Question 2: Which category has the highest rated products?
# Output: analysis_1773598124.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\graphs"

QUESTION = """Which category has the highest rated products?"""
base_name = "analysis_1773598124"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\data\amazon.csv')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df = df.dropna(subset=['rating', 'category'])
df['main_category'] = df['category'].str.split('|').str[0]

stats = {
    'question': QUESTION,
    'total': float(df['rating'].sum()),
    'mean': float(df['rating'].mean()),
    'median': float(df['rating'].median()),
    'std': float(df['rating'].std()),
    'min': float(df['rating'].min()),
    'max': float(df['rating'].max()),
    'count': int(len(df))
}

category_data = df.groupby('main_category')['rating'].mean().sort_values(ascending=False).reset_index()

plt.figure(figsize=(10, 8))
sns.barplot(data=category_data, x='rating', y='main_category', palette='magma')
plt.title('Average Product Rating by Category')
plt.xlabel('Average Rating')
plt.ylabel('Category')
plt.xlim(0, 5)

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


# Question 3: What is the distribution of product ratings?
# Output: analysis_1773598405.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\graphs"

QUESTION = """What is the distribution of product ratings?"""
base_name = "analysis_1773598405"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\data\amazon.csv')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df = df.dropna(subset=['rating'])

stats = {
    'question': QUESTION,
    'total': float(df['rating'].sum()),
    'mean': float(df['rating'].mean()),
    'median': float(df['rating'].median()),
    'std': float(df['rating'].std()),
    'min': float(df['rating'].min()),
    'max': float(df['rating'].max()),
    'count': int(len(df))
}

plt.figure(figsize=(10, 6))
sns.histplot(df['rating'], bins=15, kde=True, color='teal')
plt.title('Distribution of Product Ratings')
plt.xlabel('Rating')
plt.ylabel('Frequency')

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


# Question 4: Which products offer the best value (high rating + high discount)?
# Output: analysis_1773598429.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\graphs"

QUESTION = """Which products offer the best value (high rating + high discount)?"""
base_name = "analysis_1773598429"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\data\amazon.csv')

df['rating'] = pd.to_numeric(df['rating'].astype(str).str.replace('|', '0').str.replace(',', ''), errors='coerce').fillna(0)
df['discount_percentage'] = pd.to_numeric(df['discount_percentage'].astype(str).str.replace('%', ''), errors='coerce').fillna(0)
df['value_score'] = df['rating'] * df['discount_percentage']

stats = {
    'question': QUESTION,
    'total': float(df['value_score'].sum()),
    'mean': float(df['value_score'].mean()),
    'median': float(df['value_score'].median()),
    'std': float(df['value_score'].std()),
    'min': float(df['value_score'].min()),
    'max': float(df['value_score'].max()),
    'count': int(len(df))
}

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='discount_percentage', y='rating', hue='value_score', size='value_score', palette='viridis', alpha=0.6)
plt.title('Product Value Analysis: Rating vs Discount Percentage')
plt.xlabel('Discount Percentage (%)')
plt.ylabel('Rating (out of 5)')
plt.legend(title='Value Score', bbox_to_anchor=(1.05, 1), loc='upper left')

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


# Question 5: What are the top 10 most reviewed products?
# Output: analysis_1773598441.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\graphs"

QUESTION = """What are the top 10 most reviewed products?"""
base_name = "analysis_1773598441"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\data\amazon.csv')
df['rating_count'] = pd.to_numeric(df['rating_count'].str.replace(',', ''), errors='coerce').fillna(0)

top_10 = df.sort_values(by='rating_count', ascending=False).head(10)
top_10['product_name_short'] = top_10['product_name'].str[:50]

plt.figure(figsize=(10, 6))
sns.barplot(data=top_10, x='rating_count', y='product_name_short', palette='viridis')
plt.title('Top 10 Most Reviewed Products')
plt.xlabel('Number of Reviews')
plt.ylabel('Product Name')

stats = {
    'question': QUESTION,
    'total': float(df['rating_count'].sum()),
    'mean': float(df['rating_count'].mean()),
    'median': float(df['rating_count'].median()),
    'std': float(df['rating_count'].std()),
    'min': float(df['rating_count'].min()),
    'max': float(df['rating_count'].max()),
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


# Question 6: Give me an overall sales and product summary report.
# Output: analysis_1773598454.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\graphs"

QUESTION = """Give me an overall sales and product summary report."""
base_name = "analysis_1773598454"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_233347_ceb553f9\data\amazon.csv')

df['discounted_price'] = df['discounted_price'].astype(str).str.replace('₹', '').str.replace(',', '').astype(float)
df['actual_price'] = df['actual_price'].astype(str).str.replace('₹', '').str.replace(',', '').astype(float)
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['rating_count'] = df['rating_count'].astype(str).str.replace(',', '').astype(float)

df = df.dropna(subset=['discounted_price', 'actual_price', 'rating', 'rating_count'])

stats = {
    'question': QUESTION,
    'total': float(df['discounted_price'].sum()),
    'mean': float(df['discounted_price'].mean()),
    'median': float(df['discounted_price'].median()),
    'std': float(df['discounted_price'].std()),
    'min': float(df['discounted_price'].min()),
    'max': float(df['discounted_price'].max()),
    'count': int(len(df))
}

df['main_category'] = df['category'].str.split('|').str[0]
category_summary = df.groupby('main_category')['discounted_price'].mean().sort_values(ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x=category_summary.values, y=category_summary.index, palette='viridis')
plt.title('Average Discounted Price by Main Category')
plt.xlabel('Average Discounted Price (₹)')
plt.ylabel('Category')

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


