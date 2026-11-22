"""
PART 4 — Data Cleaning                                            (20 points)
==============================================================================
Course topics: 11 Data Cleaning (missing values, duplicates, text formatting,
               invalid values & outliers with the IQR method, filling
               missing values, type conversion), 06 Error Handling

Scenario
--------
HR exported ``data/employees_messy.csv`` from an old system. It contains:
  * exact duplicate rows
  * inconsistent text ("  KOFI MENSAH ", "accra", " marketing")
  * impossible values (negative ages, a performance score of 145)
  * extreme salary outliers (typos with extra zeros)
  * missing values in several columns

Build a cleaning pipeline out of small, testable functions. Each function
must return a NEW DataFrame and must NOT modify the DataFrame passed in
(start with ``df = df.copy()``).

Run your code:      python -m assignment.part4_data_cleaning
Run the tests:      pytest tests/test_part4_data_cleaning.py -v
"""
from pathlib import Path
import pandas as pd  # noqa: F401  (you will need this)

from assignment.paths import EMPLOYEES_CSV, OUTPUT_DIR



TEXT_COLUMNS = ["Name", "City", "Department"]


def load_raw(path=EMPLOYEES_CSV):
    """Load the messy employee CSV exactly as it is (no cleaning yet)."""
    return pd.read_csv(path)


def missing_report(df):
    """Return a DataFrame describing missing values per column.

    - Index: column names, but ONLY columns that have at least one missing value
    - Columns: ``missing_count`` (int) and ``missing_pct`` (percentage of rows,
      rounded to 2 decimals)
    - Sorted by ``missing_count`` descending
    """
    counts = df.isnull().sum()
    counts = counts[counts > 0]
    pct = (counts / len(df) * 100).round(2)

    report = pd.DataFrame({
        "missing_count":counts.astype(int),
        "missing_pct":pct,
    })
    return report.sort_values("missing_count", ascending=False)


def remove_duplicates(df):
    """Drop exact duplicate rows (keep the first) and reset the index."""
    df = df.copy() 
    return df.drop_duplicates().reset_index(drop=True)


def standardize_text(df):
    """Clean the text columns Name, City and Department.

    - Strip leading/trailing whitespace
    - Convert to Title Case ("kofi mensah" -> "Kofi Mensah")
    - Gotcha: Title Case turns "HR" into "Hr". The Department value must stay "HR".
    - Missing values must stay missing (do not turn NaN into the string "Nan").
    """
    df = df.copy()
    for col in TEXT_COLUMNS :
        df[col] = df[col].str.strip().str.title()

    df["Department"] = df["Department"].replace("Hr", "HR")
    return df


def fix_invalid_values(df):
    """Replace impossible values with NaN (domain-knowledge rules):

    - Age must be between 18 and 70 (inclusive)
    - PerformanceScore must be between 0 and 100 (inclusive)

    Values outside these ranges become NaN; they will be filled later.
    """
    df=df.copy()
    df["Age"] = df["Age"].where(df["Age"].between(18,70))
    df["PerformanceScore"] = df["PerformanceScore"].where(df["PerformanceScore"].between(0,100))
    return df

def iqr_bounds(series, k=1.5):
    """Return ``(lower, upper)`` outlier bounds using the IQR method.

        Q1 = 25th percentile, Q3 = 75th percentile, IQR = Q3 - Q1
        lower = Q1 - k * IQR ;  upper = Q3 + k * IQR

    Missing values must be ignored. Return plain floats.
    """
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr 
    upper = q3 + k * iqr
    return (lower,upper)


def cap_outliers(df, column, k=1.5):
    """Clip ``column`` to its IQR bounds (from ``iqr_bounds``).

    Capping keeps the row instead of deleting it. NaNs stay NaN.
    """
    df = df.copy()
    lower , upper = iqr_bounds(df[column], k=k)
    df[column] = df[column].clip(lower=lower, upper=upper)
    return df


def fill_missing(df):
    """Fill missing values with these strategies:

    - Age, PerformanceScore -> the column MEDIAN
    - MonthlySalary          -> the MEDIAN salary of that employee's Department
                                (hint: ``groupby(...).transform("median")``)
    - City                   -> the string "Unknown"
    - Education              -> the column MODE (most common value)

    After this step the DataFrame must have no missing values.
    """
    df = df.copy()
    return df.fillna({
        "Age": df["Age"].median(),
        "PerformanceScore": df["PerformanceScore"].median(),
        "MonthlySalary": df.groupby("Department")["MonthlySalary"].transform("median"),
        "City": "Unknown",
        "Education": df["Education"].mode().iloc[0],
    })

    

def convert_types(df):
    """Fix data types:

    - JoinDate -> datetime64
    - Age      -> int (round first: 34.6 -> 35)
    - Education -> an ORDERED pandas Categorical with order BSc < MSc < PhD
      (hint: ``pd.Categorical(..., categories=[...], ordered=True)``)
    """
    df= df.copy()
    df["JoinDate"] = pd.to_datetime(df["JoinDate"])
    df["Age"] = df["Age"].round().astype(int)
    df["Education"] = pd.Categorical(df["Education"],
                                     categories=["BSc", "MSc", "PhD"],
                                     ordered=True)
    return df 

def clean_pipeline(path=EMPLOYEES_CSV, save_to=OUTPUT_DIR / "employees_clean.csv"):
    """Run the full pipeline in this order and return the clean DataFrame:

        load_raw -> remove_duplicates -> standardize_text -> fix_invalid_values
        -> cap_outliers(MonthlySalary) -> fill_missing -> convert_types

    If ``save_to`` is not None, also save the result as CSV (no index),
    creating the folder if needed.
    """
    df = (
        load_raw(path)
        .pipe(remove_duplicates)
        .pipe(standardize_text)
        .pipe(fix_invalid_values)
        .pipe(cap_outliers, "MonthlySalary")
        .pipe(fill_missing)
        .pipe(convert_types)
    )

    if save_to is not None:
        Path(save_to).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(save_to, index=False)

    return df

if __name__ == "__main__":
    raw = load_raw()
    print("Raw shape:", raw.shape)
    print(missing_report(raw))
    clean = clean_pipeline()
    print("Clean shape:", clean.shape)
    print(clean.head())
    print(clean.dtypes)
