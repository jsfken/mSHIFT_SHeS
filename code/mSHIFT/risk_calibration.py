import numpy as np
import pandas as pd
from diabetes import *
from colorectal_cancer import *
from CVD import *
from incidence import expected_new_diabetes_cases, expected_new_CRC_cases, expected_new_CVD_cases
from variable_imputation import *
import matplotlib.pyplot as plt
from population import *
from demographic_conditions import *






def filter_df(df: pd.DataFrame, conditions_tuple: tuple):

    desc = conditions_tuple[0]
    conditions = conditions_tuple[2]

    if desc == 'Overall':
      return df
    else:
        filtered_df = pd.DataFrame()
        for idx, cond in enumerate(conditions):
            column = cond['column']
            condition = cond['condition']
            boolean_operator = cond['boolean_operator']
            if idx == 0:
                filtered_df = df[df[column].apply(condition)]
            elif boolean_operator == 'and':
                filtered_df = filtered_df[filtered_df[column].apply(condition)]
            elif boolean_operator == 'or':
                filtered_df = pd.concat([filtered_df, df[df[column].apply(condition)]],
                                        ignore_index=True).drop_duplicates()

    return filtered_df

def calibrate_diabetes_model(condition: tuple, num_runs: int, Diabetes_dict: dict):
    
    shes_data = Individual_level_data(path='data/df_SHeS_unimputed.parquet')
    beta_df_dairy = pd.read_parquet('data/beta_samples_dairy.parquet')
    df_baseline = pd.read_parquet(path='data/df_baseline.parquet')

    diabetes_cases = []
    for seed in range(num_runs):

        np.random.seed(seed)
        shes_data.impute_missing_data(seed=seed)

        df = filter_df(df=shes_data.data, conditions_tuple=condition)
        df['Total dairy'] = df_baseline['Total dairy']

        df['PM_HR_Diabetes'] = df.apply(lambda row: Hazard_ratio_CM_Diabetes(row, seed=seed), axis=1)
        df['RM_HR_Diabetes'] = df.apply(lambda row: Hazard_ratio_RM_Diabetes(row, seed=seed), axis=1)
        df['D_RR_Diabetes'] = df.apply(lambda row: RR_dairy_Diabetes(row, seed=seed, beta_df_dairy=beta_df_dairy),  axis=1)

        df['Diabetes risk'] = df.apply(lambda row: Diabetes_risk_Alva(row, Diabetes_dict=Diabetes_dict), axis=1)
        df['New diabetes cases'] = df.apply(lambda row: expected_new_diabetes_cases(row), axis=1)
        diabetes_cases.append(df['New diabetes cases'].sum())

    return diabetes_cases


def calibrate_CVD_model(condition, num_runs):
    shes_data = Individual_level_data(path='data/df_SHeS_unimputed.parquet')

    CVD_cases = []
    #df['New diabetes cases'] = 0
    for seed in range(num_runs):

        np.random.seed(seed)
        shes_data.impute_missing_data(seed=seed)
        df = filter_df(df=shes_data.data, conditions_tuple=condition)


        #print(df[['Systolic Blood Pressure', 'Total Cholesterol', 'HDL Cholesterol']])

        df['PM_HR_CVD'] = df.apply(lambda row: Hazard_ratio_CM_CVD(row, seed=seed), axis=1)
        df['RM_HR_CVD'] = df.apply(lambda row: Hazard_ratio_RM_CVD(row, seed=seed), axis=1)

        df['CVD risk with diabetes'] = df.apply(lambda row: updated_Framingham_CVD_risk(row, with_diabetes=True), axis=1)
        df['CVD risk no diabetes'] = df.apply(lambda row: updated_Framingham_CVD_risk(row, with_diabetes=False), axis=1)
        df['New CVD cases'] = df.apply(lambda row: expected_new_CVD_cases(row), axis=1)
        #print(df['New CVD cases'].head())
        CVD_cases.append(df['New CVD cases'].sum())

    return CVD_cases

def calibrate_mortalities_model(condition, num_runs):
    shes_data = Individual_level_data(path='data/df_SHeS_unimputed.parquet')

    mortalities = []
    #df['New diabetes cases'] = 0
    for seed in range(num_runs):

        np.random.seed(seed)
        shes_data.impute_missing_data(seed=seed)

        df = filter_df(df=shes_data.data, conditions_tuple=condition)
        df['CRC'] = 0
        df = run_sampling(df, seed=seed)
        df = calculate_risks(df, mortality_table=mortality_table, seed=seed)
        df = update_mortalities(df=df, year=1, pre_new_cases=True)

        mort_year1 = df[f'Total mortalities year 1 pre'].sum()
        mortalities.append(mort_year1)

    return mortalities


def perform_calibration(condition, disease: str):
    
    if disease not in {'diabetes', 'CVD', 'mortalities'}:
        raise ValueError(f"Disease must be either: 'diabetes', 'CVD', 'mortalities'" )
        
    if disease == 'diabetes':
        cases = calibrate_diabetes_model(condition=condition, num_runs=50, Diabetes_dict=Diabetes_dict)
    elif disease == 'CVD':
        cases = calibrate_CVD_model(condition, num_runs=50)
    elif disease == 'mortalities':
        cases = calibrate_mortalities_model(condition=condition, num_runs=50)


    predicted_cases = np.mean(cases)
    error = np.std(cases)
    lower = predicted_cases - 1.96*error
    upper = predicted_cases + 1.96*error
    
    calibration_const = predicted_cases / condition[1]
    
    predicted_cases = int(predicted_cases)
    lower = int(lower)
    upper = int(upper)
    
    print(f'predicted cases: {predicted_cases}, ({lower}, {upper})')
    print(f'CC: {calibration_const}')

    return


def test_imputation():
    df = pd.read_parquet('Data/df_SHeS_unimputed.parquet')
    shes_data = Dataset(path = 'Data/df_SHeS_unimputed.parquet')

    sbp_samples_1 = []
    sbp_samples_2 = []
    for _ in range(100):
        shes_data.impute_missing_data()
        sbp_samples_1.append(float(shes_data.data.loc[1400001202, 'Systolic Blood Pressure']))
        sbp_samples_2.append(float(shes_data.data.loc[1400003001, 'Systolic Blood Pressure']))

    plt.hist(sbp_samples_1, label='person 1', bins = 30)
    plt.hist(sbp_samples_2, label='person 2', bins =30)
    plt.show()



    print(shes_data.data[['age', 'Systolic Blood Pressure', 'Total Cholesterol', 'HDL Cholesterol']].head())

    return


if __name__ == '__main__':

    # CVD calibration
    for condition in CVD_conditions:
        print(condition[0])
        perform_calibration(condition=condition, disease='CVD')
        print('\n')

    # diabetes calibration
    for condition in diabetes_conditions:
        print(condition[0])
        perform_calibration(condition=condition, disease='diabetes')
        print('\n')
        
    # mortalities calibration
    for condition in mortalities_conditions:
        print(condition[0])
        perform_calibration(condition=condition, disease='mortalities')
        print('\n')



