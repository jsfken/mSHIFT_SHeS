import numpy as np
import pandas as pd
from colorectal_cancer import *
from CVD import *
from diabetes import *
from mortalities import *
from incidence import *
from obesity import *



def prep_physical_activity_data(df: pd.DataFrame, seed: int):
    
    np.random.seed(seed)
    
    df["MVPA"] = df[['Moderate PA', 'Vigorous PA']].sum(axis=1)
    df["MVPA"] = df["MVPA"].clip(upper=180)
    df["Sedentary non-sleep"] = 1440 - df['MVPA'] - 420
    
    # Apply the Welk et al calibration
    df['MVPA'] = df.apply(welk_recalibration, axis=1)
    
    # identify particpants who reported non-zero vigorous physical activity
    reported_vpa_mask = df['Vigorous PA'] > 0
    
    # set the upper boundto be the minimum of either 30 or self reported vig pa
    max_mins_vig = df.loc[reported_vpa_mask, 'MVPA'].clip(upper=30)
    
    # randomly sample from the range for thse with vig_pa >0
    random_vig_pa = np.random.uniform(low=0, high=max_mins_vig)
    
    df['Vigorous PA'] = 0.0                   
    df.loc[reported_vpa_mask, 'Vigorous PA'] = random_vig_pa
    
    # allocate the remainder to moderate PA
    df['Moderate PA'] = df['MVPA'] - df['Vigorous PA']
    
    # derivie sedentary non-sleep assuing 7 hours of sleep on average
    df['Sedentary non-sleep'] = 1440 - df['MVPA'] - 420
    
    return df



def run_sampling(df, seed, beta_df_dairy):
    np.random.seed(seed)

    df['PM_HR_Diabetes'] = df.apply(lambda row: Hazard_ratio_CM_Diabetes(row, seed=seed), axis=1)
    df['RM_HR_Diabetes'] = df.apply(lambda row: Hazard_ratio_RM_Diabetes(row, seed=seed), axis=1)
    df['D_RR_Diabetes'] = df.apply(lambda row: RR_dairy_Diabetes(row, seed=seed, beta_df_dairy=beta_df_dairy), axis=1)

    df['PM_HR_CVD'] = df.apply(lambda row: Hazard_ratio_CM_CVD(row, seed=seed), axis=1)
    df['RM_HR_CVD'] = df.apply(lambda row: Hazard_ratio_RM_CVD(row, seed=seed), axis=1)
    
    met_rng = np.random.default_rng(seed=seed)

    # sample a physical level for each particpant based on self reported PAL. MET random number generator ensures that different particpants are assigned different MET scores for modeterate and vigorous physical activities for the same seed parameter 
    df['PAL'] = df.apply(Physical_Activity_Level, axis=1, args=(met_rng,))
    
    return df


def update_smoking_pack_years(row):
    smoking_pack_years = 0

    if row['Smoking pack years'] != 0:
        smoking_pack_years = row['Smoking pack years']
        smoking_pack_years += row['Daily Cigarettes'] / 20

    return smoking_pack_years


def update_SBP(data, posterior_samples, seed):
    np.random.seed(seed)
    # SBP=row['Systolic Blood Pressure']
    SBP_samples = posterior_samples['Systolic Blood Pressure']

    Sex = data['Sex']
    Age = data['age']
    Weight = data['weight']
    Height = data['height']
    high_bp_diagnosis = data['High BP']
    BMI = data['BMI']

    data['Systolic Blood Pressure'] =  np.exp((((((Weight / (SBP_samples['a2'] + (SBP_samples['a5'] * Age))) + SBP_samples['a1']) + np.sqrt(Age)) * SBP_samples['a7']) + (-(high_bp_diagnosis) * SBP_samples['a6'])))


    data['Systolic Blood Pressure'] += np.random.normal(loc=0, scale=SBP_samples['sigma'],
                                                        size=len(data['Systolic Blood Pressure']))

    return data


def update_Total_Cholesterol(data, posterior_samples, seed):
    np.random.seed(seed)
    total_chol_samples = posterior_samples['Total Cholesterol']

    Sex = data['Sex']
    Age = data['age']
    medication_high_BP = data['Taking BPM']
    Diabetes = data['Diabetes']
    SBP = data['Systolic Blood Pressure']
    HDL_Cholesterol = data['HDL Cholesterol']

    data['Total Cholesterol'] = ((((((total_chol_samples['a12'] + (
            (total_chol_samples['a7'] ** Sex) + total_chol_samples['a10'])) * (
                                                  ((np.array(medication_high_BP) + (
                                                          np.array(Diabetes) ** total_chol_samples['a3'])) /
                                                   total_chol_samples['a2']) *
                                                  total_chol_samples['a7'])) + total_chol_samples['a0']) / np.array(Age)) ** (total_chol_samples['a4']
                  + ((np.array(Age) * total_chol_samples['a10']) * (
            (total_chol_samples['a3'] * (np.array(medication_high_BP + SBP))) ** (
            total_chol_samples['a12'] * (total_chol_samples['a6'] + np.array(HDL_Cholesterol))))))) *
                                      total_chol_samples['a8'])

    data['Total Cholesterol'] += np.random.normal(loc=0, scale=total_chol_samples['sigma'], size=len(data['Total Cholesterol']))

    mask = data['Total Cholesterol'] < 69
    data.loc[mask, 'Total Cholesterol'] = 69

    return data

def update_HDL_Cholesterol(data, posterior_samples, seed):

    np.random.seed(seed)

    HDL_samples = posterior_samples['HDL Cholesterol']

    Age = data['age']
    BMI = data['BMI']
    Sex = data['Sex']
    Smoker = data['Current Smoker']
    Diabetes = data['Diabetes']

    data['HDL Cholesterol'] = (((((((HDL_samples['a2'] ** (np.exp(np.array(BMI)) ** HDL_samples['a12'])) / -(
        HDL_samples['a0'])) * (-(HDL_samples['a0']) ** np.array(Sex))) + (HDL_samples['a4'] ** np.array(Age))) *
                                      HDL_samples['a2']) ** (
                                             (HDL_samples['a8'] ** np.array(Diabetes)) * HDL_samples[
                                         'a12'])) + -((HDL_samples['a5'] + np.array(Smoker))))



    data['HDL Cholesterol'] += np.random.normal(loc=0, scale=HDL_samples['sigma'],
                                                     size=len(data['HDL Cholesterol']))
    mask = data['HDL Cholesterol'] < 6
    data.loc[mask, 'HDL Cholesterol'] = 6


    #
    # mask = np.ones(len(data['HDL Cholesterol']), dtype=bool)
    # while mask.any():
    #     valid_samples = np.random.normal(loc=0, scale=HDL_samples['sigma'], size=mask.sum())
    #     data.loc[mask, 'HDL Cholesterol'] += valid_samples
    #     mask = data['HDL Cholesterol'] <= 6  # Minimum value of HDL cholesterol as measured in NHANES

    return data


def update_df(df, posterior_samples, seed, year, bmi_change):

    df['age'] += 1
    
    if bmi_change:
        df['weight'] = df[f'weight year {year}']
        df['BMI'] = df[f'BMI year {year}']

    df = update_SBP(data=df, posterior_samples=posterior_samples, seed=seed)
    df = update_HDL_Cholesterol(data=df, posterior_samples=posterior_samples, seed=seed)
    df = update_Total_Cholesterol(data=df, posterior_samples=posterior_samples, seed=seed)

    return df


def calculate_risks(df, mortality_table, seed):
    np.random.seed(seed)

    df['Diabetes risk'] = df.apply(lambda row: Diabetes_risk_Alva(row, Diabetes_dict=Diabetes_dict), axis=1)
    df['CVD risk no diabetes'] = df.apply(lambda row: updated_Framingham_CVD_risk(row, with_diabetes=False), axis=1)
    df['CVD risk with diabetes'] = df.apply(lambda row: updated_Framingham_CVD_risk(row, with_diabetes=True), axis=1)

    df['CRC risk no diabetes'] = 0  # df.apply(lambda row: CRC_risk(row, with_diabetes=False), axis=1)
    df['CRC risk with diabetes'] = 0  # df.apply(lambda row: CRC_risk(row, with_diabetes=True), axis=1)

    df['Diabetes and CVD risk'] = df['Diabetes risk'] * df[
        'CVD risk no diabetes']  ## Probability of getting both in one year from a starting healthy state
    df['Diabetes and CRC risk'] = 0  # df['Diabetes risk']*df['CRC risk no diabetes']
    df['CVD and CRC risk with diabetes'] = 0  # df['CVD risk with diabetes']*df['CRC risk with diabetes']
    df['CVD and CRC risk no diabetes'] = 0  # df['CVD risk no diabetes']*df['CRC risk no diabetes']
    df['Diabetes and CVD and CRC risk'] = 0  # df['Diabetes risk']*df['CVD risk no diabetes']*df['CRC risk no diabetes']

    df['diabetes mortality risk'] = df.apply(
        lambda row: mortality_prob(row, mortality_table=mortality_table, with_diabetes=True, with_CVD=False), axis=1)
    df['CVD mortality risk'] = df.apply(
        lambda row: mortality_prob(row, mortality_table=mortality_table, with_diabetes=False, with_CVD=True), axis=1)
    df['diabetes and CVD mortality risk'] = df.apply(
        lambda row: mortality_prob(row, mortality_table=mortality_table, with_diabetes=True, with_CVD=True), axis=1)
    df['CRC mortality risk'] = 0  # df.apply(lambda row: CRC_mortality_prob(row), axis=1)
    df['Healthy mortality risk'] = df.apply(
        lambda row: mortality_prob(row, mortality_table=mortality_table, with_diabetes=False, with_CVD=False), axis=1)

    return df


def update_mortalities(df, year, pre_new_cases):
    
    if pre_new_cases:
        end = 'pre'
    else:
        end = 'post'
        
    columns = [f'Healthy mortalities year {year} {end}', f'diabetes mortalities year {year} {end}', f'CVD mortalities year {year} {end}', f'diabetes and CVD mortalities year {year} {end}', f'Total mortalities year {year} {end}']
    df_year = pd.DataFrame(index =df.index, columns=columns)
    
    df_year[f'Healthy mortalities year {year} {end}'] = df.apply(lambda row: expected_healthy_mortalities(row), axis=1).copy()
    df_year[f'diabetes mortalities year {year} {end}'] = df.apply(lambda row: expected_diabetes_mortalities(row), axis=1).copy()
    df_year[f'CVD mortalities year {year} {end}'] = df.apply(lambda row: expected_CVD_mortalities(row), axis=1).copy()
  
    df_year[f'diabetes and CVD mortalities year {year} {end}'] = df.apply(lambda row: expected_diabetes_CVD_mortalities(row), axis=1).copy()
    df_year[f'Total mortalities year {year} {end}'] = df_year[f'Healthy mortalities year {year} {end}'] + df_year[f'diabetes mortalities year {year} {end}'] + df_year[f'CVD mortalities year {year} {end}'] - df_year[f'diabetes and CVD mortalities year {year} {end}']
    
    df = pd.concat([df, df_year], axis=1)

    return df


def update_cases(df, year):
    df[f'New diabetes cases year {year}'] = df.apply(lambda row: expected_new_diabetes_cases(row), axis=1)
    df[f'New CVD cases year {year}'] = df.apply(lambda row: expected_new_CVD_cases(row), axis=1)
    df[f'New CRC cases year {year}'] = df.apply(lambda row: expected_new_CRC_cases(row), axis=1)
    df[f'New diabetes and CVD cases year {year}'] = df.apply(lambda row: expected_new_diabetes_CVD_cases(row), axis=1)
    df[f'New diabetes and CRC cases year {year}'] = df.apply(lambda row: expected_new_diabetes_CRC_cases(row), axis=1)
    df[f'New CVD and CRC cases year {year}'] = df.apply(lambda row: expected_new_CVD_CRC_cases(row), axis=1)
    df[f'New diabetes and CVD and CRC cases year {year}'] = df.apply(lambda row: expected_new_diabetes_CVD_CRC_cases(row), axis=1)

    df['New diabetes cases'] += df[f'New diabetes cases year {year}']
    df['New CVD cases'] += df[f'New CVD cases year {year}']
    df['New CRC cases'] += df[f'New CRC cases year {year}']
    df['New diabetes and CVD cases'] += df[f'New diabetes and CVD cases year {year}']
    df['New diabetes and CRC cases'] += df[f'New diabetes and CRC cases year {year}']
    df['New CVD and CRC cases'] += df[f'New CVD and CRC cases year {year}']
    df['New diabetes and CVD and CRC cases'] += df[f'New diabetes and CVD and CRC cases year {year}']

    df['healthy'] = df.apply(lambda row: healthy_pop(row), axis=1)

    return df


def update_sample_weight(row, year):
    SW = row['Sample Weight']
    SW -= row[f'Total mortalities year {year} post']
    #
    if SW < 0:
        SW = 0
    else:
        pass

    return SW


## Update the diabetes cases

def update_new_diabetes_cases(row, year):
    new_cases = row['New diabetes cases']

    if row['Diabetes'] != 1:
        new_cases -= row[f'diabetes mortalities year {year} post']
        if new_cases < 0:
            new_cases = 0
    else:
        pass

    return new_cases


def update_new_CVD_cases(row, year):
    new_cases = row['New CVD cases']

    if row['CVD'] != 1:
        new_cases -= row[f'CVD mortalities year {year} post']
        if new_cases < 0:
            new_cases = 0
    else:
        pass

    return new_cases


# def update_new_CRC_cases(row, year):
#     new_cases = row['New CRC cases']

#     if row['CRC'] != 1:
#         new_cases -= row[f'CRC mortalities year {year} post']
#         if new_cases < 0:
#             new_cases = 0
#     else:
#         pass

#     return new_cases


def update_new_diabetes_CVD_cases(row, year):
    new_cases = row['New diabetes and CVD cases']

    if row['Diabetes'] != 1 and row['CVD'] != 1:
        new_cases -= row[f'diabetes and CVD mortalities year {year} post']
        if new_cases < 0:
            new_cases = 0

    return new_cases


# def update_new_diabetes_CRC_cases(row, year):
#     new_cases = row['New diabetes and CRC cases']

#     if row['Diabetes'] != 1 and row['CRC'] != 1:
#         new_cases -= row[f'diabetes and CRC mortalities year {year} post']
#         if new_cases < 0:
#             new_cases = 0

#     return new_cases


# def update_new_CVD_CRC_cases(row, year):
#     new_cases = row['New CVD and CRC cases']

#     if row['CVD'] != 1 and row['CRC'] != 1:
#         new_cases -= row[f'CVD and CRC mortalities year {year} post']
#         if new_cases < 0:
#             new_cases = 0

#     return new_cases


# def update_new_diabetes_CVD_CRC_cases(row, year):
#     new_cases = row['New diabetes and CVD and CRC cases']

#     if row['Diabetes'] != 1 and row['CVD'] != 1 and row['CRC'] != 1:
#         new_cases -= row[f'diabetes and CVD and CRC mortalities year {year} post']
#         if new_cases < 0:
#             new_cases = 0

#     return new_cases


def apply_new_mortalities(df, year):
    df['Sample Weight'] = df.apply(lambda row: update_sample_weight(row, year), axis=1)
    df['New diabetes cases'] = df.apply(lambda row: update_new_diabetes_cases(row, year), axis=1)
    df['New CVD cases'] = df.apply(lambda row: update_new_CVD_cases(row, year), axis=1)
    #df['New CRC cases'] = df.apply(lambda row: update_new_CRC_cases(row, year), axis=1)
    df['New diabetes and CVD cases'] = df.apply(lambda row: update_new_diabetes_CVD_cases(row, year), axis=1)
    #df['New diabetes and CRC cases'] = df.apply(lambda row: update_new_diabetes_CRC_cases(row, year), axis=1)
    #df['New CVD and CRC cases'] = df.apply(lambda row: update_new_CVD_CRC_cases(row, year), axis=1)
    #df['New diabetes and CVD and CRC cases'] = df.apply(lambda row: update_new_diabetes_CVD_CRC_cases(row, year),axis=1)

    return df

def update_obesity(df, year, seed):

    df[f'weight year {year}'] = df.apply(lambda row: update_weight(row=row, year=year, seed=seed), axis=1)
    df[f'BMI year {year}'] = df.apply(lambda row: compute_BMI(row, year), axis=1)
    
    return df