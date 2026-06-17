import json
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

class NumpyJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for numpy types"""
    def default(self, obj):
        try:
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
        except Exception:
            return str(obj)

# Question 1: Give an overall sales report.
# Output: analysis_1774028936.png
import os, json, pandas as pd, numpy as np, matplotlib.pyplot as plt, seaborn as sns
sns.set()
plt.ioff()

# Path configurations
RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = os.path.join(RESPONSE_DIR, "request_20260320_231846_90ca4dc0", "stats")
GRAPHS_DIR = os.path.join(RESPONSE_DIR, "request_20260320_231846_90ca4dc0", "graphs")
DATA_DIR = os.path.join(RESPONSE_DIR, "request_20260320_231846_90ca4dc0", "data")

# Ensure directories exist
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

QUESTION = """Give an overall sales report."""
base_name = "analysis_1774028936"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")
csv_path = os.path.join(DATA_DIR, "Covid_19_data.csv")

try:
    # Load data
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Data file not found at {csv_path}")
        
    df = pd.read_csv(csv_path)
    df = df.fillna(0)

    # Calculate stats
    confirmed_col = 'Confirmed' if 'Confirmed' in df.columns else df.select_dtypes(include=[np.number]).columns[0]
    region_col = 'Region' if 'Region' in df.columns else df.select_dtypes(include=['object']).columns[0]

    stats = {
        'question': QUESTION,
        'total': float(df[confirmed_col].sum()),
        'mean': float(df[confirmed_col].mean()),
        'median': float(df[confirmed_col].median()),
        'std': float(df[confirmed_col].std()),
        'min': float(df[confirmed_col].min()),
        'max': float(df[confirmed_col].max()),
        'count': int(len(df))
    }

    # Create visualization
    plt.figure(figsize=(10, 6))
    top_regions = df.groupby(region_col)[confirmed_col].sum().sort_values(ascending=False).head(10)
    sns.barplot(x=top_regions.values, y=top_regions.index, palette='viridis')
    plt.title(f'Top 10 {region_col}s by {confirmed_col} Cases')
    plt.xlabel(confirmed_col)
    plt.ylabel(region_col)

    # Save graph
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=100)
    except Exception as e:
        print(f"Error saving graph: {e}")
    finally:
        plt.close()

    # Save stats
    try:
        with open(stats_file, 'w') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")

except Exception as e:
    print(f"An error occurred during analysis: {e}")
    stats = {"question": QUESTION, "error": str(e)}

# Fallback save - ensures files always get written
try:
    if not os.path.exists(graph_file):
        plt.figure(figsize=(5, 5))
        plt.text(0.5, 0.5, "Graph generation failed", ha='center')
        plt.savefig(graph_file, bbox_inches="tight", dpi=100)
        plt.close()
except Exception:
    pass

try:
    if not os.path.exists(stats_file):
        if "stats" not in locals():
            stats = {"question": QUESTION, "note": "No stats generated due to error"}
        with open(stats_file, "w") as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
except Exception:
    pass