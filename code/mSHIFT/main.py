import pandas as pd
import time
import sys
import json
from utils import *
from population import *
from variable_imputation import *
from mapping_dictionary import meat_mapping_dict
from pathlib import Path 

def run_sim(path_to_df: str,
            seed: int,
            red_meat: bool,
            processed_meat: bool,
            years: int,
            bmi_change: bool,
            max_intake=None,
            percent_reduction=None,
            dairy_reduction=None,
            test_mode=False):
    """

    :param path_to_df: specify file path to baseline data
    :param seed: random seed parameter
    :param red_meat: Apply reduction to red meat food groups
    :param processed_meat: Aply reductions to processed red meat food groups
    :param bmi_change: Boolean, if True the simulation accounts for the associated impact on the decrease in BMI from the change in energy intake. True by default.
    :param years: number of years to run the simulation
    :param max_intake: if not set to None, sets a maximum daily intake of all food groups that are to be reduced
    :param percent_reduction: if not set to None, sets
    :param dairy_reduction:
    :param test_mode:
    :return:
    """

    results_path = Path("results")

    print('\n')
    print('#' * 20)

    if max_intake is not None:
        print(
            f'MAX_INTAKE: {max_intake}g, Random Seed: {seed}, Processed meat: {processed_meat}, Unprocessed red meat: {red_meat}')
        output_directory = results_path / 'Output/Max_intake/'
    elif percent_reduction is not None:
        print(
            f'REDUCTION: {percent_reduction}%, Random Seed: {seed}, Processed meat: {processed_meat}, Red meat: {red_meat}')
        output_directory = results_path / 'Output/Percent_reduction/'
    else:
        raise ValueError('Must either specify a maximum intake of meat or a fixed percentage reduction in meat')

    print(f'DAIRY_REDUCTION: {dairy_reduction}')
    print(f"BMI change: {bmi_change}")
    print('#' * 20)
    print('\n')

    if test_mode:
        output_directory = results_path / 'Output/Tests/'

    if not os.path.exists(output_directory):
        os.makedirs(output_directory, exist_ok=True)

    RM_foods = ['Beefg',
                'Lambg',
                'Porkg',
                'Burgersg',
                'OtherRedMeatg']

    RPM_foods = ['ProcessedRedMeatg',
                 'Sausagesg',
                 'Offalg']

    if red_meat and not processed_meat:
        if max_intake is not None:
            mdir = f'{max_intake}_max_RM_alone'
        elif percent_reduction is not None:
            mdir = f'{percent_reduction}_reduction_RM_alone'

        file_name = f'df_seed_{seed}_RM.parquet'
        food_groups_to_reduce = RM_foods

    elif processed_meat and not red_meat:
        if max_intake is not None:
            mdir = f'{max_intake}_max_PM_alone'
        elif percent_reduction is not None:
            mdir = f'{percent_reduction}_reduction_PM_alone'

        file_name = f'df_seed_{seed}_PM.parquet'
        food_groups_to_reduce = RPM_foods

    elif red_meat and processed_meat:
        if max_intake is not None:
            mdir = f'{max_intake}_max_reduction'
        elif percent_reduction is not None:
            mdir = f'{percent_reduction}_reduction'

        file_name = f'df_seed_{seed}.parquet'
        food_groups_to_reduce = RM_foods + RPM_foods
    else:
        raise ValueError()

    # Ensure simulation output files that also contain reductions in dairy are properly labelled
    if dairy_reduction is not None:
        mdir += f'{dairy_reduction}_dairy_reduction'
    if not bmi_change:
        mdir += '_bmi_const'

    # Test mode -> run the simulation for 50 individuals only
    if test_mode:
        mdir = mdir + '_test/'
    else:
        mdir = mdir + '/'

    path = os.path.join(output_directory, mdir)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    # Initialise the health data
    shes_data = Individual_level_data(path=path_to_df)
    # Impute the missing variables for the health data
    post_samples = shes_data.impute_missing_data(seed=seed)

    # Food groups that were not in in the dataset of nutrients per gram.
    # Need to explicity set these columns to zero ensure simulation runs without an error message as impact on these nutrients is also computed in the output
    missing_food_groups_meat = ['Milk_Skimmed',
                                'Milk_SemiSkimmed', 'Milk_Whole', 'Cheese_Skimmed',
                                'Cheese_SemiSkimmed', 'Cheese_Whole', 'Yogurt_Skimmed',
                                'Yogurt_SemiSkimmed', 'Yogurt_Whole', 'Cream_SemiSkimmed',
                                'Cream_Whole', 'Butter', 'WhiteFishg', 'OilyFishg', 'CannedTunag', 'Shellfishg',
                                'Fruitg', 'DriedFruitg',
                                'FruitJuiceg', 'SmoothieFruitg', 'Tomatoesg', 'TomatoPureeg', 'Brassicaceaeg',
                                'YellowRedGreeng', 'Beansg', 'Nutsg', 'OtherVegg']

    missing_food_groups_dairy = ['WhiteFishg', 'OilyFishg', 'CannedTunag', 'Shellfishg', 'Fruitg', 'DriedFruitg',
                                 'FruitJuiceg', 'SmoothieFruitg', 'Tomatoesg', 'TomatoPureeg', 'Brassicaceaeg',
                                 'YellowRedGreeng', 'Beansg', 'Nutsg', 'OtherVegg']

    food_groups_dairy = ['Milk_Skimmed',
                         'Milk_SemiSkimmed', 'Milk_Whole', 'Cheese_Skimmed',
                         'Cheese_SemiSkimmed', 'Cheese_Whole', 'Yogurt_Skimmed',
                         'Yogurt_SemiSkimmed', 'Yogurt_Whole', 'Cream_SemiSkimmed',
                         'Cream_Whole', 'Butter']

    data_path = Path("data")

    nutrients_per_gram_dairy_meat = pd.read_parquet(data_path / 'nutrients_per_gram_dairy.parquet')
    nutrients_per_gram_meat = pd.read_parquet(data_path / 'nutrients_per_gram_meat.parquet')
    # Baseline nutrient intake for each individual in SHeS
    df_baseline = pd.read_parquet(data_path / 'df_baseline.parquet')

    #nutrients_per_gram_meat.loc[:, missing_food_groups_meat] = 0
    #nutrients_per_gram_dairy_meat.loc[:, missing_food_groups_dairy] = 0
    nutrients_per_gram_meat[missing_food_groups_meat] = 0
    nutrients_per_gram_dairy_meat[missing_food_groups_dairy] = 0

    # Load the item level diet data
    item_level_data = Food_item_level_data(path=data_path / 'diet_data.parquet')

    nutrient_path = os.path.join(path, 'nutrient_intake/')
    if not os.path.exists(nutrient_path):
        os.mkdir(nutrient_path)

    # Load the mapping between composite dairy food codes and the associated dairy ingredient
    with open(data_path / 'mappings/dairy_ingredients_dict.json', 'r') as f:
        dairy_ingredient_dict = json.load(f)

    ## For CCC scenarios, include poultry food groups ["Poultryg", "ProcessedPoultryg", "GameBirds"] to food_groups_to_reduce
    all_meat_food_groups = food_groups_to_reduce + ['Poultryg', 'ProcessedPoultryg', 'GameBirdsg']

    #Run the simulation to compute impact on nutrients based on maximum daily intake for the SDG, 60g/day and 31g/day scenarios
    if max_intake is not None:
        
        if not os.path.exists(nutrient_path + f'diet_data_seed_{seed}.parquet'):
            item_level_data.reduction_percentage(percent_reduction=dairy_reduction, 
                                                 food_group_reductions=food_groups_dairy)
    
            item_level_data.reduction_to_cutoff_random(cutoff=max_intake, 
                                                       min_reduction=10, 
                                                       baseline_intake=df_baseline,
                                                       food_groups_to_reduce=food_groups_to_reduce, seed=seed)
    
    
            # Apply reductions in red and red processed meat at the item level
            scenario_diet_data = item_level_data.nutrient_impact_item_level_reductions_cutoff   (                                             
                                                food_groups_to_reduce=food_groups_to_reduce,
                                                df_nutrients=nutrients_per_gram_meat,
                                                mapping_dict=meat_mapping_dict,
                                                )
    
    
            scenario_diet_data = item_level_data.nutrient_impact_item_level_reductions_percentage(
                diet_data=scenario_diet_data,
                df_nutrients=nutrients_per_gram_dairy_meat,
                food_group_reductions=food_groups_dairy,
                mapping_dict=dairy_ingredient_dict,
                dairy_reduction=dairy_reduction
            )
    
            df_nutrients_scenario = item_level_data.finalise_nutrient_intake(scenario_diet_data=scenario_diet_data)
            if (df_nutrients_scenario[food_groups_to_reduce] < 0).any().any():
                raise ValueError(
                    'Reduction has exceeded reported consumption: check for possible double counting in specification of nutrients to include in reduction scenarios')
    
            if (df_nutrients_scenario['Total RRPM meat'] > max_intake + 0.001).any():
                print(
                    df_nutrients_scenario[df_nutrients_scenario['Total RRPM meat'] > max_intake + 0.001]['Total RRPM meat'])
                print(len(df_nutrients_scenario[df_nutrients_scenario['Total RRPM meat'] > max_intake + 0.001]['Total RRPM meat']))
                raise ValueError("The sum of food_groups_to_reduce exceeds the maximum intake threshold")
    
            scenario_diet_data.to_parquet(nutrient_path + f'diet_data_seed_{seed}.parquet')
            df_nutrients_scenario.to_parquet(nutrient_path + f'df_nutrients_seed_{seed}.parquet')
        
        else:
            scenario_diet_data = pd.read_parquet(nutrient_path + f'diet_data_seed_{seed}.parquet')
            df_nutrients_scenario = pd.read_parquet(nutrient_path + f'df_nutrients_seed_{seed}.parquet')

    # Applies a percent level reduction to all meat food groups for the CCC 2030 and CCC 2050 scenarios and computes the associated impact on nutrient intake
    elif percent_reduction is not None:
        # Nutrient impact for percent reductions are unique and do not need to be re-run for different random seed parameters.
        if not os.path.exists(nutrient_path + f'diet_data_scenario.parquet'):
            item_level_data.reduction_percentage(percent_reduction=dairy_reduction, food_group_reductions=food_groups_dairy)
            item_level_data.reduction_percentage(percent_reduction=percent_reduction,
                                                 food_group_reductions=all_meat_food_groups)

            scenario_diet_data = item_level_data.data.copy()

            # dairy food group reductions
            scenario_diet_data = item_level_data.nutrient_impact_item_level_reductions_percentage(
                diet_data=scenario_diet_data,
                df_nutrients=nutrients_per_gram_dairy_meat,
                food_group_reductions=food_groups_dairy,
                mapping_dict=dairy_ingredient_dict,
                dairy_reduction=dairy_reduction
            )

            # meat food group reductions
            scenario_diet_data = item_level_data.nutrient_impact_item_level_reductions_percentage(
                # percent_reduction=dairy_reduction,
                diet_data=scenario_diet_data,
                df_nutrients=nutrients_per_gram_meat,
                food_group_reductions=all_meat_food_groups,
                mapping_dict=meat_mapping_dict,
                dairy_reduction=dairy_reduction
            )

            df_nutrients_scenario = item_level_data.finalise_nutrient_intake(scenario_diet_data=scenario_diet_data)
            if (df_nutrients_scenario[food_groups_to_reduce] < 0).any().any():
                raise ValueError(
                    'Reduction has exceeded reported consumption: check for possible double counting in specification of nutrients to include in reduction scenarios')

            df_nutrients_scenario.to_parquet(nutrient_path + f'df_scenario.parquet')
            scenario_diet_data.to_parquet(nutrient_path + f'diet_data_scenario.parquet')
        else:
            df_nutrients_scenario = pd.read_parquet(nutrient_path + f'df_scenario.parquet')

    else:
        raise ValueError('Must specify either a maximum daily intake in g, or a percent level reduction')

    shes_data.data['Red meat intake'] = df_nutrients_scenario['Red meat intake']
    shes_data.data['Processed meat intake'] = df_nutrients_scenario['Processed meat intake']

    shes_data.data['Change in energy kcal'] = df_nutrients_scenario['Energykcal'] - df_baseline['Energykcal']
    # Change in energy intake per individual between the baseline and the simulation scenario. The change in kJ is used as input to the obesity model.
    shes_data.data['Change in energy kJ'] = df_nutrients_scenario['EnergykJ'] - df_baseline['EnergykJ']
    
    if not bmi_change:
        shes_data.data['Change in energy kJ'] = 0

    df_sim = shes_data.data.copy()
    df_sim['CRC'] = 0
    df_sim['Total dairy'] = df_baseline['Total dairy']

    # remove the pregnant participants from the sample for the health simulations as the disease risk models are non-applicable
    pregnant_ids = df_sim[df_sim['preg'] == 1].index.tolist()
    df_sim = df_sim[~df_sim.index.isin(pregnant_ids)]

    if dairy_reduction is not None:
        df_sim['Total dairy'] = ((100 - dairy_reduction) / 100) * df_sim['Total dairy']

    # if test_mode:
    #     df_sim = df_sim.head(n=50)  # If test mode only select the first 50 individuals in the population.py

    # Takes the samples from the beta distribution that was used to model the association between total dairy intake and diabetes risk
    beta_df_dairy = pd.read_parquet(data_path / 'beta_samples_dairy.parquet')
    
    # Set vigorous PA to 0, reallocate to moderate and apply the calibration equations from Welk et al,
    df_sim = prep_physical_activity_data(df=df_sim, seed=seed)

    # Sample from known sources of uncertainty
    df_sim = run_sampling(df_sim, seed=seed, beta_df_dairy=beta_df_dairy)
    
    # Calculate baseline risks 
    df_sim = calculate_risks(df_sim, mortality_table=mortality_table, seed=seed)

    # Iterate over all simulation years
    for year in range(1, years + 1):
        # Compute expected mortalities prior to new disease cases
        df_sim = update_mortalities(df_sim, year=year, pre_new_cases=True)
        # Compute expected incidence of each disease
        df_sim = update_cases(df_sim, year=year)
        # Compute expected mortalities accounting for new disease cases
        df_sim = update_mortalities(df_sim, year=year, pre_new_cases=False)
        # Remove the new mortalities from the simulation population
        df_sim = apply_new_mortalities(df_sim, year=year)

        # Compute the change in BMI from the reduction in meat intake
        df_sim = update_obesity(df=df_sim, year=year, seed=seed)
            
        # Update demographic variables for the next year of the sim
        df_sim = update_df(df=df_sim, posterior_samples=post_samples, seed=seed, year=year, bmi_change=bmi_change)
        # Update disease risks for each individual based on the updated demographic variables
        df_sim = calculate_risks(df_sim, mortality_table=mortality_table, seed=seed)
        print(f'Finished year {year}')

    print(f'Saving output to: {path}{file_name}')
    df_sim.to_parquet(path=path + file_name)

    return


def parse_arguments(args=None):
    """
    Parse the arguments supplied
    """
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('--path_to_df', default=os.getcwd(), type=str, required=True) # path to unimputed health data df_SHeS_unimputed.parquet
    parser.add_argument('--seed', default=0, type=int, required=True)# random seed parameter
    parser.add_argument('--red_meat', default=False, type=str2bool, required=True)# boolean, sets whether to reduce unprocessed re meat or not
    parser.add_argument('--processed_meat', default=False, type=str2bool, required=True)# boolean, sets whether to reduce processed meat or not.
    parser.add_argument('--bmi_change', default=True, type=str2bool, required=False)# boolean, sets whether to also include the Hall obesity model assuming that the meat reductions reduce caloric intake
    parser.add_argument('--years', default=10, type=int, required=False) # int, number of years to run the simulation for
    parser.add_argument('--max_intake', default=None, type=float, required=False) # float, if set the nutrient simulation sets a maximum intake level for red and/or processed meat and calculates the net reduction for a single iteration of red and/or processed meat reduction. Cannot also be set with a percent_reduction parameter 
    parser.add_argument('--percent_reduction', default=None, type=float, required=False) # float, if set the simulation applies a blanket level reduction of red and/or processed meat. Cannot be set with a parameter for the maximum intake level.
    parser.add_argument('--dairy_reduction', default=None, type=float, required=False) # float; Percent level reduction to apply to all dairy ingredients.
    parser.add_argument('--test_mode', default=False, type=str2bool, required=False) # boolean: if true the simulation runs for a subset of the paricipants.

    options = parser.parse_args(args)
    return options


def main(args=None):
    options = parse_arguments(args)
    run_sim(**vars(options))


if __name__ == '__main__':
    start_time = time.time()
    main(sys.argv[1:])
    end_time = time.time()
    print(f'Total running time: {(end_time - start_time) / 60} minutes')
