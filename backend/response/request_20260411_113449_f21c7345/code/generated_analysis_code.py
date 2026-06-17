
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

# Question 1: Give overall analysis report.
# Output: analysis_1775887500.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
import warnings; warnings.filterwarnings("ignore")
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_113449_f21c7345\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_113449_f21c7345\graphs"

# ── Always use DATA_PATH to read the CSV ──
DATA_PATH = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_113449_f21c7345\data\pizza_sales.csv"
QUESTION = """Give overall analysis report."""
base_name = "analysis_1775887500"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

df = pd.read_csv(DATA_PATH)
df = df.dropna()

stats = {
    'question': QUESTION,
    'total': float(df['total_price'].sum()),
    'mean': float(df['total_price'].mean()),
    'median': float(df['total_price'].median()),
    'std': float(df['total_price'].std()),
    'min': float(df['total_price'].min()),
    'max': float(df['total_price'].max()),
    'count': int(len(df))
}

plt.figure(figsize=(10, 6))
sns.barplot(x='pizza_category', y='total_price', data=df, estimator=sum, errorbar=None, palette='viridis')
plt.title('Total Sales Revenue by Pizza Category')
plt.xlabel('Pizza Category')
plt.ylabel('Total Revenue')

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


