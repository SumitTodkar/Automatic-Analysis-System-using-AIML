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
        except Exception:
            pass
        return super().default(obj)

# Question 1: Give an overall sales report.
# Output: analysis_1774030395.png
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260320_234304_dcdf7aa5\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260320_234304_dcdf7aa5\graphs"

# Ensure directories exist
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

QUESTION = """Give an overall sales report."""
base_name = "analysis_1774030395"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")
data_path = os.path.join(r'C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260320_234304_dcdf7aa5', 'data', 'pizza_sales.csv')

stats = {"question": QUESTION}

try:
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Data file not found at {data_path}")
        
    df = pd.read_csv(data_path)
    
    if 'total_price' not in df.columns:
        raise ValueError("Column 'total_price' missing from dataset")
        
    df = df.dropna(subset=['total_price'])
    
    if df.empty:
        stats.update({'note': 'Dataset is empty after dropping nulls'})
    else:
        stats.update({
            'total': float(df['total_price'].sum()),
            'mean': float(df['total_price'].mean()),
            'median': float(df['total_price'].median()),
            'std': float(df['total_price'].std()) if len(df) > 1 else 0.0,
            'min': float(df['total_price'].min()),
            'max': float(df['total_price'].max()),
            'count': int(len(df))
        })

        # Plotting
        plt.figure(figsize=(10, 6))
        sns.set_style("whitegrid")
        
        if 'pizza_category' in df.columns:
            category_data = df.groupby('pizza_category')['total_price'].sum().sort_values(ascending=False).reset_index()
            sns.barplot(data=category_data, x='pizza_category', y='total_price', palette='viridis')
            plt.title('Total Sales Revenue by Pizza Category', fontsize=14)
            plt.xlabel('Pizza Category', fontsize=12)
            plt.ylabel('Total Revenue', fontsize=12)
        else:
            plt.text(0.5, 0.5, 'pizza_category column missing', ha='center')
            
        try:
            plt.savefig(os.path.join(GRAPHS_DIR, base_name + ".png"), bbox_inches='tight', dpi=100)
        except Exception as e:
            print(f"Error saving graph: {e}")
        finally:
            plt.close()

except Exception as e:
    stats['error'] = str(e)
    # Create an empty plot if error occurs to satisfy file requirements
    plt.figure()
    plt.text(0.5, 0.5, f"Error: {str(e)}", ha='center')
    plt.savefig(os.path.join(GRAPHS_DIR, base_name + ".png"), bbox_inches='tight', dpi=100)
    plt.close()

# Save stats
try:
    with open(os.path.join(STATS_DIR, base_name + "_stats.json"), 'w') as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
except Exception as e:
    print(f"Error saving stats: {e}")

# Fallback save - ensures files always get written if they don't exist
if not os.path.exists(graph_file):
    try:
        plt.figure()
        plt.text(0.5, 0.5, "Fallback: Graph generation failed", ha='center')
        plt.savefig(os.path.join(GRAPHS_DIR, base_name + ".png"), bbox_inches="tight", dpi=100)
        plt.close()
    except:
        pass

if not os.path.exists(stats_file):
    try:
        with open(os.path.join(STATS_DIR, base_name + "_stats.json"), "w") as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except:
        pass