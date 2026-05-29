import pandas as pd
import numpy as np

def item_only_nutrients(item_only: str, nutrients: list, diet_data: pd.DataFrame):

  df = pd.DataFrame(index=item_only, columns=nutrients)

  for item in item_only:
    df_item = diet_data[diet_data['FoodDescription']==item][nutrients]
    item_mean = df_item.div(df_item['TotalGrams'], axis=0).mean(axis=0)
    df.loc[item, :] = item_mean

  return df

def weighted_consumption(item: str, item_list: list, diet_data: pd.DataFrame):

  if item not in item_list:
    raise ValueError('string item must be in list item_list')

  total = diet_data[diet_data['FoodDescription'].isin(item_list)]['Sample Weight'].sum()
  item_consump = diet_data[diet_data['FoodDescription']==item]['Sample Weight'].sum()
  weighted_consumption = float(item_consump/total)*100

  return weighted_consumption

def daily_consumption_dict(item_list: list, diet_data: pd.DataFrame):

  consumption_dict = {}
  
  ## total population of those that consumed the items in food_list
  total = 0
  for item in item_list:
     consumption_dict[item] = weighted_consumption(item=item, item_list=item_list, diet_data=diet_data)

  return consumption_dict

def unique_mixed_items(variable: str, diet_data: pd.DataFrame):

  columns = ['FoodNumber', 'FoodDescription', variable, 'TotalGrams']

  df = diet_data[columns]
  item_only_cond = df['TotalGrams']/df[variable]==1
  item_only = df[item_only_cond]
  mixed_dish_with_item = df[(df[variable]>0) & (~item_only_cond)]
  mixed_items = mixed_dish_with_item['FoodDescription'].unique().tolist()
  unique_items = item_only['FoodDescription'].unique().tolist()

  return unique_items, mixed_items
  
  
def add_weighted_composite(description: str, 
                    nutrients_per_gram_sub: pd.DataFrame, 
                    diet_data: pd.DataFrame, 
                    replacement_dict_weights: dict, 
                    indicators: list,
                    error_columns: list):
                        
    items = list(replacement_dict_weights.keys())
    weights = list(replacement_dict_weights.values())

    for item in items:
        item_consumption = diet_data[diet_data['FoodDescription'] == item][indicators]
        nutr_per_gram = item_consumption.div(item_consumption['TotalGrams'], axis=0)
        nutrients_per_gram_sub.loc[item] = nutr_per_gram.mean()

    item_data = nutrients_per_gram_sub.loc[items]
    weighted_avg = np.zeros(item_data.shape[1])

    for i, col in enumerate(item_data.columns):
        col_data = item_data[col]
        nan_mask = ~col_data.isna()

        filtered_col_data = col_data[nan_mask]
        filtered_items = filtered_col_data.index

        filtered_weight_dict = {item: weight for item, weight in replacement_dict_weights.items() if item in filtered_items}
        filtered_weights = np.array(list(filtered_weight_dict.values()))

        if len(filtered_col_data) > 0:
            if col in error_columns:
                variances = nutrients_per_gram_sub.loc[filtered_items, col] ** 2
                weighted_variances = variances * (filtered_weights ** 2)
                combined_weighted_variance = weighted_variances.sum() / (filtered_weights.sum() ** 2)
                combined_standard_error = np.sqrt(combined_weighted_variance)
                weighted_avg[i] = combined_standard_error
            else:
                weighted_avg[i] = np.average(nutrients_per_gram_sub.loc[filtered_items, col], axis=0, weights=filtered_weights)
        else:
            weighted_avg[i] = np.nan

    nutrients_per_gram_sub.loc[description] = weighted_avg

    return nutrients_per_gram_sub