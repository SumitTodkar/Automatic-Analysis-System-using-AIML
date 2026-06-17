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

# Question 1: Give me overall sales report.
# Output: analysis_1773588653.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_205155_68100926\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_205155_68100926\graphs"

# Ensure directories exist
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

QUESTION = """Give me overall sales report."""
base_name = "analysis_1773588653"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    csv_path = os.path.join(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_205155_68100926\data', 'pizza_sales.csv')
    df = pd.read_csv(csv_path)
    
    if 'total_price' in df.columns:
        df = df.dropna(subset=['total_price'])
        
        stats = {
            'question': QUESTION,
            'total': float(df['total_price'].sum()) if not df.empty else 0.0,
            'mean': float(df['total_price'].mean()) if not df.empty else 0.0,
            'median': float(df['total_price'].median()) if not df.empty else 0.0,
            'std': float(df['total_price'].std()) if len(df) > 1 else 0.0,
            'min': float(df['total_price'].min()) if not df.empty else 0.0,
            'max': float(df['total_price'].max()) if not df.empty else 0.0,
            'count': int(len(df))
        }

        if not df.empty and 'pizza_category' in df.columns:
            plt.figure(figsize=(10, 6))
            sns.set_style("whitegrid")
            category_sales = df.groupby('pizza_category')['total_price'].sum().sort_values(ascending=False).reset_index()
            sns.barplot(data=category_sales, x='pizza_category', y='total_price', palette='viridis')
            plt.title('Overall Sales Report: Total Revenue by Pizza Category')
            plt.xlabel('Pizza Category')
            plt.ylabel('Total Revenue ($)')
            
            try:
                plt.savefig(graph_file, bbox_inches='tight', dpi=100)
            except Exception as e:
                print(f"Error saving graph: {e}")
            finally:
                plt.close()
    else:
        stats = {'question': QUESTION, 'error': 'Column total_price not found'}

except Exception as e:
    stats = {'question': QUESTION, 'error': str(e)}

# Save stats with error handling
try:
    with open(stats_file, 'w') as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
except Exception as e:
    print(f"Error saving stats: {e}")

# Fallback save - ensures files always get written
if not os.path.exists(graph_file):
    try:
        plt.figure(figsize=(5, 5))
        plt.text(0.5, 0.5, "Graph generation failed or no data", ha='center', va='center')
        plt.savefig(graph_file, bbox_inches="tight", dpi=100)
        plt.close()
    except:
        pass

if not os.path.exists(stats_file):
    try:
        if "stats" not in locals():
            stats = {"question": QUESTION, "note": "No stats generated"}
        with open(stats_file, "w") as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except:
        pass