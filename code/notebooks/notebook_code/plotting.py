import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from data_processing import filter_dataframes



# plt.rcParams["font.family"] = 'serif'
# plt.rcParams["mathtext.fontset"] = "cm"
# plt.rcParams["axes.formatter.use_mathtext"] = True

# 1. Set the overall font family to sans-serif
plt.rcParams["font.family"] = "sans-serif"

# 2. Prioritize Arial, then Helvetica, falling back to DejaVu Sans if neither is found
plt.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]

# 3. Force math text (like subscripts and equations) to use the regular sans-serif font
plt.rcParams["mathtext.default"] = "regular"

# 4. Keep this to allow math text formatting on your axes
plt.rcParams["axes.formatter.use_mathtext"] = True

# Ensures text in pdfs is editable
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

plt.rcParams["font.size"] = 8          
plt.rcParams["axes.labelsize"] = 12    
plt.rcParams["xtick.labelsize"] = 9    
plt.rcParams["ytick.labelsize"] = 9   
plt.rcParams["legend.fontsize"] = 10  

def compute_plot_data(indicator: str, dem_group: str, path_to_results: str, nutrient_label_dict: dict, mean_env_columns: list):

    df_change = pd.DataFrame(index=['change', 'lower error', 'upper error'], columns=range(1, 34))
    
    for scenario in range(1, 36):
        df = pd.read_excel(path_to_results / f'Scenario_{scenario}/results_difference_scenario_{scenario}.xlsx')
        df = df.set_index('Unnamed: 0')
        try:
          column_name = nutrient_label_dict[f'{indicator}']['title'] + ', ' + nutrient_label_dict[f'{indicator}']['units']
          change = df.loc[dem_group, column_name]

        except KeyError:
          column_name = nutrient_label_dict[f'{indicator}']['title'] + ', '
          change = df.loc[dem_group, column_name]

        df_change.loc['change', scenario] = change

        # indicator_error = None
        # if indicator in mean_env_columns:
        #   # includes uncertainty from both the survey and the uncertainty on the impacts in the mapping
        #   if 'price' in indicator:
        #     error_column_name = 'Price se sim, p'
        #   else:
        #     error_column_name = nutrient_label_dict[f"sd_{indicator}"]['title'] + ', ' + nutrient_label_dict[f'{indicator}']['units']
        # else:
        #   error_column_name =  f"survey_se_{indicator}"

        error_column_name = f"se_{indicator}"
        se_indicator = df.loc[dem_group, error_column_name]

        df_change.loc['lower error', scenario] = change - 1.96*se_indicator
        df_change.loc['upper error', scenario] = change + 1.96*se_indicator

    return df_change
    
def plot_change_impact(indicator: str, 
                       dem_group: str, 
                       path_to_results: str,  
                       nutrient_label_dict: dict,
                       plot_indicator_dict: dict, 
                       mean_env_columns: list,
                       save_path: str = "",
                       title_pad=0, 
                       legend_position=(1, 0.3), 
                       save_fig=False,
                       ):
                           
    df_change = compute_plot_data(indicator=indicator, dem_group=dem_group, path_to_results=path_to_results, nutrient_label_dict=nutrient_label_dict, mean_env_columns = mean_env_columns)

    colors = ["#332288", "#117733", "#44AA99", "#88CCEE", "#DDCC77", "#CC6677", "#882255", '#FF9999', '#990000', '#E69F00']
    
    baseline_results = pd.read_excel(path_to_results / 'baseline/results_value_baseline.xlsx')
    baseline_results = baseline_results.set_index('Unnamed: 0')
    try:
      column_name = nutrient_label_dict[f'{indicator}']['title'] + ', ' + nutrient_label_dict[f'{indicator}']['units']
    except KeyError:
      column_name = nutrient_label_dict[f'{indicator}']['title'] + ', '
      
    column_name = nutrient_label_dict[f'{indicator}']['title'] + ', ' + nutrient_label_dict[f'{indicator}']['units']
    baseline_value = baseline_results.loc[dem_group, column_name]

    #aseline_group = filter_dataframes([df_baseline], conditions_tuple = dem_group_dict[dem_group])
    #baseline_value = (baseline_group[0][indicator]*baseline_group[0]['Sample Weight']).sum()/baseline_group[0]['Sample Weight'].sum()

    print(f"Baseline value: {baseline_value}")

    # convert the price variable to pounds
    if "price" in indicator:
        baseline_value /= 100
        df_change /= 100
        baseline_value = np.round(baseline_value, 3)
    else:
        pass

    indicator_values = {
        'No replacement': (df_change[22].iloc[0], df_change[23].iloc[0], df_change[1].iloc[0], df_change[2].iloc[0], df_change[3].iloc[0]),
        'Pulses and legumes': (df_change[24].iloc[0], df_change[25].iloc[0], df_change[4].iloc[0], df_change[5].iloc[0], df_change[6].iloc[0]),
        'Vegetables': (df_change[26].iloc[0], df_change[27].iloc[0], df_change[7].iloc[0], df_change[8].iloc[0], df_change[9].iloc[0]),
        'Eggs': (df_change[28].iloc[0], df_change[29].iloc[0], df_change[10].iloc[0], df_change[11].iloc[0], df_change[12].iloc[0]),
        'Oily fish': (df_change[30].iloc[0], df_change[31].iloc[0], df_change[13].iloc[0], df_change[14].iloc[0], df_change[15].iloc[0]),
        'Plant-based meat alternatives': (df_change[32].iloc[0], df_change[33].iloc[0],df_change[16].iloc[0], df_change[17].iloc[0], df_change[18].iloc[0]),
        'Chicken': (0, 0, df_change[19].iloc[0], df_change[20].iloc[0], df_change[21].iloc[0]),
    }

    indicator_errors = {
        'No replacement': ([df_change[22].iloc[0] - df_change[22].iloc[1], df_change[22].iloc[2] - df_change[22].iloc[0]],
                           [df_change[23].iloc[0] - df_change[23].iloc[1], df_change[23].iloc[2] - df_change[23].iloc[0]],
         [df_change[1].iloc[0] - df_change[1].iloc[1], df_change[1].iloc[2] - df_change[1].iloc[0]],
         [df_change[2].iloc[0] - df_change[2].iloc[1], df_change[2].iloc[2] - df_change[2].iloc[0]],
          [df_change[3].iloc[0] - df_change[3].iloc[1], df_change[3].iloc[2] - df_change[3].iloc[0]]),

        'Pulses and legumes': ([df_change[24].iloc[0] - df_change[24].iloc[1], df_change[24].iloc[2] - df_change[24].iloc[0]],
                           [df_change[25].iloc[0] - df_change[25].iloc[1], df_change[25].iloc[2] - df_change[25].iloc[0]],
            [df_change[4].iloc[0] - df_change[4].iloc[1], df_change[4].iloc[2] - df_change[4].iloc[0]],
         [df_change[5].iloc[0] - df_change[5].iloc[1], df_change[5].iloc[2] - df_change[5].iloc[0]],
          [df_change[6].iloc[0] - df_change[6].iloc[1], df_change[6].iloc[2] - df_change[6].iloc[0]]),

        'Vegetables': ([df_change[26].iloc[0] - df_change[26].iloc[1], df_change[26].iloc[2] - df_change[26].iloc[0]],
                       [df_change[27].iloc[0] - df_change[27].iloc[1], df_change[27].iloc[2] - df_change[27].iloc[0]],
                      [df_change[7].iloc[0] - df_change[7].iloc[1], df_change[7].iloc[2] - df_change[7].iloc[0]],
                        [df_change[8].iloc[0] - df_change[8].iloc[1], df_change[8].iloc[2] - df_change[8].iloc[0]],
                          [df_change[9].iloc[0] - df_change[9].iloc[1], df_change[9].iloc[2] - df_change[9].iloc[0]]),

        'Eggs': ([df_change[28].iloc[0] - df_change[28].iloc[1], df_change[28].iloc[2] - df_change[28].iloc[0]],
                           [df_change[29].iloc[0] - df_change[29].iloc[1], df_change[29].iloc[2] - df_change[29].iloc[0]],
            [df_change[10].iloc[0] - df_change[10].iloc[1], df_change[10].iloc[2] - df_change[10].iloc[0]],
                 [df_change[11].iloc[0] - df_change[11].iloc[1], df_change[11].iloc[2] - df_change[11].iloc[0]],
                  [df_change[12].iloc[0] - df_change[12].iloc[1], df_change[12].iloc[2] - df_change[12].iloc[0]]),

        'Oily fish': ([df_change[30].iloc[0] - df_change[30].iloc[1], df_change[30].iloc[2] - df_change[30].iloc[0]],
                           [df_change[31].iloc[0] - df_change[31].iloc[1], df_change[31].iloc[2] - df_change[31].iloc[0]],
                      [df_change[13].iloc[0] - df_change[13].iloc[1], df_change[13].iloc[2] - df_change[13].iloc[0]],
                      [df_change[14].iloc[0] - df_change[14].iloc[1], df_change[14].iloc[2] - df_change[14].iloc[0]],
                      [df_change[15].iloc[0] - df_change[15].iloc[1], df_change[15].iloc[2] - df_change[15].iloc[0]]),

        'Plant-based meat alternatives': ([df_change[32].iloc[0] - df_change[32].iloc[1], df_change[32].iloc[2] - df_change[32].iloc[0]],
                                          [df_change[33].iloc[0] - df_change[33].iloc[1], df_change[33].iloc[2] - df_change[33].iloc[0]],
            [df_change[16].iloc[0] - df_change[16].iloc[1], df_change[16].iloc[2] - df_change[16].iloc[0]],
                                           [df_change[17].iloc[0] - df_change[17].iloc[1], df_change[17].iloc[2] - df_change[17].iloc[0]],
                                          [df_change[18].iloc[0] - df_change[18].iloc[1], df_change[18].iloc[2] - df_change[18].iloc[0]]),

        'Chicken': ([0,0],
                    [0,0],
            [df_change[19].iloc[0] - df_change[19].iloc[1], df_change[19].iloc[2] - df_change[19].iloc[0]],
                     [df_change[20].iloc[0] - df_change[20].iloc[1], df_change[20].iloc[2] - df_change[20].iloc[0]],
                    [df_change[21].iloc[0] - df_change[21].iloc[1], df_change[21].iloc[2] - df_change[21].iloc[0]]),
    }
    
    dairy_values = {"No replacement": df_change[34].iloc[0],
                    "Plant-based dairy alternatives": df_change[35].iloc[0],
    }
    dairy_errors = {"No replacement": [df_change[34].iloc[0] - df_change[34].iloc[1], df_change[34].iloc[2] - df_change[34].iloc[0]],
                    "Plant-based dairy alternatives": [df_change[35].iloc[0] - df_change[35].iloc[1], df_change[35].iloc[2] - df_change[35].iloc[0]]
    }

    reduction_scenarios = ("CCC 2030", "CCC 2050", "SDG", "Max red meat \n 60g/day", "Max red meat \n 31g/day", "Dairy reduction \n 20%")

    # Plot the meat reduction scenarios first
    x = np.arange(len(reduction_scenarios)-1)  # the label locations
    width = 0.1  # the width of the bars

    fig, ax = plt.subplots(figsize=(7.08661,4.5))
    plt.subplots_adjust(hspace=0.15)

    for index, (attribute, measurement) in enumerate(indicator_values.items()):
        offset = width * index
        color = colors[index % len(colors)]

        lower_errors = [e[0] for e in indicator_errors[attribute]]
        upper_errors = [e[1] for e in indicator_errors[attribute]]
        y_error = [lower_errors, upper_errors]

        rects = ax.bar(x + offset, measurement, width, color=color, bottom=baseline_value, yerr=y_error, capsize=5, label=attribute)

        scen = {0: "CCC20", 1: "CCC35", 2: "HC70", 3: "HC60", 4: "HC31"}
        for i, value in enumerate(measurement):
            LE = np.round(value - lower_errors[i], 2)
            UE = np.round(value + upper_errors[i], 2)
            print(f"{scen[i]}, {attribute}: {np.round(value, 2)} ({LE}, {UE}), percent change: {(value/baseline_value)*100}")

    print("\n")
    
    colors_dairy = [colors[0], colors[-1]]
    
    dairy_x = x[-1] + width * (len(indicator_values) + 6.5)
    dairy_width = width
    for index, (attribute, measurement) in enumerate(dairy_values.items()):
        offset = dairy_width*index
        color = colors_dairy[index]
        y_error = dairy_errors[attribute]
        rects = ax.bar(dairy_x + offset, measurement, dairy_width, color=color, bottom=baseline_value, yerr=[[y_error[0]], [y_error[1]]], capsize=5, label=attribute)
        LE = np.round(measurement - y_error[0], 2)
        UE = np.round(measurement + y_error[1], 2)
        print(f"{attribute}: {measurement} ({LE}, {UE}), percent change: {(measurement/baseline_value)*100} ")
    
    
    group_config = plot_indicator_dict.get(indicator, {}).get(dem_group, {})
    
    y_axis_label = group_config.get('y_axis_label')
    title = group_config.get('title')
    y_lim = group_config.get('y_lim')
    threshold = group_config.get('threshold')
    
    ####### add the comparator line ########

    # if threshold is not None:

    #   if any(i in indicator.lower() for i in ["protein", "zinc", 'selenium']):
    #     plt.axhline(y=plot_indicator_dict[indicator][dem_group]['threshold'], color='red', linestyle='--', label=f"RNI, Men: {plot_indicator_dict[indicator][dem_group]['threshold']} {nutrient_label_dict[indicator]['units']}/day")
    #   else:
    #     plt.axhline(y=plot_indicator_dict[indicator][dem_group]['threshold'], color='red', linestyle='--', label=f"RNI: {plot_indicator_dict[indicator][dem_group]['threshold']} {nutrient_label_dict[indicator]['units']}/day")
        
    #########################################

    linewidth=2
    if "price" in indicator:
        plt.axhline(y=baseline_value, color='black', linestyle='-', linewidth=linewidth, label=f"Baseline: £{np.round(baseline_value, 2)}/day")
    elif 'wateruse' in indicator.lower():
        plt.axhline(y=baseline_value, color='black', linestyle='-', linewidth=linewidth, label=f"Baseline: {np.round(baseline_value, 2)} litres/day")
    elif 'eut' in indicator.lower():
        plt.axhline(y=baseline_value, color='black', linestyle='-', linewidth=linewidth, label=f"Baseline: {np.round(baseline_value, 2)} gPO$_4$e/day")
    else:
        plt.axhline(y=baseline_value, color='black', linestyle='-', linewidth=linewidth, label=f"Baseline: {np.round(baseline_value, 2)} {nutrient_label_dict[indicator]['units']}/day")

    ax.legend(loc='center left', bbox_to_anchor=legend_position)
    ax.set_ylabel(y_axis_label)
    
    xticks = list(x + width * 3) + [dairy_x]
    xtick_labels = list(reduction_scenarios)
    ax.set_xticks(xticks)
    ax.set_xticklabels(list(reduction_scenarios))
    
    if y_lim is None:
        margin = abs(baseline_value)*0.5
        y_lim = [baseline_value - margin, baseline_value + margin] 
    
    yticks = np.arange(y_lim[0], y_lim[1], (y_lim[1] - y_lim[0]) / 30)
    y_ticks = np.round(yticks, 2)
    ax.set_ylim(y_lim[0], y_lim[1])
    ax.grid(True, linestyle='--', linewidth=0.5, axis='y')
    ax.set_axisbelow(True)

    if save_fig:
        plt.subplots_adjust(right=1.05)
        if '/' in dem_group:
            dem_group = dem_group.replace('/', ' per ')
        plt.savefig(save_path / f'{indicator}_{dem_group}.pdf', dpi=600, bbox_inches='tight')


    return