import pandas as pd
import numpy as np
import regex as re
import operator

def price_variable(row, metric):

  price = row[f'{metric}_price_2022']
  if pd.isnull(price):
    price = row[f'{metric}_price_2021']
    if pd.isnull(price):
      price = row[f'{metric}_price_2019']
  else:
    pass

  return price

def price_error(row):

  price = row[f'sd_price_2022']
  if pd.isnull(price):
    price = row[f'sd_price_2021']
    if pd.isnull(price):
      price = row[f'sd_price_2019']
  else:
    pass

  return price

def add_env_data(row: pd.Series,
                      NDB_data: pd.DataFrame,
                      df_impacts: pd.DataFrame,
                      mean_env_columns: list,
                      error_columns: list,
                      conversion_dict: dict,
                      ):

  food_code = row['FoodNumber']
  food_desc = row['FoodDescription']

  # Try assigning the impacts to be those with the same item desription
  try:
      impacts_result = df_impacts.loc[food_desc, :]
      if isinstance(impacts_result, pd.Series):
          # If it's a Series, it means a unique match for the food description.
          # We should directly use its values for the relevant columns.
          mean_impacts = impacts_result[mean_env_columns]
          error_impacts = impacts_result[error_columns]
      elif isinstance(impacts_result, pd.DataFrame):
          # If it's a DataFrame, it means multiple matches, take mean across rows.
          mean_impacts = impacts_result[mean_env_columns].mean(skipna=True)
          error_impacts = ((impacts_result[error_columns]**2).sum(skipna=True))**0.5/len(impacts_result)
      else:
          # This case should ideally not happen if df_impacts is well-formed
          raise TypeError(f"Unexpected type for impacts_result: {type(impacts_result)}")

  # Otherwise assign the impacts to those of the items that share a food code wth the item description
  except KeyError:
       ndb_items = list(NDB_data[NDB_data['Food composition record ID']==food_code]['Local description'])
       impacts_from_ndb = df_impacts[df_impacts.index.isin(ndb_items)]
       mean_impacts = impacts_from_ndb[mean_env_columns].mean(skipna=True)
       error_impacts = ((impacts_from_ndb[error_columns]**2).sum(skipna=True))**0.5/len(ndb_items)

  # if the food item is an item that does not account for diluted water seperately
  if food_desc in conversion_dict.keys():
    conversion_factor = conversion_dict[food_desc]

    row[mean_env_columns] = (mean_impacts/100)*row['TotalGrams']*conversion_factor
    row[error_columns] = (error_impacts/100)*row['TotalGrams']*conversion_factor

    # Include the water use from the remaining gram weight of the converted item and convert to litres
    row['median_WaterUse'] += (1-conversion_factor)*row['TotalGrams']*0.001
    row['mean_WaterUse'] += (1- conversion_factor)*row['TotalGrams']*0.001
  else:
    # add the impacts of each item weighted by consumption
    row[mean_env_columns] = (mean_impacts/100)*row['TotalGrams'] ## impact is per 100g
    row[error_columns] = (error_impacts/100)*row['TotalGrams']

  return row


def add_sw(row:pd.Series, ind_data:pd.DataFrame):

  id = row['Cpseriala']
  SW = ind_data[ind_data['Cpseriala']==id]['SHeS_Intake24_wt_sc'].iloc[0]

  return SW


########################## Dairy disaggregation #########################################

def dairy_intake_diet_data(row, category, diet_data, dairy_per100g, dairy_codes):

  # Reassign two food codes that appear in SHeS 2021 but are not included in the NDB. 10159 corresponds to "Oat Milk" and 821 to either "Savoury pastry (e.g. cheese pastry)" or "Cheese and onion pasty/roll (includes potato)"
  SHeS_item_map = {10966: 10159,
                       356: 821}

  food_code = row['FoodNumber']

  if food_code in SHeS_item_map.keys():
    food_code = SHeS_item_map[food_code]

  item_total = row['TotalGrams']
  # Some items have the same food code with identical nutritional data. In this case so take the nutritional data from the first row
  item = dairy_per100g[dairy_per100g['FoodNumber']==food_code].iloc[0, :]

  row[category] = (item[category]/100)*item_total

  return row

def unique_mixed_items_dairy(variable: str, dairy_disag_data: pd.DataFrame):

  """
  param: variable: disaggregated dairy food group, e.g. "Milk_SemiSkimmed"
  param: dairy_disag_data: Dataset containing the disaggregated dairy content for each dairy food group per 100g of all items in NDB 2022
  return: Two lists of composite and non-composite food codes that contain the dairy food group variable.

  """

  columns = ['FoodNumber', 'FoodDescription_SHeS', variable, 'Dairy']

  # food_items are the ingredients per 100g of the food item

  df = dairy_disag_data[columns]

  # Ensures that the assignment is robust against numerical estimatation issues
  tolerance = 0.000001
  item_only_cond = (100/df[variable] >= 1 - tolerance) & (100/df[variable] <= 1 + tolerance)

  item_only = df[item_only_cond]
  mixed_dish_with_item = df[(df[variable]>0) & (~item_only_cond)]

  mixed_items = mixed_dish_with_item['FoodNumber'].unique().tolist()
  unique_items = item_only['FoodNumber'].unique().tolist()

  return unique_items, mixed_items


def initialise_dairy_mapping(food_groups: list):

    """
    variable food groups: list of food groups to inclde in the mapping
    return: empty dictionary in the required format for mapping to composite and non-cmposite food codes in each food group
    """

    dairy_mapping = {}

    for fg in food_groups:
        item_mapping = {'items_mixed': [], 'items_only': []}
        dairy_mapping[fg] = item_mapping

    return dairy_mapping


def complete_dairy_mapping(dairy_map: dict, dairy_disag_data: pd.DataFrame):

  """
  param: dairy_map: dictionary initialised by the fucniton initialise_dairy_mapping()
  param: dairy_disag_data: Dataset containing the disaggregated dairy content for each dairy food group per 100g of all items in NDB 2022
  return: dairy_mapping: dictionary mapping each dairy food group to a list of non-composite and composite food codes that contain the dairy group

  """

  dairy_mapping = dairy_map.copy()

  for food_group in dairy_mapping.keys():
    item_only, item_mixed = unique_mixed_items_dairy(variable=food_group, dairy_disag_data=dairy_disag_data)
    dairy_mapping[food_group]['items_only'] += item_only
    dairy_mapping[food_group]['items_mixed'] += item_mixed

  return dairy_mapping

def initialise_dairy_mapping_dictionary(dairy_categories: list, dairy_mapping: dict, recipe_data: pd.DataFrame):

  """
  param: dairy_categories: list of the non-composite dairy food groups
  param: dairy_mapping: disctionary mapping dairy food categories to a list of composite ('items_only') and non-composite ('items_mixed') items that contain that dairy category
  param: recipe_data: FSA recipe database
  return: mapping_dict_dairy: Nested dictionary, with each key corresponding to all food groups in dairy_categories. The dictionary for each food group maps each food code of a composte item that contains a non-zero quantity of the dairy food group to a list of non-compoiste ingredients within that dairy food group. 
    
  """
        
  mapping_dict_dairy = {}
  for dairy_group in dairy_categories:

    possible_codes = dairy_mapping[dairy_group]['items_only']
    
    dairy_group_dictionary = {}
    for code in dairy_mapping[dairy_group]['items_mixed']:
      #Exctract the ingredients of the mixed item from the code
      item_recipe = recipe_data[recipe_data['L0FoodCode']==code]
      # Extract the list of 100% dairy items from the appropriate food group
      list_dairy_items = item_recipe[item_recipe['IFoodCode'].isin(possible_codes)]['IFoodCode'].unique().tolist()

      if len(list_dairy_items)>0:
        dairy_group_dictionary[code] = list_dairy_items

    mapping_dict_dairy[dairy_group]=dairy_group_dictionary

  return mapping_dict_dairy

def initialise_ingredient_proportion(ingredient_dict: dict):

  proportion_ing_dict = {}

  for key, ing_mapping in ingredient_dict.items():
    proportion_ing_dict[key] = {ing: {} for ing in ing_mapping.keys()}

  return proportion_ing_dict


def ingredient_weighting_item(composite_FC, ingredient_list, recipe_data):

  ingredient_weights = {}

  item = recipe_data[recipe_data['L0FoodCode']==composite_FC]
  total = 0


  # Ingredients ordered into 5 layers of disaggregation in the recipe database. This loop uses the mapping from composite food code to dairy ingredient food code to identify the quantiy of that dairy ingredient in the recipe data.
  for ing in ingredient_list:
    for ing_level in range(1, 5):
      matching_ingredient = item[item[f"L{ing_level}FoodCode"]==ing]
      if not matching_ingredient.empty:
        weight = float(matching_ingredient[f"L{ing_level}ComponentAmount"].iloc[0]) ## Some ingredients are listed
        total += weight
        ingredient_weights[ing] = weight

  ingredient_weights_ratio = {ing: np.round(weight/total, 3) for ing, weight in ingredient_weights.items()}

  return ingredient_weights_ratio


def ingredient_weighting_dict(ingredient_dict: dict, recipe_data: pd.DataFrame):

  proportional_ing_dict = initialise_ingredient_proportion(ingredient_dict=ingredient_dict)

  for food_group, mapping in proportional_ing_dict.items():
    for composite_FC in mapping.keys():
      ingredient_list = ingredient_dict[food_group][composite_FC]
      weights_dict = ingredient_weighting_item(composite_FC=int(composite_FC), ingredient_list=ingredient_list, recipe_data=recipe_data)
      proportional_ing_dict[food_group][composite_FC] = weights_dict

  return proportional_ing_dict

######## Ingredient nutrient and impact data processing #########

def item_only_nutrients(item_only: list, indicators:list, diet_data: pd.DataFrame):

  """
  param item_only: list of non-composite meat or dairy items in a particular food group
  param nutrients: list of indicators to compute per gram
  param diet_data: item level dietary data containing estimates for all indicators

  """

  if not all(col in diet_data.columns for col in indicators):
    raise ValueError("Not all indicators are present in diet data. Check list of indicators, version of the diet data or alternate spelling")

  df = pd.DataFrame(index=item_only, columns=indicators)

  for item in item_only:
    df_item = diet_data[diet_data['FoodDescription']==item][indicators]
    item_mean = df_item.div(df_item['TotalGrams'], axis=0).mean(axis=0)

    df.loc[item, :] = item_mean

  return df

def unique_mixed_items(variable: str, diet_data: pd.DataFrame):

  """
  param: variable:
  return: Two lists of composite and non-composite food descriptions that contain the meat group variable.
  """

  columns = ['FoodNumber', 'FoodDescription', variable, 'TotalGrams']

  df = diet_data[columns]
  item_only_cond = df['TotalGrams']/df[variable]==1
  item_only = df[item_only_cond]
  mixed_dish_with_item = df[(df[variable]>0) & (~item_only_cond)]

  mixed_items = mixed_dish_with_item['FoodDescription'].unique().tolist()
  unique_items = item_only['FoodDescription'].unique().tolist()

  return unique_items, mixed_items
  
def add_env_data_description(row: pd.Series, df_impacts: pd.DataFrame, diet_data: pd.DataFrame, matched_items_data: pd.DataFrame, env_columns: list, mean_env_columns: list, error_columns: list):

  '''
  param row: meat ingredients with each column corresponding to the impacts or nutrients per gram of the meat ingredient
  return row: including the enviornmental impacts and cost per gram of the meat ingredient
  '''

  desc_shes = row.name

  try:
    # If the item description matches that in shes then assign the data to the item
    env_data = df_impacts.loc[desc_shes, :]/100
  except:
    # else extract the food code from SHeS and obtain the item descriptions for that food code in the NDB -> impact assumed to be average of that over all food codes
    food_code = diet_data[diet_data['FoodDescription']==desc_shes]['FoodNumber'].iloc[0]
    descriptions_ndb = matched_items_data[matched_items_data['Food composition record ID']==food_code]['Local description'].tolist()

    if len(descriptions_ndb) ==1:
      env_data_mean = df_impacts.loc[descriptions_ndb, mean_env_columns]/100
      env_data_error = df_impacts.loc[descriptions_ndb, error_columns]/100
    else:
      # In cases where the food code corresponds to multiple iitems with different imapcts, estimate the ipact as the average of the impacts of each item.
      env_data_mean = df_impacts.loc[descriptions_ndb, mean_env_columns]/100
      env_data_mean = env_data_mean.mean(axis=0)

      env_data_error = df_impacts.loc[descriptions_ndb, error_columns]/100
      env_data_error = (env_data_error**2).sum(axis=0)
      env_data_error = np.sqrt(env_data_error)/len(descriptions_ndb)

    env_data = pd.concat([env_data_mean, env_data_error], axis=0)

  try:
    for col in env_columns:
        if isinstance(env_data[col], pd.Series):
            series = env_data[col].copy()
            value = series.dropna().values[0]
            row[col] = value
        else:
            row[col] = env_data[col]
  except:
      print(food_code, descriptions_ndb)

  return row
  
def add_env_data_food_code(row: pd.Series, df_impacts: pd.DataFrame, matched_items_data: pd.DataFrame, env_columns: list ,mean_env_columns: list, error_columns: list):

  '''
  param row: food code with each column corresponding to the impacts or nutrients per gram of the ingredient
  return row: including the enviornmental impact and cost per gram of the ingredient
  '''
  
  #### Food number ####

  food_code = row.name
  #list of items in the NDB corresponding to that food code
  descriptions_ndb = matched_items_data[matched_items_data['Food composition record ID']==food_code]['Local description'].tolist()
  
  env_data_mean = df_impacts.loc[descriptions_ndb, mean_env_columns]/100
  env_data_mean = env_data_mean.mean(axis=0)
  env_data_error = df_impacts.loc[descriptions_ndb, error_columns]/100
  env_data_error = (env_data_error**2).sum(axis=0)
  env_data_error = np.sqrt(env_data_error)/len(descriptions_ndb)
  env_data = pd.concat([env_data_mean, env_data_error], axis=0)
  
  for col in env_columns:
      row[col] = env_data[col]

  return row
  
def item_only_nutrients_dairy(item_codes: list, nutrients: list, ndb_data: pd.DataFrame):
    
    """
    Iinitialises the dataframe of with each rowcorresponding to a non-composite dairy ingredient and the columns indicating teh nutrients per gram of the non-composite dairy ingredient
    """

    df = pd.DataFrame(index=item_codes, columns=nutrients)
    
    for code in item_codes:
        df_item = ndb_data[ndb_data['FCT record ID']==code][nutrients]
        df_item /= 100
        item_mean = df_item.mean(axis=0)
        df.loc[code, :] = item_mean
    
    return df
    
def add_dairy_ndb(row: pd.Series, dairy_category: str, dairy_per100g: pd.DataFrame):

  food_code = row["FCT record ID"]

  # some items have the same food code and identical dairy content. Only consider items that contan dairy. 
  if dairy_per100g[dairy_per100g['FoodNumber']==food_code]["Dairy"].mean(axis=0)>0:
    item = dairy_per100g[dairy_per100g['FoodNumber']==food_code].iloc[0, :]
    row[dairy_category]=item[dairy_category]
  else:
    pass

  return row

################# Baseline indicators #######################

# define a function to convert a string to a float if it contains a float
def convert_to_float(s):
    pattern = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
    if pattern.match(s):
        return float(s)
    else:
        return s

#from pandas.core.groupby.ops import Int64Dtype
def add_variable(row, variable, dem_data):

    id = float(row.name)
    ind = dem_data[dem_data['Cpseriala']==id]
    value = ind[variable].values[0]

    if variable == 'SIMD20_RPa' or variable == 'Ethnic05':
      value = str(value)
    else:

      if value == 'Male':
        value=0
      elif value == 'Female':
        value=1
      elif isinstance(value, str):
        value = convert_to_float(value)
      else:
        pass

      if isinstance(value, str):
        value = np.nan

    return value


def SIMD(df):
    # Creating new columns based on SIMD_labels
  simd_mapping = {
      'Most deprived': ('SIMD1', 1),
      '4th': ('SIMD2', 1),
      '3rd': ('SIMD3', 1),
      '2nd': ('SIMD4', 1),
      'Least deprived': ('SIMD5', 1)
  }

  for new_col in ['SIMD1', 'SIMD2', 'SIMD3', 'SIMD4', 'SIMD5']:
      df[new_col] = 0

  for index, row in df.iterrows():
      label = row['SIMD_labels']
      if label in simd_mapping:
          col, value = simd_mapping[label]
          df.at[index, col] = value

  return df

def Ethnicity(df):

    # Creating new columns based on SIMD_labels
  eth_mapping = {
      'White: Scottish': ('white_scot', 1),
      'White: Other British': ('white_OB', 1),
      'Asian': ('asian', 1),
      'White: Other': ('white_oth', 1),
      'Other minority ethnic': ('oth_min_eth', 1)
  }

  for new_col in ['white_scot', 'white_OB', 'asian', 'white_oth', 'oth_min_eth']:
      df[new_col] = 0

  for index, row in df.iterrows():
      label = row['Ethnicity']
      if label in eth_mapping:
          col, value = eth_mapping[label]
          df.at[index, col] = value

  return df

def add_non_diet_variables(df, dem_data):

  df['Sample Weight'] = df.apply(lambda row: add_variable(row, variable='SHeS_Intake24_wt_sc', dem_data=dem_data), axis=1)
  df['strata'] = df.apply(lambda row: add_variable(row, variable='Strata', dem_data=dem_data), axis=1)
  df['psu'] = df.apply(lambda row: add_variable(row, variable='psu', dem_data=dem_data), axis=1)
  df['age'] = df.apply(lambda row: add_variable(row, variable='age', dem_data=dem_data), axis=1)
  df['Sex'] = df.apply(lambda row: add_variable(row, variable='Sex', dem_data=dem_data), axis=1)

  df['SIMD_labels'] = df.apply(lambda row: add_variable(row, variable='SIMD20_RPa', dem_data=dem_data), axis=1)
  df['Ethnicity'] = df.apply(lambda row: add_variable(row, variable='Ethnic05', dem_data=dem_data), axis=1)
  df['BMI'] = df.apply(lambda row: add_variable(row, variable='bmi_adj', dem_data=dem_data), axis=1)

  df = SIMD(df)
  df = Ethnicity(df)

  return df
  
def nutrient_intake(row: pd.Series, diet_data: pd.DataFrame, nutrients: list, error_columns: list):

    id = float(row.name)
    diet = diet_data[diet_data['Cpseriala'] == id]
    num_days = len(diet['RecallNo'].unique())

    for nutr in nutrients:
        if nutr in error_columns:
            row[nutr] = np.sqrt((diet[nutr] ** 2).sum()) / num_days
        else:
            row[nutr] = float(diet[nutr].sum()) / num_days

    return row
    
def white_processed_meat_consumption(row: pd.Series, diet_data: pd.DataFrame):
    
    """
    Calculates white processed meat consumption at the participant level
    """

    white_offal = ['Chicken and vegetable soup, homemade', 'Chicken liver']
    white_sausage = ['Chicken/turkey sausage']

    id = float(row.name)
    diet = diet_data[diet_data['Cpseriala'] == id]
    num_days = len(diet['RecallNo'].unique())

    white_PM_consumption = 0
    white_PM_consumption += diet[diet['FoodDescription'].isin(white_offal)]['Offalg'].sum() / num_days
    white_PM_consumption += diet[diet['FoodDescription'].isin(white_sausage)]['Sausagesg'].sum() / num_days

    return white_PM_consumption
    
def filter_dataframes(dfs: list, conditions_tuple: tuple):
    """
    Apply multiple filters to a list of DataFrames using a declarative
    operator-based condition structure.

    Parameters:
    dfs (list): List of DataFrames to apply the filters on.
    conditions_tuple (tuple): A tuple containing a description string and a
                              list of condition dictionaries.

    Returns:
    list: List of filtered DataFrames.
    """
    desc, conditions = conditions_tuple

    # If the description is 'Overall' or there are no conditions, return the original list
    if desc == 'Overall' or not conditions or conditions[0].get('column') is None:
        return dfs

    # Define the mapping from string operators to their actual functions
    operator_map = {
        '>=': operator.ge,
        '<=': operator.le,
        '>': operator.gt,
        '<': operator.lt,
        '==': operator.eq,
        '!=': operator.ne
    }

    filtered_dfs = []
    for df in dfs:
        # --- Start building the combined boolean mask for this DataFrame ---

        # 1. Create the initial mask from the *first* condition
        first_cond = conditions[0]
        op_func = operator_map[first_cond['operator']]
        combined_mask = op_func(df[first_cond['column']], first_cond['value'])

        # 2. Loop through the *rest* of the conditions and combine them
        for cond in conditions[1:]:
            op_str = cond['operator']
            col = cond['column']
            val = cond['value']
            boolean_op = cond.get('boolean_operator') # Use .get for safety

            # Create the mask for the current condition
            op_func = operator_map[op_str]
            current_mask = op_func(df[col], val)

            # Combine it with the main mask using the specified boolean operator
            if boolean_op in ('|', 'or'):
                combined_mask |= current_mask
            else:
                # Default to 'and' logic if the operator is '&', None, or anything else
                combined_mask &= current_mask

        # 3. Apply the single, final mask to the DataFrame once
        filtered_dfs.append(df[combined_mask])

    return filtered_dfs
    
# def filter_dataframes(dfs: list, conditions_tuple: tuple):
#     """
#     Apply multiple filters to a list of DataFrames based on given conditions.

#     Parameters:
#     dfs (list): List of DataFrames to apply the filters on.
#     conditions (list): List of dictionaries containing conditions.

#     Returns:
#     list: List of filtered DataFrames.
#     """

#     desc = conditions_tuple[0]
#     conditions = conditions_tuple[1]

#     if desc == 'Overall':
#       return dfs
#     else:
#       filtered_dfs = []
#       for df in dfs:
#           filtered_df = pd.DataFrame()
#           for idx, cond in enumerate(conditions):
#               column = cond['column']
#               condition = cond['condition']
#               boolean_operator = cond['boolean_operator']
#               if idx == 0:
#                   filtered_df = df[df[column].apply(condition)]
#               elif boolean_operator == 'and':
#                   filtered_df = filtered_df[filtered_df[column].apply(condition)]
#               elif boolean_operator == 'or':
#                   filtered_df = pd.concat([filtered_df, df[df[column].apply(condition)]], ignore_index=True).drop_duplicates()

#           filtered_dfs.append(filtered_df)
#       return filtered_dfs
      
      
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

    return se_value

