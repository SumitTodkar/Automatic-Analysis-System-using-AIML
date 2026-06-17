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

# Question 1: Give an overall sales report.
# Output: analysis_1774030006.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260320_233231_fb8b1290\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260320_233231_fb8b1290\graphs"

# Ensure directories exist
try:
    os.makedirs(STATS_DIR, exist_ok=True)
    os.makedirs(GRAPHS_DIR, exist_ok=True)
except Exception:
    pass

QUESTION = """Give an overall sales report."""
base_name = "analysis_1774030006"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    data_path = os.path.join(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260320_233231_fb8b1290\data', 'pizza_sales.csv')
    df = pd.read_csv(data_path)
    df = df.dropna()

    if not df.empty:
        stats = {
            'question': QUESTION,
            'total': float(df['total_price'].sum()) if 'total_price' in df.columns else 0.0,
            'mean': float(df['total_price'].mean()) if 'total_price' in df.columns else 0.0,
            'median': float(df['total_price'].median()) if 'total_price' in df.columns else 0.0,
            'std': float(df['total_price'].std()) if 'total_price' in df.columns and len(df) > 1 else 0.0,
            'min': float(df['total_price'].min()) if 'total_price' in df.columns else 0.0,
            'max': float(df['total_price'].max()) if 'total_price' in df.columns else 0.0,
            'count': int(len(df))
        }

        plt.figure(figsize=(10, 6))
        if 'pizza_category' in df.columns and 'total_price' in df.columns:
            sns.barplot(x='pizza_category', y='total_price', data=df, estimator=sum, errorbar=None)
            plt.title('Overall Sales Report: Total Revenue by Category')
            plt.xlabel('Pizza Category')
            plt.ylabel('Total Revenue')
        else:
            plt.text(0.5, 0.5, 'Required columns missing', ha='center')
        
        plt.savefig(graph_file, bbox_inches='tight', dpi=100)
        plt.close()
    else:
        stats = {'question': QUESTION, 'note': 'DataFrame is empty'}
except Exception as e:
    stats = {'question': QUESTION, 'error': str(e)}

# Save stats
try:
    with open(stats_file, 'w') as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
except Exception:
    pass

# Fallback save - ensures files always get written
if not os.path.exists(graph_file):
    try:
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "Graph generation failed", ha='center')
        plt.savefig(graph_file, bbox_inches="tight", dpi=100)
        plt.close()
    except Exception:
        pass

if not os.path.exists(stats_file):
    try:
        if "stats" not in dir():
            stats = {"question": QUESTION, "note": "No stats generated"}
        with open(stats_file, "w") as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception:
        pass