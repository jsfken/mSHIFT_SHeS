import pandas as pd
import numpy as np
from data_processing import nutrient_intake
from pathlib import Path

def new_diet_data(row: pd.Series,
                  food_groups_to_reduce: list,
                  nutrients: list,
                  df_nutrients: pd.DataFrame,
                  mapping_dict: dict,
                  error_columns: list,
                  dairy_ingredient_proportion_dict: dict,
                  items_to_ignore=[]):
    """
    Function that takes in the diet data with the required reductions in FOODGROUP_reductions column
    and uses that data to compute the change in nutrients based on ingredients and nutrients per gram of that ingredient

    """

    for variable in food_groups_to_reduce:
        if row[variable + '_reduction'] > 0:
            reduction = row[variable + '_reduction']
            desc = row['FoodDescription']
            food_code = row['FoodNumber']

            # Do not include the reduction in nutrients from a list if items to ignore.

            if desc not in items_to_ignore:
                # check whether the reductions are being applied to the dairy or meat food groups
                if 'Milk_Skimmed' in mapping_dict.keys():
                    item_mapping = mapping_dict[variable]
                    # check whether the dairy food code is a composite ingredient and if so, extract the list of ingredient food codes
                    if food_code not in df_nutrients.index:
                        ing_list = item_mapping[str(food_code)]
                    elif food_code in df_nutrients.index:
                        ing_list = [food_code]
                    else:
                        raise ValueError('Reported food code does not have ingredient data')

                    for nutr in nutrients:
                        # Combine the standard errors in such a way that
                        if nutr in error_columns:
                            total = 0
                            for ing in ing_list:
                                # can be multiple ingredients per dairy food group. Equally space the reduction among all ingredients per item

                                if len(ing_list) > 1:
                                    total += (reduction * df_nutrients.loc[ing, nutr] * dairy_ingredient_proportion_dict[variable][str(food_code)][str(ing)]) ** 2
                                else:
                                    total += (reduction * df_nutrients.loc[ing, nutr]) ** 2

                            # Standard error on A - B: (\alpha_A**2 + \alpha_B**2)**0.5
                            row[nutr] = np.sqrt(total + row[nutr] ** 2)

                        else:
                            for ing in ing_list:
                                # can be multiple ingredients per dairy food group. Equally space the reduction among all ingredients per item

                                if len(ing_list) > 1:
                                    row[nutr] -= reduction * df_nutrients.loc[ing, nutr] * dairy_ingredient_proportion_dict[variable][str(food_code)][str(ing)]
                                else:
                                    row[nutr] -= reduction * df_nutrients.loc[ing, nutr]

                            # If the reduction in nutrients exceeds the total nutrient count, set to zero. Can occur due to the approximation in meat mapping
                            if row[nutr] < 0:
                                row[nutr] = 0

                # should refer to meat
                elif 'Beefg' in mapping_dict.keys():
                    # no nearest neighbour matches for offal items. As an approx use the gram weight reduction in offal to reduce the gram weight of the whole item by that gram weight.
                    if variable == "Offalg":

                        # calculate nutrients per gram of whole item consumed
                        nutr_per_gram_offal_item = row[nutrients] / row['TotalGrams']
                        # For each nutrient take off the associated nutrients from the gram weight of the reduction
                        for nutr in nutrients:
                            if nutr in error_columns:
                                # Combined error of the original nutrient intake and that of the reduction
                                row[nutr] = np.sqrt(
                                    row[nutr] ** 2 + (row["Offalg_reduction"] * nutr_per_gram_offal_item[nutr]) ** 2)
                            else:
                                row[nutr] -= row["Offalg_reduction"] * nutr_per_gram_offal_item[nutr]
                    else:
                        item_mapping = mapping_dict[variable]
                        try:
                            nn = item_mapping[desc]
                        except:
                            nn = desc

                        for nutr in nutrients:
                            if nutr in error_columns:
                                row[nutr] = np.sqrt(row[nutr] ** 2 + (reduction * df_nutrients.loc[nn, nutr]) ** 2)
                            else:
                                row[nutr] -= reduction * df_nutrients.loc[nn, nutr]
                            # If the reduction in nutrients exceeds the total nutrient count, set to zero. Can occur due to the approximation in meat mapping
                            if row[nutr] < 0:
                                row[nutr] = 0
                else:
                    raise ValueError('No composite or ingredient item exists -> check the mapping dictionary')

                if row[variable] < 0:
                    raise ValueError('Magnitude of the reduction cannot be greater than that currently consumed')
        else:
            pass

    return row
    
def apply_reductions_env_data(diet_data: pd.DataFrame, 
                                RRPM_alone: bool, 
                                env_columns: list, 
                                error_columns: list, 
                                food_groups_dairy: list, 
                                nutrients_per_gram_meat: pd.DataFrame,                                           nutrients_per_gram_dairy: pd.DataFrame, 
                                meat_mapping_dict: dict, 
                                dairy_mapping_dict: dict, 
                                dairy_ingredient_proportion_dict: dict):

  diet_data_copy = diet_data.copy()
  white_PM_items = ['Chicken and vegetable soup, homemade', 'Chicken liver', 'Chicken/turkey sausage']

  if RRPM_alone:
    items_to_ignore = white_PM_items
    meat_food_groups= ['Beefg',
                'Lambg',
                'Porkg',
                'Burgersg',
                'OtherRedMeatg',
                   'ProcessedRedMeatg',
                 'Sausagesg',
                 'Offalg']
  else:
    meat_food_groups= ['Beefg',
                'Lambg',
                'Porkg',
                'Burgersg',
                'OtherRedMeatg',
                   'ProcessedRedMeatg',
                 'Sausagesg',
                 'Offalg',
                   'Poultryg', 'ProcessedPoultryg', 'GameBirdsg']
    items_to_ignore = []

  # reduce the meat items
  scenario_diet_data = diet_data_copy.apply(
            lambda row: new_diet_data(row,
                                      food_groups_to_reduce=meat_food_groups,
                                      nutrients=env_columns,
                                      df_nutrients=nutrients_per_gram_meat,
                                      items_to_ignore=items_to_ignore,
                                      mapping_dict=meat_mapping_dict,
                                      error_columns = error_columns,
                                      dairy_ingredient_proportion_dict=dairy_ingredient_proportion_dict,
                                      ),
            axis=1)


  # reduce the dairy items
  scenario_diet_data = scenario_diet_data.apply(
            lambda row: new_diet_data(row,
                                      food_groups_to_reduce=food_groups_dairy,
                                      nutrients=env_columns,
                                      df_nutrients=nutrients_per_gram_dairy,
                                      items_to_ignore=items_to_ignore,
                                      mapping_dict=dairy_mapping_dict,
                                      error_columns = error_columns,
                                      dairy_ingredient_proportion_dict = dairy_ingredient_proportion_dict,
                                      ),
            axis=1)

  return scenario_diet_data
  
def include_env_data_ccc( 
                          diet_data_baseline: pd.DataFrame,
                          env_columns: list, 
                          error_columns: list, 
                          food_groups_dairy: list, 
                          nutrients_per_gram_meat: pd.DataFrame, 
                          nutrients_per_gram_dairy: pd.DataFrame, 
                          meat_mapping_dict: dict, 
                          dairy_mapping_dict: dict, 
                          dairy_ingredient_proportion_dict: dict,
                          scenario_path: Path):
                              
  diet_data_scenario = pd.read_parquet(scenario_path / 'diet_data_scenario.parquet')
  # Item-level impacts
  diet_data_scenario[env_columns + ['TotalGrams']] = diet_data_baseline[env_columns + ['TotalGrams']]
  # apply the reductions to the env impact data
  diet_data_scenario = apply_reductions_env_data(diet_data=diet_data_scenario, 
                                                 RRPM_alone=False,
                                                 env_columns= env_columns, 
                                                 error_columns=error_columns, 
                                                 food_groups_dairy = food_groups_dairy, 
                                                 nutrients_per_gram_meat=nutrients_per_gram_meat, 
                                                 nutrients_per_gram_dairy=nutrients_per_gram_dairy, 
                                                 meat_mapping_dict=meat_mapping_dict, 
                                                 dairy_mapping_dict=dairy_mapping_dict, 
                                                 dairy_ingredient_proportion_dict=dairy_ingredient_proportion_dict
                                                  )
  # save the new item level data
  diet_data_scenario.to_parquet(scenario_path / "scenario_diet_data.parquet")

  # Participant level impacts
  df_scenario = pd.read_parquet(scenario_path / 'df_scenario.parquet')
  df_env = pd.DataFrame(index=diet_data_baseline['Cpseriala'].unique(), columns=env_columns)
  df_env = df_env.apply(lambda row: nutrient_intake(row,
                                                  diet_data=diet_data_scenario,
                                                  nutrients=env_columns,
                                                  error_columns=error_columns), 
                        axis=1)
 
  df_scenario[env_columns] = df_env[env_columns]
  # Save the participant level data with impacts
  df_scenario.to_parquet(scenario_path / 'df_scenario.parquet')

  return


def include_env_data_high_consumers(diet_data_baseline: pd.DataFrame,
                                    max_intake: int, 
                                    max_seed: int,
                                    env_columns: list, 
                                    error_columns: list, 
                                    food_groups_dairy: list, 
                                    nutrients_per_gram_meat: pd.DataFrame, 
                                    nutrients_per_gram_dairy: pd.DataFrame, 
                                    meat_mapping_dict: dict, 
                                    dairy_mapping_dict: dict, 
                                    dairy_ingredient_proportion_dict: dict,
                                    path_scenario: Path):

  """
  Incorporates item level environmental impact data for each reduction scenario of reducing red and red processed meat in high consuemrs.

  max_intake: max daily intake of red meat. Either one of 70, 60 or 31.
  RRPM_alone: Specify whether to apply the reduction to red and red processed meat alone. For all high consumer scenarios should be set to TRUE
  Column subset: list of columns where the simulation will be applied

  """

  for seed in range(0, max_seed):
    diet_data = pd.read_parquet(path_scenario / f'diet_data_seed_{seed}.parquet')
    # include the baseline environmental impact data
    diet_data[env_columns + ['TotalGrams']] = diet_data_baseline[env_columns + ['TotalGrams']]
    # apply the reductions to the env impact data
    scenario_diet_data = apply_reductions_env_data(diet_data=diet_data,
                                                    RRPM_alone=True, 
                                                    env_columns= env_columns, 
                                                    error_columns=error_columns, 
                                                    food_groups_dairy = food_groups_dairy, 
                                                    nutrients_per_gram_meat=nutrients_per_gram_meat, 
                                                    nutrients_per_gram_dairy=nutrients_per_gram_dairy, 
                                                    meat_mapping_dict=meat_mapping_dict, 
                                                    dairy_mapping_dict=dairy_mapping_dict, 
                                                    dairy_ingredient_proportion_dict=dairy_ingredient_proportion_dict)
    # save the new diet data with env impacts
    scenario_diet_data.to_parquet(path_scenario / f'diet_data_seed_{seed}.parquet')
    df_scenario = pd.read_parquet(path_scenario / f'df_nutrients_seed_{seed}.parquet')

    df_env = pd.DataFrame(index=diet_data_baseline['Cpseriala'].unique(), columns=env_columns)
    df_env = df_env.apply(lambda row: nutrient_intake(row,
                                                    diet_data=scenario_diet_data,
                                                    nutrients=env_columns,
                                                    error_columns=error_columns),
                  axis=1)

    df_scenario[env_columns] = df_env[env_columns]

    df_scenario.to_parquet(path_scenario / f'df_nutrients_seed_{seed}.parquet')
    print(f'finished seed {seed}')

  return