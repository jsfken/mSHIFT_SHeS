import pandas as pd
import matplotlib.pyplot as plt

# plt.rcParams["font.family"] = 'serif'
# plt.rcParams["mathtext.fontset"] = "cm"
# plt.rcParams["axes.formatter.use_mathtext"] = True


plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
plt.rcParams["mathtext.default"] = "regular"
plt.rcParams["axes.formatter.use_mathtext"] = True

plt.rcParams["font.size"] = 8          
plt.rcParams["axes.labelsize"] = 9    
plt.rcParams["xtick.labelsize"] = 9    
plt.rcParams["ytick.labelsize"] = 9   
plt.rcParams["legend.fontsize"] = 6.5 

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

def item_contribution_nutrients_daily_average(row:pd.Series, 
                                            column_grouping: list, 
                                            diet_data: pd.DataFrame, 
                                            df_baseline: pd.DataFrame,
                                            columns: list):

  """
  Calculate the relative contribution of different food groups to total nutrient intake by taking a weighted average of the relative contribution of different food groups to nutrient intake across all respondents in diet_data.
  
  row: Food group to calculate contribution row, with each column indicating a different nutrient
  column_grouping: The level at which to perform the food grouping. Set to 'FoodCategory' for the highest level categorisation in SHeS. Set to "FoodDescription" will compute the relative                    contribution of individual food items to nutrient intake.
  columns: List of nutrients to calculate the food group contribution for. Default set to all nutrients.
  """

  item = row.name

  consumer_ids = df_baseline.index.to_list()
  df_contribution = pd.DataFrame(index = consumer_ids, columns=columns+['Sample Weight'])
  df_contribution['Sample Weight'] = df_baseline['Sample Weight']

  for id in consumer_ids:
    # Relative contribution of the food group for the individual on each day of recall
    individual_contribution_day = pd.DataFrame(index=['day1', 'day2'], columns = columns)

    # Extract the whole diet, the number of recalls and the reported foods within the food group
    diet = diet_data[diet_data['Cpseriala']==id]
    num_recalls = diet['RecallNo'].max()

    for day in range(1, num_recalls+1):
      diet_day = diet[diet['RecallNo']==day]
      fg_contribution_day = diet_day[diet_day[column_grouping]==item][columns].sum()
      total_contribution_day = diet_day[columns].sum()
      relative_contribution_day = fg_contribution_day / total_contribution_day
      individual_contribution_day.loc[f"day{day}", columns] = relative_contribution_day[columns]

    individual_contribution_average = individual_contribution_day.mean(axis=0, skipna=True)
    df_contribution.loc[id, columns] = individual_contribution_average[columns]

  row[columns] = df_contribution[columns].multiply(df_contribution['Sample Weight'], axis=0).sum() /df_contribution['Sample Weight'].sum()

  return row
  
def item_contribution_nutrients(row:pd.Series, 
                                column_grouping: list, 
                                diet_data: pd.DataFrame, 
                                df_baseline: pd.DataFrame,
                                columns: list):

  """
  Calculate the relative contribution of different food groups to total nutrient intake by taking a weighted average of the relative contribution of different food groups to nutrient intake across all respondents in diet_data.
  
  row: Food group to calculate contribution row, with each column indicating a different nutrient
  column_grouping: The level at which to perform the food grouping. Set to 'FoodCategory' for the highest level categorisation in SHeS. Set to "FoodDescription" will compute the relative                    contribution of individual food items to nutrient intake.
  columns: List of nutrients to calculate the food group contribution for. Default set to all nutrients.
  """

  food_group = row.name

  consumer_ids = df_baseline.index.to_list()
  df_contribution = pd.DataFrame(index = consumer_ids, columns=columns+['Sample Weight'])
  df_contribution['Sample Weight'] = df_baseline['Sample Weight']

  for id in consumer_ids:
    
    # Extract the whole diet, the number of recalls and the reported foods within the food group
    diet = diet_data[diet_data['Cpseriala']==id]
    num_recalls = diet['RecallNo'].max()
    fg_contribution = diet[diet[column_grouping]==food_group][columns].sum()/num_recalls
    total_contribution = diet[columns].sum()/num_recalls
    relative_contribution = fg_contribution / total_contribution
    df_contribution.loc[id, columns] = relative_contribution[columns]

  row[columns] = df_contribution[columns].multiply(df_contribution['Sample Weight'], axis=0).sum() /df_contribution['Sample Weight'].sum()

  return row

def item_contribution_env_impact(row: pd.Series, 
                                 column_grouping: list, 
                                 diet_data: pd.DataFrame, 
                                 columns: list):

  """
  Calculate the relative contribution of each food group to total enviornmental impact by taking the sum of each individuals average environmental impact on each day of recall across all   individuals and dividing by the sum of the environmental indicator across all food groups.
  
  row: Food group to calculate contribution row, with each column indicating a different environmental indicator
  column_grouping: The level at which to perform the food grouping. Set to 'FoodCategory' for the highest level categorisation in SHeS. Set to "FoodDescription" will compute the relative   contribution of individual food items.
  columns: List of indicators to calculate the food group contribution for. Default set to all environmental indicators.

  """

  item = row.name

  consumers = diet_data[diet_data[column_grouping]==item]
  consumer_ids = consumers['Cpseriala'].unique()
  diet_data['Sample Weight scaled'] = diet_data['Sample Weight']*1325.319

  for id in consumer_ids:
    diet = diet_data[diet_data['Cpseriala']==id]
    num_recalls = diet['RecallNo'].max()
    fg_contribution = diet[diet[column_grouping]==item]

    if len(fg_contribution) > 0:
      env_impact = (fg_contribution[columns]*(fg_contribution['Sample Weight scaled'].iloc[0])).sum()
      env_impact /= num_recalls
      row[columns] += env_impact

    else:
      pass

  return row
  
def stacked_bar_plot(env_columns: list, 
                     nutrients: list, 
                     main_category_sums: pd.DataFrame, 
                     plot_name: str, 
                     nutrient_label_dict: dict, 
                     save_fig: bool, 
                     save_path: str,
                     columns_to_group=[]):

  rename_dict = {'median_Eut': 'Eutrophication',
               'median_GHG': "Greenhouse gas emissions",
               'median_Land': "Land use",
               'median_WaterUse': 'Water use',
               'median_price_sim': 'Cost'}

  category_sums = main_category_sums[env_columns]
  category_sums = category_sums.drop(labels=['Toddler foods', 'Artificial sweeteners'], axis=0)

  category_sums_nutrients = main_category_sums[nutrients]
  category_sums_nutrients = category_sums_nutrients.drop(labels=['Toddler foods', 'Artificial sweeteners'], axis=0)

  total_contribution_map = {var: category_sums[var].sum() for var in env_columns}
  prop_contribution_map = {var: category_sums[var]/total_contribution_map[var] for var in env_columns}

  for var in env_columns:
    category_sums[f"{var}"] = prop_contribution_map[var]

  category_sums = pd.concat([category_sums[env_columns], category_sums_nutrients[nutrients]], axis=1)

  if len(columns_to_group) > 1:
    category_sums.loc['Other food groups', :] = category_sums[category_sums.index.isin(columns_to_group)].sum()
    category_sums = category_sums.drop(labels=columns_to_group, axis=0)

  columns_to_plot = [f'{var}' for var in env_columns] + nutrients
  plot_data = category_sums[columns_to_plot].T

  sorted_columns = category_sums.sort_index().index
  sorted_plot_data = plot_data

  for ind in sorted_plot_data.index:
    if ind in env_columns:
      sorted_plot_data = sorted_plot_data.rename(index={ind: rename_dict[ind]})
    else:
      sorted_plot_data = sorted_plot_data.rename(index={ind: nutrient_label_dict[ind]['title']})

  colors = plt.get_cmap('tab20').colors[3:20]

  # Option to manually reset colors for different food groups
  # colour_map = {'Meat and Meat Products': colors[0],
  #               'Milk and Milk Products': colors[3],
  #               'Other food groups': colors[10],
  #               'Non-alcoholic beverages': colors[4],
  #               'Cereals and Cereal Products': colors[2],
  #               'Sandwiches': colors[1],
  #               'Savoury Snacks': colors[5],
  #               'Fish and Fish Dishes': colors[6],
  #               'Alcoholic beverages': colors[7],
  #               'Eggs and Egg Dishes': colors[9],
  #               }

  sorted_plot_data.plot(kind='barh', stacked=True, color=colors, figsize=(7.08661,4.5))
  ax = plt.gca()

  handles, labels = ax.get_legend_handles_labels()

  #Reverse the order
  handles = handles[::-1]
  labels = labels[::-1]
  # Creating the legend with the reversed order
  ax.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')

  plt.xticks()
  plt.yticks()
  plt.xlim(0,1.01)

  plt.xlabel('Proportion of total daily contribution')
  plt.tight_layout()

  if save_fig:
    plt.savefig(save_path / f'{plot_name}.pdf', dpi=600)

  plt.show()

  return