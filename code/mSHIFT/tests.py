from colorectal_cancer import *
from population import *
import pandas as pd
import numpy as np
import warnings
from variable_imputation import *




def test_reduction():
    shes_data = Dataset(path='Data/df_SHeS_unimputed.parquet')

    shes_data.reduction_to_cutoff_random(max_intake=50, min_reduction=10,
                                         food_groups_to_reduce=['Red meat intake', 'Processed meat intake'], seed=2)

    cols = []
    for col in shes_data.data.columns:
        if 'meat' in col.lower():
            cols.append(col)

    print(shes_data.data[cols])

    return


def test_SBP_update(seed):
    shes_data = Dataset(path='Data/df_SHeS_unimputed.parquet')
    post_samples = shes_data.impute_missing_data(seed=seed)

    print(post_samples['Systolic Blood Pressure'])

    df = shes_data.data.copy()
    #print(df[df['age']<30][['Systolic Blood Pressure', 'age', 'Sex', 'Diabetes', 'High BP', 'Taking BPM', 'weight', 'height']])
    df['age'] += 1

    df = update_SBP(data=df, posterior_samples = post_samples, seed=seed)
    #print(df[df['age']<30][['Systolic Blood Pressure', 'age', 'Sex', 'Diabetes', 'High BP', 'Taking BPM', 'weight', 'height']])

    return

def test_BMI_update(seed, max_intake=60):

    nutrients_per_gram_meat = pd.read_parquet('Data/nutrients_per_gram_meat.parquet')
    df_baseline = pd.read_parquet('Data/df_baseline.parquet')
    shes_data = Individual_level_data(path='Data/df_SHeS_unimputed.parquet')
    #shes_data.initialise_BMI(years=10)
    post_samples = shes_data.impute_missing_data(seed=seed)

    RRPM_foods = ['Beefg',
                  'Lambg',
                  'Porkg',
                  'ProcessedRedMeatg',
                  'OtherRedMeatg',
                  'Burgersg',
                  'Sausagesg',
                  'Offalg']

    item_level_data = Food_item_level_data(path='Data/shes_2021_item_level_data.parquet',
                                           food_group_reductions=RRPM_foods,
                                           nutrients_per_gram_df=nutrients_per_gram_meat)

    df_nutrients_scenario = item_level_data.nutrient_impact_item_level_reductions(cutoff=max_intake,
                                                                                  min_reduction=10,
                                                                                  baseline_intake=df_baseline,
                                                                                  food_groups_to_reduce=RRPM_foods,
                                                                                  seed=seed)

    shes_data.data['Red meat intake'] = df_nutrients_scenario['Red meat intake']
    shes_data.data['Processed meat intake'] = df_nutrients_scenario['Processed meat intake']
    shes_data.data['Change in energy kJ'] = df_nutrients_scenario['EnergykJ'] - df_baseline['EnergykJ']

    #shes_data.data['Avg Mins MVPA per day'] = shes_data.data['Avg Mins MVPA per week']/7

    # mean_deltaE = shes_data.data['Change in energy kcal'].sum()
    # print(f'mean change in energy: {mean_deltaE}')

    df_subset = shes_data.data[shes_data.data['Change in energy kJ'] != 0].copy()
    df_subset[f'BMI year 0'] = df_subset['BMI']

    #print(df_subset[[f'BMI year 0', 'height', 'weight', 'initial weight', 'Change in energy kcal']].head())

    for year in range(1, 3):
        #print(shes_data.data['weight'].mean())
        #rint(f"mean BMI in year {year}: {shes_data.data[f'BMI year {year}'].mean()}")


        #print(df_subset.head())

        df_subset['weight'] = df_subset.apply(lambda row: update_weight(row=row, year=year), axis=1)
        df_subset['PAL'] = df_subset.apply(lambda row: Physical_Activity_Level(row), axis=1)
        df_subset[f'BMI year {year}'] = BMI(df=df_subset)


            #df_subset.apply(lambda row: BMI(row), axis=1)
        print(df_subset[df_subset['Vigorous PA']==0][[f'BMI year {year}', 'height', 'weight', 'initial weight', 'Change in energy kJ', 'PAL', 'Vigorous PA']].head())


        #shes_data.data = update_obesity(shes_data.data, year)








    return



def pick_out_outliers():

    #df = pd.read_parquet('Output/Max_intake/60.0_max_reduction/df_seed_1.parquet')

    df = pd.read_parquet('Data/nutrients_per_gram_meat.parquet')
    print(df.head())

    # columns = ['Change in energy kJ', 'BMI']
    #
    # for year in range(1, 6):
    #     columns.append(f'BMI year {year}')
    #
    # print(df.loc[1400004901, 'Change in energy kJ'])


    #
    # print(df[df['Change in energy kJ']<0][columns].head())
    # print('\n')
#
    # ind = df[df[f'BMI year 4']<0].iloc[0, :] #['Change in energy kJ']
    # print(ind)

    #print(df[(df[f'BMI year 4'] > 0) & (df['Change in energy kJ'] < 0)]['Change in energy kJ'])

    # for col, value in ind.items():
    #     print(col, value)




    return





if __name__=='__main__':


    #df = pd.read_parquet("Output/Max_intake/31.0_max_reduction20.0_dairy_reduction/df_seed_10.parquet")
    df = pd.read_parquet("Data/df_SHeS_unimputed.parquet")
    print(df["Processed meat intake"].sum())

    #test_BMI_update(seed=2, max_intake=60)







