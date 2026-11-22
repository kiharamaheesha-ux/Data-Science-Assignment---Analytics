"""
PART 2 — Numerical Computing with NumPy                           (10 points)
==============================================================================
Course topics: 08 NumPy (arrays vs lists, indexing & slicing, vectorised
               operations, aggregation, boolean masks, 2-D arrays)

Scenario
--------
You are given daily temperature readings and a matrix of student test
scores. Implement the functions below using **vectorised NumPy operations**.
Avoid Python ``for`` loops over array elements — that is the whole point
of NumPy!

Run your code:      python -m assignment.part2_numpy
Run the tests:      pytest tests/test_part2_numpy.py -v
"""
import numpy as np


def to_array(values):
    """Convert a Python list (or list of lists) to a NumPy array of dtype float64."""
    return np.array(values, dtype=np.float64)


def summary_stats(arr):
    """Return a dict with keys: mean, median, std, min, max.

    - Use the *population* standard deviation (NumPy's default, ddof=0).
    - Every value must be a plain Python ``float`` rounded to 2 decimals.
    """
    return {
        "mean": round(float(np.mean(arr)),2),
        "median": round(float(np.median(arr)),2),
        "std": round(float(np.std(arr)),2),
        "min": round(float(np.min(arr)),2),
        "max": round(float(np.max(arr)),2),
        
    }


def min_max_scale(arr):
    """Rescale values to the range [0, 1]:  (x - min) / (max - min).

    If all values are identical (max == min) return an array of zeros
    with the same shape.
    """
    min_scale = np.min(arr)
    max_scale = np.max(arr)
    if min_scale == max_scale:
        return np.zeros_like(arr,dtype=np.float64)
    return (arr - min_scale)/ (max_scale - min_scale)


def z_scores(arr):
    """Standardise values:  (x - mean) / std   (population std, ddof=0)."""
    return (arr - np.mean(arr)) / np.std(arr,ddof=0)


def filter_above(arr, threshold):
    """Return only the values strictly greater than ``threshold``.

    Use a boolean mask, e.g. ``arr[arr > threshold]``.
    """
    return arr[arr>threshold]


def count_in_range(arr, low, high):
    """Return (as an int) how many values satisfy  low <= x <= high."""
    count= (arr >= low) & (arr <= high)
    return int(np.sum(count))


def daily_change(arr):
    """Return the difference between consecutive values: arr[i] - arr[i-1].

    The result has one fewer element than the input. Hint: slicing or np.diff.
    """
    return np.diff(arr)


def column_means(matrix):
    """Return the mean of each COLUMN of a 2-D array (a 1-D array)."""
    return np.mean(matrix,axis=0)


def row_totals(matrix):
    """Return the sum of each ROW of a 2-D array (a 1-D array)."""
    return np.sum(matrix,axis=1)


def top_student(matrix, names):
    """Return the name of the student (row) with the highest average score.

    ``names[i]`` is the name for ``matrix[i]``. Hint: np.argmax.
    """
    average_scores= np.mean(matrix,axis=1)
    highest_average= int(np.argmax(average_scores))
    return names[highest_average]

if __name__ == "__main__":
    temps = to_array([24.5, 26.1, 27.8, 25.0, 29.4, 31.2, 30.0])
    print("Stats:", summary_stats(temps))
    print("Scaled:", np.round(min_max_scale(temps), 2))
    print("Hot days (>28):", filter_above(temps, 28))
    print("Change:", daily_change(temps))

    scores = to_array([[78, 85, 90], [88, 92, 79], [65, 70, 72]])
    print("Column means:", column_means(scores))
    print("Top student:", top_student(scores, ["Ama", "Kofi", "Esi"]))
