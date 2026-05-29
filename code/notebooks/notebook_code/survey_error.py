import pandas as pd

from rpy2.robjects.vectors import StrVector, FloatVector, IntVector
from rpy2.robjects import DataFrame
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr


def pandas_to_r_dataframe(df: pd.DataFrame):
    """
    Converts a pandas DataFrame to an R-compatible DataFrame manually.

    Args:
        df (pd.DataFrame): The pandas DataFrame to convert.

    Returns:
        rpy2.robjects.DataFrame: An R-compatible DataFrame.
    """

    # Create a dictionary of R-compatible vectors
    r_data = {}
    for column_name, column_data in df.items():
        if pd.api.types.is_numeric_dtype(column_data):
            r_data[column_name] = FloatVector(column_data)
        elif pd.api.types.is_integer_dtype(column_data):
            r_data[column_name] = IntVector(column_data)
        elif pd.api.types.is_string_dtype(column_data):
            r_data[column_name] = StrVector(column_data)
        else:
            raise ValueError(f"Unsupported column type for '{column_name}'.")

    # Return the R DataFrame
    return DataFrame(r_data)

# Calculate weighted mean within strata
def weighted_mean(group: pd.DataFrame, variable: str):
    return np.average(group[variable], weights=group['Sample Weight'])

def survey_se(df: pd.DataFrame, variable: str):
    """
    Runs R code to calculate standard error for a given column in a survey design.

    Args:
        df (pd.DataFrame): The input pandas DataFrame.
        variable (str): The column for which to compute confidence intervals.

    Returns:
        tuple: (lower_confidence_interval, upper_confidence_interval)
    """
    # Ensure the DataFrame is compatible with rpy2
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input data must be a pandas DataFrame.")

    df_renamed = df.rename(columns={'Sample Weight': 'sw'})

    # Manually convert the pandas DataFrame to an R-compatible DataFrame
    r_df = pandas_to_r_dataframe(df_renamed)

    # Assign the R DataFrame to a variable in the R environment
    r.assign("data", r_df)

    # Clean column names in R to make them valid R identifiers
    r('colnames(data) <- make.names(colnames(data))')

    # Create unique PSU identifiers (adjust for your dataset structure)
    r("""
    library(dplyr)
    data <- data %>% mutate(psu = interaction(strata, psu, sep = "_"))
    """)

    # Define the survey design in R
    r("""
    design <- svydesign(
        id = ~psu,
        strata = ~strata,
        weights = ~sw,
        data = data,
        nest = TRUE
    )
    """)

    # Compute the confidence intervals in R
    r.assign("column_name", variable)

    r("""
    ci_result <- svymean(as.formula(paste("~", column_name)), design)
    mean_value <- coef(ci_result)[1]  # Extract the mean
    se_value <- SE(ci_result)[1]      # Extract the standard error
    """)

    # Extract mean and standard error
    mean_value = r("mean_value")[0]  # Convert mean to Python float
    se_value = r("se_value")[0]

    return mean_value, se_value