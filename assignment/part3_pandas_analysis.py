"""
PART 3 — Data Analysis with Pandas                                (15 points)
==============================================================================
Course topics: 09 Pandas (Series, DataFrames, reading data, selecting,
               filtering, groupby/aggregation), 10 Understanding Data
               (data types, central tendency, dispersion, skewness)

Scenario
--------
``data/sales_sample.csv`` holds 5,000 orders from a bicycle and accessories
retailer (columns include Date, Country, Product_Category, Product,
Order_Quantity, Revenue, Profit, Cost ...).
Management wants a quick, reliable picture of where the money comes from.

Run your code:      python -m assignment.part3_pandas_analysis
Run the tests:      pytest tests/test_part3_pandas_analysis.py -v
"""
import pandas as pd  # noqa: F401  (you will need this)

from assignment.paths import SALES_CSV



def load_sales(path=SALES_CSV):
    """Load the sales CSV into a DataFrame.

    The ``Date`` column is written day-first (e.g. 26/11/2013). Convert it to
    a proper datetime column (hint: ``pd.to_datetime(..., dayfirst=True)``
    or ``format="%d/%m/%Y"``).
    """
    df = pd.read_csv(path)
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
    return df


def dataset_overview(df):
    """Return a dict describing the dataset with these keys:

    - ``rows``: number of rows (int)
    - ``columns``: number of columns (int)
    - ``missing_total``: total number of missing cells (int)
    - ``numeric_columns``: list of numeric column names (original order)
    - ``categorical_columns``: list of text/object column names (original order)

    Hint: ``df.select_dtypes(include="number")`` and
    ``df.select_dtypes(include=["object", "string"])``. The datetime ``Date``
    column should appear in NEITHER list.
    """
    return{
        "rows" : int(df.shape[0]),
        "columns" : int(df.shape[1]),
        "missing_total" : int(df.isnull().sum().sum()),
        "numeric_columns" : df.select_dtypes(include="number").columns.tolist(),
        "categorical_columns" : df.select_dtypes(
            include=["object" ,"string"]
        ).columns.tolist()
    }


def revenue_by_country(df):
    """Total Revenue per Country as a Series, sorted from highest to lowest."""
    return df.groupby("Country")["Revenue"].sum().sort_values(ascending=False)


def top_products_by_profit(df, n=5):
    """Return the ``n`` products with the highest total Profit.

    Result: a Series indexed by Product, sorted descending, length ``n``.
    """
    return (df.groupby("Product")["Profit"].sum().sort_values(ascending=False).head(n)
    )


def monthly_revenue(df, year):
    """Total Revenue for each month (1–12) of the given ``year``.

    - Filter rows for that year using the parsed Date column.
    - Return a Series indexed by month NUMBER 1..12 (all 12 months present;
      fill months with no sales with 0).
    """
    return(
        df[df["Date"].dt.year == year]
        .groupby(df["Date"].dt.month)["Revenue"]
        .sum()
        .reindex(range(1,13), fill_value=0)
    )


def category_summary(df):
    """Summarise each Product_Category.

    Return a DataFrame indexed by Product_Category with columns, in order:
        orders   — number of rows
        revenue  — total Revenue
        profit   — total Profit
        margin   — profit / revenue * 100, rounded to 2 decimals
    sorted by ``revenue`` descending.
    """
    pc = df.groupby("Product_Category")
    summary = pd.DataFrame({
        "orders": pc.size(),
        "revenue" : pc["Revenue"].sum(),
        "profit" : pc["Profit"].sum(),
    })
    summary["margin"]=(summary["profit"] / summary["revenue"] * 100).round(2)
    return summary.sort_values("revenue", ascending=False)
    


def high_value_orders(df, min_revenue=2000, country=None):
    """Filter orders with Revenue >= ``min_revenue``.

    If ``country`` is given, also keep only orders from that country.
    Return the filtered DataFrame (keep the original index).
    """
    hv = df["Revenue"] >= min_revenue
    if country is not None:
        hv = hv & (df["Country"] == country)
    return df[hv]


def describe_column(series):
    """Return descriptive statistics for a numeric Series as a dict:

        mean, median, mode, range, variance, std, q1, q3, iqr, skew

    - Use pandas' defaults (sample variance/std, ddof=1).
    - ``mode``: the smallest mode if there are several (``series.mode()[0]``).
    - ``range`` = max - min ; ``iqr`` = q3 - q1 (q1/q3 are the 25th/75th
      percentiles).
    - Every value must be a Python float rounded to 2 decimals.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    stats = {
        "mean": series.mean(),
        "median":series.median(),
        "mode":series.mode(0),
        "range":series.max() - series.min(),
        "variance":series.var(),
        "std":series.std(),
        "q1":q1,
        "q3":q3,
        "iqr":q3-q1,
        "skew": series.skew()

    }
    return {k: round(float(v),2) for k, v in stats.items()}


def skew_direction(series):
    """Return "right-skewed" if skew > 0.5, "left-skewed" if skew < -0.5,
    otherwise "approximately symmetric"."""
    sk = series.skew()
    if sk > 0.5:
        return "right-skewed"
    elif sk < -0.5:
        return "left-skewed"
    return "approximately symmetric"
  


if __name__ == "__main__":
    sales = load_sales()
    print(dataset_overview(sales))
    print(revenue_by_country(sales))
    print(top_products_by_profit(sales))
    print(category_summary(sales))
    print(describe_column(sales["Revenue"]), skew_direction(sales["Revenue"]))
