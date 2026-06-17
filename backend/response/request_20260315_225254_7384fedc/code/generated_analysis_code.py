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

# Question 1: Give an overall analysis report.
# Output: analysis_1773595386.png
sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_225254_7384fedc\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_225254_7384fedc\graphs"
DATA_PATH = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260315_225254_7384fedc\data\amazon.csv"

# Ensure directories exist
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

QUESTION = """Give an overall analysis report."""
base_name = "analysis_1773595386"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")

try:
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Data file not found at {DATA_PATH}")
        
    df = pd.read_csv(DATA_PATH)

    # Data Cleaning
    df['discounted_price'] = df['discounted_price'].astype(str).str.replace('₹', '').str.replace(',', '').astype(float)
    df['actual_price'] = df['actual_price'].astype(str).str.replace('₹', '').str.replace(',', '').astype(float)
    # Handle the '|' character often found in the rating column of this specific dataset
    df['rating'] = pd.to_numeric(df['rating'].astype(str).str.replace('|', '0', regex=False), errors='coerce').fillna(0)
    df['rating_count'] = pd.to_numeric(df['rating_count'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    df = df.dropna(subset=['discounted_price', 'actual_price', 'rating'])

    if df.empty:
        stats = {'question': QUESTION, 'error': 'No data available after cleaning'}
    else:
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

        # Plotting
        plt.figure(figsize=(12, 6))
        sns.set_style("whitegrid")
        plot = sns.scatterplot(
            data=df, 
            x='actual_price', 
            y='discounted_price', 
            hue='rating', 
            size='rating_count', 
            sizes=(20, 200), 
            alpha=0.6, 
            palette='viridis'
        )
        plt.title('Amazon Product Pricing and Rating Analysis')
        plt.xlabel('Actual Price (INR)')
        plt.ylabel('Discounted Price (INR)')
        
        try:
            plt.savefig(graph_file, bbox_inches='tight', dpi=100)
        except Exception as e:
            print(f"Error saving graph: {e}")
        finally:
            plt.close()

except Exception as e:
    stats = {"question": QUESTION, "error": str(e)}
    print(f"An error occurred: {e}")

# Save stats with error handling
try:
    with open(stats_file, 'w') as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
except Exception as e:
    print(f"Error saving stats: {e}")

# Final check to ensure files exist as per requirements
if not os.path.exists(stats_file):
    try:
        with open(stats_file, "w") as f:
            json.dump({"question": QUESTION, "note": "Fallback stats"}, f, cls=NumpyJSONEncoder, indent=4)
    except:
        pass