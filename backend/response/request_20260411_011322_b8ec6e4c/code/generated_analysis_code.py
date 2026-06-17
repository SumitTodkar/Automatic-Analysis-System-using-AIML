import json
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

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

# Question 1: Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly
# Output: analysis_1775850242.png

sns.set()
plt.ioff()

RESPONSE_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response"
STATS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_011322_b8ec6e4c\stats"
GRAPHS_DIR = r"C:\Users\Ashut\PycharmProjects\pythonProject14\Analytics system\backend\response\request_20260411_011322_b8ec6e4c\graphs"

# Ensure directories exist
os.makedirs(STATS_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

QUESTION = """Perform a comprehensive business and pricing analysis of the Amazon catalog. First, clean the 'actual_price', 'discounted_price', and 'rating_count' columns by removing the '₹' symbols and commas, and convert them to numeric. Extract the main 'Parent Category' by splitting the nested category string. Second, calculate the total number of products, the overall average rating, and the average discount percentage. Third, create a correlation matrix to see if there is a relationship between a product's price, its discount percentage, and its rating. Finally, identify the top 5 Parent Categories by volume and detect any abnormally expensive products using the IQR outlier method on the actual price. Use multi-panel subplots to visualize these trends clearly"""
base_name = "analysis_1775850242"
graph_file = os.path.join(GRAPHS_DIR, base_name + ".png")
stats_file = os.path.join(STATS_DIR, base_name + "_stats.json")
csv_path = os.path.join(RESPONSE_DIR, 'amazon.csv')

try:
    df = pd.read_csv(csv_path)

    # Data Cleaning
    for col in ['actual_price', 'discounted_price', 'rating_count', 'discount_percentage']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('₹', '').str.replace(',', '').str.replace('%', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'category' in df.columns:
        df['parent_category'] = df['category'].astype(str).str.split('|').str[0]
    else:
        df['parent_category'] = 'Unknown'

    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    # Drop duplicates and handle missing values for critical analysis columns
    df = df.drop_duplicates()
    df_clean = df.dropna(subset=['actual_price', 'rating', 'discount_percentage']).copy()

    # IQR Outlier Detection
    Q1 = df_clean['actual_price'].quantile(0.25)
    Q3 = df_clean['actual_price'].quantile(0.75)
    IQR = Q3 - Q1
    upper_bound = Q3 + 1.5 * IQR
    outliers = df_clean[df_clean['actual_price'] > upper_bound]

    # Calculate Stats
    stats = {
        'question': QUESTION,
        'total_records': int(len(df_clean)),
        'mean_actual_price': float(df_clean['actual_price'].mean()),
        'median_actual_price': float(df_clean['actual_price'].median()),
        'std_actual_price': float(df_clean['actual_price'].std()),
        'min_actual_price': float(df_clean['actual_price'].min()),
        'max_actual_price': float(df_clean['actual_price'].max()),
        'outlier_count': int(len(outliers)),
        'skewness': float(df_clean['actual_price'].skew()) if not df_clean['actual_price'].empty else 0,
        'top_category': str(df_clean['parent_category'].value_counts().idxmax()) if not df_clean['parent_category'].empty else "N/A",
        'avg_rating': float(df_clean['rating'].mean()),
        'avg_discount': float(df_clean['discount_percentage'].mean())
    }

    # Save Stats
    try:
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)
    except Exception as e:
        print(f"Error saving stats: {e}")

    # Visualization
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))

    # 1. Price Distribution
    sns.histplot(df_clean['actual_price'], kde=True, ax=axes[0, 0], color='skyblue')
    axes[0, 0].set_xscale('log')
    axes[0, 0].set_title('Actual Price Distribution (Log Scale)')
    axes[0, 0].set_xlabel('Price (INR)')
    axes[0, 0].set_ylabel('Frequency')

    # 2. Top 5 Categories
    top_cats = df_clean['parent_category'].value_counts().head(5)
    sns.barplot(x=top_cats.values, y=top_cats.index, hue=top_cats.index, ax=axes[0, 1], palette='viridis', legend=False)
    axes[0, 1].set_title('Top 5 Parent Categories by Volume')
    axes[0, 1].set_xlabel('Number of Products')
    axes[0, 1].set_ylabel('Category')

    # 3. Correlation Matrix
    corr = df_clean[['actual_price', 'discount_percentage', 'rating']].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=axes[1, 0])
    axes[1, 0].set_title('Correlation: Price, Discount, Rating')

    # 4. Rating vs Discount
    sns.scatterplot(data=df_clean, x='discount_percentage', y='rating', alpha=0.4, ax=axes[1, 1], color='coral')
    axes[1, 1].set_title('Rating vs Discount Percentage')
    axes[1, 1].set_xlabel('Discount %')
    axes[1, 1].set_ylabel('Rating')

    plt.suptitle("Amazon Catalog Business & Pricing Analysis", fontsize=16, fontweight='bold')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    try:
        plt.savefig(graph_file, bbox_inches='tight', dpi=150)
    except Exception as e:
        print(f"Error saving graph: {e}")
    finally:
        plt.close('all')

except Exception as e:
    # Error handling for file operations and processing
    error_stats = {"question": QUESTION, "error": str(e)}
    try:
        with open(stats_file, "w", encoding='utf-8') as f:
            json.dump(error_stats, f, indent=4)
    except:
        pass

# Fallback check
if not os.path.exists(stats_file):
    stats = {"question": QUESTION, "note": "No stats generated due to processing error"}
    with open(stats_file, "w", encoding='utf-8') as f:
        json.dump(stats, f, cls=NumpyJSONEncoder, indent=4)