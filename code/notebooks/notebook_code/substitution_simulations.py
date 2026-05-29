import pandas as pd
import os
import numpy as np
import time
import gc
import operator
import rpy2.robjects as ro

from data_processing import filter_dataframes
from survey_error import survey_se
from pathlib import Path

from rpy2.robjects.vectors import FloatVector, IntVector, StrVector, FactorVector
from rpy2.robjects import r, pandas2ri, DataFrame

all_meat_food_groups = np.loadtxt('data/indicator_lists/all_meat_food_groups.txt', dtype=str)

def food_group_substitution_per_gram(row: pd.DataFrame, 
                             food_group: str, 
                             substitute: str, 
                             diet_data_reduced: pd.DataFrame, 
                             nutrients_per_gram_sub: pd.DataFrame, 
                             indicators: list,
                             error_columns: list):

  """
  Calculates the impact on each indicator in the list indicators following gram for gram replacements of food_group with the substitute. Calculates impacts from the item-level reductions to allow for multiple food group and substitute pairs in a single simulation scenario.   
  """

  id = row.name
  diet = diet_data_reduced[diet_data_reduced['Cpseriala']==id]
  num_days = diet['RecallNo'].nunique()

  reductiong_total = diet_data_reduced.loc[diet_data_reduced['Cpseriala']==id][food_group + '_reduction'].sum()  # reduction in consumption of the aggregate meat variable, e.g. Beefg
  reductiong_daily = reductiong_total/num_days

  if reductiong_daily > 0:
    for nutr in indicators:
      if nutr in error_columns:
        ## standard error after adding in replacement food is the combined error of the relacement se and the se on the current intake/impact
        row[nutr] = np.sqrt((reductiong_daily*nutrients_per_gram_sub.loc[substitute, nutr])**2 + row[nutr]**2)
      else:
        row[nutr] += reductiong_daily*nutrients_per_gram_sub.loc[substitute, nutr]

  else:
    pass

  return row

def food_group_substitution_per_gram_ind_level(row: pd.Series, 
                                               food_group: str, 
                                               substitute: str, 
                                               nutrients_per_gram_sub: pd.DataFrame, 
                                               indicators: list,
                                               error_columns: list):
                                                   
  """
  Calculates the impacts of gram for gram substitution for all indicators in the list indicators. 
  Assumes average daily reduction for the food group has been calculated at the particpant level and is available in the participant level data in the column f'{food group} reduction'.
  Only allows for one substition for each food_group per scenario.  
  """

  id = row.name
  # reduction in consumption of the aggregate meat variable, e.g. red and red processed meat
  reduction_g = float(row[f"{food_group} reduction"]) 

  if reduction_g > 0:
    for nutr in indicators:
      if nutr in error_columns:
          ## standard error after adding in replacement food is the combined error of the relacement se and the se on the current intake/impact
          row[nutr] = np.sqrt((reduction_g*nutrients_per_gram_sub.loc[substitute, nutr])**2 + row[nutr]**2)
      else:
          row[nutr] += reduction_g*nutrients_per_gram_sub.loc[substitute, nutr]
  else:
    pass

  return row
  
# def table_mean_values_subgroup(df_reduced_total: pd.DataFrame, 
#                               conditions_tuple: tuple, 
#                               df_baseline_total: pd.DataFrame, 
#                               nutrient_label_dict: dict, 
#                               standard_error_dict: dict,
#                               error_columns: list):

#   nutrients = nutrient_label_dict.keys()
#   dfs = [df_baseline_total, df_reduced_total]
#   filtered_data = filter_dataframes(dfs=dfs, conditions_tuple = conditions_tuple) 

#   # conditions are part of a tuple, with the first element being the description and the second being the set of conditions
#   df_baseline = filtered_data[0]
#   df_reduced = filtered_data[1]

#   mean_baseline = (df_baseline[nutrients].multiply(df_baseline['Sample Weight'], axis=0)).sum() / df_baseline['Sample Weight'].sum()
#   mean_reduced = (df_reduced[nutrients].multiply(df_reduced['Sample Weight'], axis=0)).sum() / df_reduced['Sample Weight'].sum()

#   # weighted standard error of between individual variance

#   error_baseline = (1/df_baseline['Sample Weight'].sum()) * np.sqrt( ((df_baseline[error_columns].multiply(df_baseline['Sample Weight'], axis=0))**2).sum())
#   error_reduced = (1/df_reduced['Sample Weight'].sum()) * np.sqrt( ((df_reduced[error_columns].multiply(df_reduced['Sample Weight'], axis=0))**2).sum())
  
#   mean_baseline[error_columns] = error_baseline
#   mean_reduced[error_columns] = error_reduced

#   for nutr in nutrient_label_dict.keys():
#     if nutr not in error_columns:
#       _, survey_error_baseline = survey_se(df=df_baseline, variable=nutr)
#       _, survey_error_reduced = survey_se(df=df_reduced, variable=nutr)
#       mean_baseline[f"survey_se_{nutr}"] = survey_error_baseline
#       mean_reduced[f"survey_se_{nutr}"] = survey_error_reduced

#   # Include the survey error in the overall error
#   for nutr in nutrient_label_dict.keys():
#     if nutr in error_columns:
#       mean_baseline[nutr] = np.sqrt(mean_baseline[nutr]**2 + mean_baseline[f'survey_se_{standard_error_dict[nutr]}']**2)
#       mean_reduced[nutr] = np.sqrt(mean_reduced[nutr]**2 + mean_reduced[f'survey_se_{standard_error_dict[nutr]}']**2)

#   change_subgroup = mean_reduced - mean_baseline
#   for nutr in nutrient_label_dict.keys():
#     if nutr in error_columns:
#       change_subgroup[nutr] = np.sqrt(mean_reduced[nutr]**2+ mean_baseline[nutr]**2)
#     else:
#       change_subgroup[f"survey_se_{nutr}"] = np.sqrt(mean_reduced[f"survey_se_{nutr}"]**2+ mean_baseline[f"survey_se_{nutr}"]**2)

#   mean_reduced = np.array(mean_reduced)
#   mean_reduced = np.round(mean_reduced, 2)

#   change_subgroup = np.array(change_subgroup)
#   change_subgroup = np.round(change_subgroup, 3)

#   return change_subgroup, mean_reduced

def pandas_to_r_dataframe(df: pd.DataFrame):
    """
    Converts a pandas DataFrame to an R-compatible DataFrame manually.
    Handles numeric, integer, and string/object columns (as factors in R).

    Args:
        df (pd.DataFrame): The pandas DataFrame to convert.

    Returns:
        rpy2.robjects.DataFrame: An R-compatible DataFrame.
    """

    r_data = {}
    for column_name, column_data in df.items():
        if pd.api.types.is_numeric_dtype(column_data):
            r_data[column_name] = FloatVector(column_data.fillna(float("nan")))
        elif pd.api.types.is_integer_dtype(column_data):
            r_data[column_name] = IntVector(column_data.fillna(0))
        elif pd.api.types.is_string_dtype(column_data) or column_data.dtype == "object":
            # Convert string/object columns into R factors
            column_data = column_data.fillna("").astype(str)
            r_data[column_name] = FactorVector(StrVector(column_data))
        else:
            raise ValueError(f"Unsupported column type for '{column_name}'.")

    return DataFrame(r_data)


def survey_results_by_subgroup(df: pd.DataFrame, nutrients: list, subgroup_conditions: list):
    """
    Calculate survey-weighted means + SEs for multiple nutrients and multiple population subgroups.

    Args:
        df (pd.DataFrame): Dataset (baseline or simulated scenario).
        nutrients (list): Nutrient column names.
        subgroup_conditions (list[tuple]): List of (label, conditions), where each condition is
                                           [{'column', 'operator', 'value', 'boolean_operator'}, ...]

        Conditions needs to be mutually exclusive for each subgroup i.e. cannot include age conditions and sex conditions. 
        Should the conditions not be mutally exclusive there will be an additional unlabelled subgroup in the final dataframe 

    Returns:
        pd.DataFrame: Columns = ["subgroup", "mean_intake_nutrient_i", ... , "se_nutrient_i"]
    """
    # rename the sample weight column to be readable by R
    df = df.rename(columns={'Sample Weight': 'sw'})

    # Create a new subgroup column to label the subgroups
    df_subgroup = df.copy()
    subgroup_labels = []
    mask_total = pd.Series(False, index=df.index)

    # Define the operators
    operator_map = {
    '>=': operator.ge,
    '<=': operator.le,
    '>': operator.gt,
    '<': operator.lt,
    '==': operator.eq,
    '!=': operator.ne
    }

    # Assign subgroup labels using Python filtering
    for label, conditions in subgroup_conditions:
        # For the overall group do not apply filtering
        if label == "Overall":
            df_subgroup.loc[~mask_total, "subgroup"] = label
        else:
          mask = pd.Series(True, index=df.index)

          for cond in conditions:
              operator_str = cond['operator']
              col = cond['column']
              val = cond['value']

              if operator_str not in operator_map:
                  raise ValueError(f"Unsupported operator: {operator_str}")

              op_function = operator_map[operator_str]
              mask &= op_function(df[col], val)

          df_subgroup.loc[mask, "subgroup"] = label

    ########## Beginning of R script ###########################
    r_df = pandas_to_r_dataframe(df_subgroup)
    r.assign("data", r_df)
    r('colnames(data) <- make.names(colnames(data))')

    nutrients_r = " + ".join([f"`{n}`" for n in nutrients])
    r.assign("formula_str", f"~ {nutrients_r}")

    r("""
    # iteratively test the different strata variables in building a survey design to ensure at least 2 psu per strata
    strata_candidates <- c("strata")
    design <- NULL
    all_nutrient_vars <- all.vars(as.formula(formula_str))
    column_test <- all_nutrient_vars[1]

    for (strata_var in strata_candidates) {
      if (!strata_var %in% names(data)) next

      try({
        data[[strata_var]] <- as.character(data[[strata_var]])
        data$psu <- as.character(data$psu)
        data$psu <- interaction(data[[strata_var]], data$psu, sep = "_")

        design_attempt <- svydesign(
          id = ~psu,
          strata = as.formula(paste0("~", strata_var)),
          weights = ~sw,
          data = data,
          nest = TRUE
        )

        # Test if estimation will succeed with a particular strata variable
        ci_test <- try(svymean(as.formula(paste("~", column_test)), design_attempt), silent = TRUE)
        #print(ci_test)

        if (!inherits(ci_test, "try-error")) {
          design <- design_attempt
          #message("Successfully created survey design with: ", strata_var)
          break
        }

      }, silent = TRUE)
    }

    """)

    r("""
    svy_results <- svyby(
        formula = as.formula(formula_str),
        by = ~subgroup,
        design = design,
        FUN = svymean,
        vartype = c("se")
    )
    """)

    pandas2ri.activate()
    result_df = ro.r['svy_results']

    ## Convert the R dataframe back to a pandas dataframe
    with (ro.default_converter + pandas2ri.converter).context():
      result_df = ro.conversion.get_conversion().rpy2py(result_df)
      
    ############ end of R script ##################

    for col in result_df.columns:
      if col.startswith("se."):
        new_col = col.replace("se.", "survey_se_")
        result_df.rename(columns={col: new_col}, inplace=True)

    for label, _ in subgroup_conditions:
      if label == "Overall":
        result_df['subgroup'] = 'Overall'

    ro.r('rm(list = ls())') # Removes all objects from the R environment
    ro.r('gc()')

    return result_df

def table_mean_values_subgroup(df_reduced_total: pd.DataFrame,
                               subgroup_conditions: list,
                               df_baseline_total: pd.DataFrame,
                               nutrients: list,
                               nutrient_label_dict: dict,
                               mean_env_columns: list,
                               standard_error_dict: dict
                               ):

    #nutrients = list(nutrient_label_dict.keys())
    # remove the within-item indicators from the list of nutrients as these have already been accounted for in combine_seeds()

    # extract the indicators that have associated metadata in the nutrient_label_dict 
    indicators = [nutr for nutr in nutrient_label_dict.keys() if not nutr.startswith('se_') and nutr in nutrients+mean_env_columns]
    error_dict = {value: key for key, value in standard_error_dict.items()}

    for nutr in indicators:
      # set the standard error of the baseline indicators as the within item uncertainty for env, otherwise set them as 0 for the nutrients
      if nutr in mean_env_columns:
        df_baseline_total[f"se_{nutr}"] = df_baseline_total[error_dict[nutr]]
      else:
        df_baseline_total[f"se_{nutr}"] = 0

    cols_to_remove = []
    for col in df_reduced_total:
      if col not in df_baseline_total.columns:
        cols_to_remove.append(col)

    df_baseline_total_local = df_baseline_total.copy()
    df_reduced_total.drop(columns=cols_to_remove, inplace=True)

    # Get survey results for baseline + reduced
    survey_baseline = survey_results_by_subgroup(df=df_baseline_total_local, nutrients=indicators, subgroup_conditions=subgroup_conditions)
    survey_reduced = survey_results_by_subgroup(df=df_reduced_total, nutrients=indicators, subgroup_conditions=subgroup_conditions)

    survey_baseline.set_index('subgroup', inplace=True)
    survey_reduced.set_index('subgroup', inplace=True)

    error_columns = [f"se_{nutr}" for nutr in indicators]

    for nutr in indicators:
      # set the standard error of the baseline indicators as the within item uncertainty for env, otherwise set them as 0 for the nutrients
      if nutr in mean_env_columns:
        df_baseline_total_local[f"se_{nutr}"] = df_baseline_total_local[error_dict[nutr]]
      else:
        df_baseline_total_local[f"se_{nutr}"] = 0

    dfs = [df_baseline_total_local, df_reduced_total]

    for conditions_tuple in subgroup_conditions:
      subgroup_label = conditions_tuple[0]

      filtered_data = filter_dataframes(dfs=dfs, conditions_tuple=conditions_tuple)
      df_baseline = filtered_data[0]
      df_reduced = filtered_data[1]

      error_baseline = (1/df_baseline['Sample Weight'].sum()) * np.sqrt(((df_baseline[error_columns] * df_baseline['Sample Weight'])**2).sum())
      error_reduced = (1/df_reduced['Sample Weight'].sum()) * np.sqrt(((df_reduced[error_columns] * df_reduced['Sample Weight'])**2).sum())

      # add in the within-item uncertainty for the enviornmental indicators
      for nutr in indicators:
        survey_var_baseline = survey_baseline.loc[subgroup_label, f"survey_se_{nutr}"] ** 2
        survey_var_reduced = survey_reduced.loc[subgroup_label, f"survey_se_{nutr}"] ** 2

        survey_baseline.loc[subgroup_label, f"se_{nutr}"] = np.sqrt(error_baseline[f"se_{nutr}"]**2 + survey_var_baseline)
        survey_reduced.loc[subgroup_label, f"se_{nutr}"] = np.sqrt(error_reduced[f"se_{nutr}"]**2 + survey_var_reduced)

    # after combining total standard error with survey error for all subgroups, drop the survey error columns from the analysis
    for nutr in indicators:
      survey_baseline.drop(columns=[f"survey_se_{nutr}"], inplace=True)
      survey_reduced.drop(columns=[f"survey_se_{nutr}"], inplace=True)

    df_mean_baseline = survey_baseline.drop(columns=error_columns)
    df_mean_reduced = survey_reduced.drop(columns=error_columns)
    df_change_mean = df_mean_reduced - df_mean_baseline

    df_error_baseline = survey_baseline[error_columns]
    df_error_reduced = survey_reduced[error_columns]

    df_change_error = np.sqrt(df_error_baseline**2 + df_error_reduced**2)
    df_change = pd.concat([df_change_mean, df_change_error], axis=1)

    return survey_baseline, survey_reduced, df_change


def results_table(path_scenario: Path, 
                  all_conditions: list, 
                  df_reduced_total: pd.DataFrame, 
                  df_baseline_total: pd.DataFrame, 
                  nutrient_label_dict: dict, 
                  nutrients: list,
                  mean_env_columns: list,
                  scenario: int ,
                  error_columns: list,
                  standard_error_dict: dict
                  ):

    nutrients_head = [f"{data['title']}, {data['units']}" for nutr, data in nutrient_label_dict.items() if not nutr.startswith('se_') and nutr in nutrients+mean_env_columns]
    standard_error_columns = [f"se_{nutr}" for nutr in nutrient_label_dict.keys() if not nutr.startswith('se') and nutr in nutrients+mean_env_columns]

    df_change = pd.DataFrame(columns = nutrients_head+standard_error_columns)
    df_mean = pd.DataFrame(columns = nutrients_head+standard_error_columns)
    change_filename =  f"results_difference_scenario_{scenario}.xlsx"
    mean_filename = f"results_value_scenario_{scenario}.xlsx"

    for condition_list in all_conditions:
        survey_baseline, survey_mean, survey_change =  table_mean_values_subgroup(df_reduced_total=df_reduced_total,
                                                                                      subgroup_conditions = condition_list,
                                                                                      df_baseline_total = df_baseline_total,
                                                                                      nutrients = nutrients,
                                                                                      nutrient_label_dict = nutrient_label_dict,
                                                                                      mean_env_columns=mean_env_columns,
                                                                                      standard_error_dict= standard_error_dict
                                                                                    )

        survey_change.rename(columns={nutr: f"{data['title']}, {data['units']}" for nutr, data in nutrient_label_dict.items() if not nutr.startswith('se_') and nutr in nutrients+mean_env_columns}, inplace=True )
        survey_mean.rename(columns={nutr: f"{data['title']}, {data['units']}" for nutr, data in nutrient_label_dict.items() if not nutr.startswith('se_') and nutr in nutrients+mean_env_columns}, inplace=True )
        for cond_label, _ in condition_list:
          df_change.loc[cond_label, :] = survey_change.loc[cond_label, :].round(2)
          df_mean.loc[cond_label, :] = survey_mean.loc[cond_label, :].round(2)
        
    df_change.to_excel(path_scenario / change_filename, index=True)
    df_mean.to_excel(path_scenario / mean_filename, index=True)


    return


def combine_seeds(reduction_path_scenario: Path,
                  nutrients: list, 
                  mean_env_columns:list,
                  error_columns: list,
                  standard_error_dict: dict,
                  demographic_columns: list):

  df_seeds =[]

  seed_files = [
        f for f in os.listdir(reduction_path_scenario)
        if f.startswith("df_nutrients_seed") and f.endswith(".parquet")
    ]

  for file in seed_files:
    df_scenario_seed = pd.read_parquet(reduction_path_scenario / file)
    df_seeds.append(df_scenario_seed)

  concatenated_df = pd.concat(df_seeds)
  # Calculate the mean and standard deviation for each row index

  del df_seeds
  del seed_files
  gc.collect()

  df_scenario_mean = concatenated_df.groupby(level=0).mean()
  # calculate the standard error on the mean across different seeds
  df_scenario_se = concatenated_df.groupby(level=0).sem()

  # calculate the indiividual level standard errors from the within item variance
  combined_se_df = pd.DataFrame(index=df_scenario_mean.index)
  for col in error_columns:
      se_scenarios = concatenated_df.groupby(level=0)[col].apply(lambda x: np.sqrt(np.sum(x**2))/len(x))
      combined_se_df[col] = se_scenarios

  del concatenated_df
  gc.collect()

  se_columns = [f"se_{indicator}" for indicator in nutrients + mean_env_columns]
  se_columns_dict = {}
  error_dict = {indicator: error for error, indicator in standard_error_dict.items()}

  for col in nutrients + mean_env_columns:
      se_col_name = f"se_{col}"
      if col in mean_env_columns:
          se_columns_dict[se_col_name] = np.sqrt(combined_se_df[error_dict[col]]**2 + df_scenario_se[col]**2)
      else:
          se_columns_dict[se_col_name] = df_scenario_se[col]

  se_df = pd.DataFrame(se_columns_dict, index=df_scenario_mean.index)
  df_scenario = df_scenario_mean.join(se_df)

  del combined_se_df
  gc.collect()

  return df_scenario
  
def replacement_sim(base_path: str, 
                    scenario: int, 
                    df_baseline: pd.DataFrame, 
                    dairy_sub_mapping: dict,
                    nutrients_per_gram_sub: pd.DataFrame,
                    meat_sub: str,
                    demographic_columns: list, 
                    ccc_scenario_mapping: dict,
                    indicators: list,
                    nutrients: list,
                    mean_env_columns: list,
                    error_columns: list,
                    nutrient_label_dict: dict,
                    standard_error_dict: dict,
                    all_conditions: list,
                    dairy_sub: bool,
                    max_seed: int = 51,
                    max_intake=None, 
                    meat_percent_reduction=None
                    ):

  scenario_file = f'Output/Scenarios/Scenario_{scenario}/'
  path_scenario = base_path / scenario_file
  path_scenario.mkdir(parents=True, exist_ok=True)

  if max_intake is not None:
    reduction_path_scenario = base_path / f'Output/Max_intake/{max_intake}.0_max_reduction20.0_dairy_reduction/nutrient_intake/'
    df_scenario = combine_seeds(reduction_path_scenario = reduction_path_scenario,
                                                  nutrients = nutrients, 
                                                  mean_env_columns = mean_env_columns,
                                                  error_columns=error_columns,
                                                  standard_error_dict=standard_error_dict,
                                                  demographic_columns=demographic_columns 
                                                  )
    # Add the demographic variables back in which were removed upon taking the average over simulation iterations
    df_scenario[demographic_columns] = df_baseline[demographic_columns].copy()
                                                  
  elif meat_percent_reduction is not None:
    baseline_scenario = ccc_scenario_mapping[meat_percent_reduction]
    df_scenario = pd.read_parquet(base_path / f"Output/Scenarios/Scenario_{baseline_scenario}/df_scenario{baseline_scenario}.parquet")
    error_columns_to_add = [f"se_{col}" for col in nutrients + mean_env_columns]
    df_scenario.loc[:, error_columns_to_add] = 0
    dem_cols_to_add = [col for col in demographic_columns if col not in df_scenario.columns and col in df_baseline.columns]
    if len(dem_cols_to_add) > 0:
        df_scenario.loc[:, dem_cols_to_add] = df_baseline.loc[:, dem_cols_to_add]
    
  else:
    raise ValueError("Either max_intake or meat_percent_reduction must be provided.")
    
  nutrients_head = [f"{data['title']}, {data['units']}" for nutr, data in nutrient_label_dict.items() if not nutr.startswith('se_') and nutr in nutrients+mean_env_columns]
  # For those variabes that do not have an uncertainty estimate include additional columns for the associated standard errors
  standard_error_columns = [f"se_{nutr}" for nutr in nutrient_label_dict.keys() if not nutr.startswith('se') and nutr in nutrients+mean_env_columns]

  if 'All meat' not in df_scenario.columns:
        df_scenario['All meat'] = df_scenario[all_meat_food_groups].sum(axis=1)

  df_scenario['Total RRPM baseline'] = df_baseline['Total RRPM baseline'].copy()
  df_scenario['All meat reduction'] = (df_baseline['All meat'] - df_scenario['All meat']).copy()
  df_scenario['RRPM reduction'] = (df_baseline['Total RRPM baseline'] - df_scenario['Total RRPM meat']).copy()
  
  # The dairy reduction is the same for all scenarios. Take one scenario with the dairy reduction for the item level gram weight of the reduction
  diet_data_dairy_reduced = pd.read_parquet(base_path /  f'Output/Max_intake/70.0_max_reduction20.0_dairy_reduction/nutrient_intake/diet_data_seed_0.parquet')

  if dairy_sub:
    for FG, replacement in dairy_sub_mapping.items():
      df_scenario = df_scenario.apply(lambda row: food_group_substitution_per_gram(row,
                                                                          food_group=FG,
                                                                          substitute=replacement,
                                                                          diet_data_reduced=diet_data_dairy_reduced,
                                                                          nutrients_per_gram_sub=nutrients_per_gram_sub,
                                                                          indicators=indicators,
                                                                          error_columns=error_columns),
                                      axis=1)

  if meat_sub is not None:
    if max_intake is not None:
     df_scenario = df_scenario.apply(lambda row: food_group_substitution_per_gram_ind_level(row, food_group='RRPM',
                                                                                    substitute=meat_sub,
                                                                                    nutrients_per_gram_sub=nutrients_per_gram_sub,
                                                                                    indicators=indicators,
                                                                                    error_columns=error_columns), axis=1)
    elif meat_percent_reduction is not None:
      df_scenario = df_scenario.apply(lambda row: food_group_substitution_per_gram_ind_level(row, food_group='All meat',
                                                                                    substitute=meat_sub,
                                                                                    nutrients_per_gram_sub=nutrients_per_gram_sub,
                                                                                    indicators=indicators,
                                                                                    error_columns=error_columns), axis=1)
      

  
  df_scenario.to_parquet(path_scenario / f'df_scenario{scenario}.parquet')

  results_table(path_scenario=path_scenario, 
                  all_conditions=all_conditions, 
                  df_reduced_total=df_scenario, 
                  df_baseline_total=df_baseline, 
                  nutrient_label_dict=nutrient_label_dict, 
                  nutrients= nutrients,
                  mean_env_columns = mean_env_columns,
                  scenario = scenario,
                  error_columns=error_columns,
                  standard_error_dict=standard_error_dict
                  )
  
  print(f"Finished scenario {scenario}")

  return




