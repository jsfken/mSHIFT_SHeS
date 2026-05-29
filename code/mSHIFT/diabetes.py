import numpy as np


def sample_closest_beta(total_dairy, beta_df):

    # Sample from te beta distribution with the values as close to the values of Total Dairy intake

    closest_row = beta_df.iloc[(beta_df['Total dairy'] - total_dairy).abs().argsort()[:1]]
    alpha, beta = closest_row['alpha'].values[0], closest_row['beta'].values[0]
    sample = np.random.beta(alpha, beta)

    return sample


def RR_dairy_Diabetes(row, seed, beta_df_dairy):
    """
    Samples from the reconstructed relative risk association between totaly dairy intake and diabetes risk
    :param row: individual in the simualtion
    :param seed: random seed parameter
    :param beta_df_dairy: beta distribution samples for different values of total dairy intake
    :return:
    """
    np.random.seed(seed)
    RR_dairy = sample_closest_beta(total_dairy=row['Total dairy'], beta_df=beta_df_dairy)

    return RR_dairy

def Hazard_ratio_CM_Diabetes(row, seed):

    """
    :param row: row of the dataframe corresponding to an individual participant
    :param seed: random seed parameter
    :return: estimated relative risk for a individual's processed meat intake
    """

    np.random.seed(seed)

    if row['Processed meat intake'] > 0:
        if row['Processed meat intake'] < 15:
            HR_best_fit = 0.02 * row['Processed meat intake'] + 1
        else:
            HR_best_fit = 0.0022 * row['Processed meat intake'] + 1.27

        if row['Processed meat intake'] < 15:
            HR_2sigma = 0.0271 * row['Processed meat intake'] + 1  ## Estimated from the upper curve
        else:
            HR_2sigma = 0.00366 * row['Processed meat intake'] + 1.28
            # HR_lower = 0.003*diet.red_meat + 0.88

        sigma = (HR_2sigma - HR_best_fit) / 2
        Hazard_ratio = np.random.normal(HR_best_fit, sigma)
    else:
        Hazard_ratio = 1

    return Hazard_ratio


def Hazard_ratio_RM_Diabetes(row, seed):

    """
    :param row: row of the dataframe corresponding to an individual particpant
    :param seed: random seed parameter
    :return: estimated relative risk for a individual's unprocessed red meat intake
    """
    np.random.seed(seed)

    if row['Red meat intake'] > 0:
        if row['Red meat intake'] < 40:
            HR_best_fit = 0.004 * row['Red meat intake'] + 1
            HR_2sigma = 0.0078 * row['Red meat intake'] + 1  ## Estimated from the upper curve
        else:
            HR_best_fit = 0.004 * row['Red meat intake'] + 1.0
            HR_2sigma = 0.004 * row['Red meat intake'] + 1.19

        sigma = (HR_2sigma - HR_best_fit) / 2
        Hazard_ratio = max(np.random.normal(HR_best_fit, sigma), 1)
    else:
        Hazard_ratio = 1

    return Hazard_ratio


Diabetes_dict = {

    'CARDIA': {

        'age Group': 0.295,
        'Black': -0.055,
        'Male': -0.958,
        'BMI': 0.083,
        'Parental History': 0.507,
        'Smoker': -0.13,
        'High SBP': 1.347,
        'High Cholesterol': 0.431,
        'Time': 10,
        'Constant': -5.171

    },

    'CARDIA-10': {
        'age Group': 0.217,
        'Black': 0.342,
        'Male': 0.322,
        'BMI': 0.134,
        'Parental History': 0.857,
        'Smoker': -0.013,
        'High SBP': 0.09,
        'High Cholesterol': 0.328,
        'Time': 10,
        'Constant': -7.516

    },

    'ARIC': {

        'age Group': 0.076,
        'Black': 0.280,
        'Male': 0.454,
        'BMI': 0.130,
        'Parental History': 0.626,
        'Smoker': 0.305,
        'High SBP': 0.386,
        'High Cholesterol': 0.002,
        'Time': 9,
        'Constant': -6.662

    },
    'CHS': {

        'age Group': -0.164,
        'Black': 0.235,
        'Male': 0.414,
        'BMI': 0.135,
        'Parental History': 0.281,  # What variable to use for parental history? Currently using 'family history'
        'Smoker': 0.181,
        'High SBP': 0.635,
        'High Cholesterol': -0.054,
        'Time': 7,
        'Constant': -7.405

    }
}


def Sigmoid(x):
    """
    :param x: float
    :return: sigmoid of the float
    """
    z = 1 / (1 + np.exp(-x))
    return z


def Diabetes_risk_Alva(row, Diabetes_dict):

    """
    :param row: participant
    :param Diabetes_dict: Dictionary containing the parameters for estimating diabetes risk based on demographic variables.
    :return: Yearly diabetes risk for that individual
    """

    if row['age'] < 35:
        dict = Diabetes_dict['CARDIA']
    elif row['age'] < 55:
        dict = Diabetes_dict['CARDIA-10']
    elif row['age'] < 75:
        dict = Diabetes_dict['ARIC']
    else:
        dict = Diabetes_dict['CHS']

    S = 0

    S += dict['age Group']

    if row['Ethnicity'] == 'Other minority ethnic':
        S += dict['Black']
    if row['Sex'] == 0:
        S += dict['Male']

    S += row['BMI'] * dict['BMI']
    S += row['Parental Diabetes History'] * dict['Parental History']
    S += row['Current Smoker'] * dict['Smoker']

    if row['Systolic Blood Pressure'] > 140:
        S += dict['High SBP']
    if row['Total Cholesterol'] > 240:
        S += dict['High Cholesterol']

    S += dict['Constant']

    P = Sigmoid(S)
    Diabetes_rate = -np.log(1 - P) / dict['Time']
    Diabetes_risk = 1 - np.exp(-Diabetes_rate)

    HR_CM = row['PM_HR_Diabetes']
    HR_RM = row['RM_HR_Diabetes']
    RR_D = row['D_RR_Diabetes']

    Diabetes_risk = Diabetes_risk * HR_CM * HR_RM * RR_D

    # including dairy
    age_calibration_values = [
        (15, 19, 82.51),
        (20, 29, 17.46),
        (30, 39, 5.73),
        (40, 49, 1.74),
        (50, 59,  1.78),
        (60, 69, 1.75),
        (70, 200, 1.17)
    ]

    for lower_bound, upper_bound, value in age_calibration_values:
        if lower_bound <= row['age'] <= upper_bound:
            Diabetes_risk /= value
            break  # exit loop once calibration is applied
        else:
            pass


    return Diabetes_risk
