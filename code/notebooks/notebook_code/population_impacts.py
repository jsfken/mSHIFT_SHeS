import pandas as pd



def extract_threshold(age, age_dict):
    for (start, end), value in age_dict.items():
        if start <= age <= end:
            return value
    return None


def energy_gap(row: pd.Series):
    
  """
  Compute the level of underreported calories for each individual based on sex
  """
  
  energy_thresholds = {
    1: {
        (1, 3): 1004.0,
        (4, 6): 1378.0,
        (7, 10): 1703.0,
        (11, 14): 2000.0,
        (15, 18): 2000.0,
        (19, 50): 2000.0,
        (51, 64): 2000.0,
        (65, 74): 1912.0,
        (75, 500): 1840.0
    },
    0: {
        (1, 3): 1088.0,
        (4, 6): 1482.0,
        (7, 10): 1817.0,
        (11, 14): 2500.0,
        (15, 18): 2500.0,
        (19, 50): 2500.0,
        (51, 64): 2500.0,
        (65, 74): 2342.0,
        (75, 500): 2294.0
    }
    }
    
  sex = row['Sex']
  age = row['age']
    
  threshold_dict = energy_thresholds[sex]
  threshold = extract_threshold(age=age, age_dict=threshold_dict)

  energy_gap = threshold - row['Energykcal']

  #if row['Sex'] ==0:
#   elif row['Sex'] == 1:
#     energy_gap = 2000 - row['Energykcal']

  if energy_gap < 0:
    energy_gap = 0

  return energy_gap
  
def baseline_energy_exp(row):
    
    weight = row['weight']
    height = row['height']
    age = row['age']
    sex= row['Sex']

    if sex==0:
        # male
        BEE = 293-3.8*age + 4.564*height + 10.12*weight    # Assuming the height is in cm / age(yrs), weight (kgs)
    elif sex==1:
        # female
        BEE = 247-2.67*age + 4.015*height + 8.6*weight
  
    return BEE


def Physical_Activity_Level(row):

    weight = row['weight']
    height = row['height']
    age = row['age']
    sex= row['Sex']

    MET_dict = {'Moderate PA': 4.45, 'Vigorous PA': 7.95,
                'Sedentary non-sleep': 1.95, 'Sedentary sleep': 1.0}

    BEE = baseline_energy_exp(row=row)
    DeltaPAL = 0
    denominator = BEE/(0.0175*1440*weight)

    for activity in MET_dict.keys():
        numerator = (MET_dict[activity] - 1)*((1.15/0.9)*row[activity])/1440
        DeltaPAL_i = numerator/denominator
        DeltaPAL += DeltaPAL_i

    PAL = 1.1 + DeltaPAL

    return PAL
    
def total_energy_expenditure(row):
    
    age = row['age']
    height=row['height']
    weight=row['weight']
    preg = row['preg']
    
    PA = Physical_Activity_Level(row)
    
    if row['Sex'] == 0:
        TEE = 864 - 9.72*age + PA*(14.2*weight + 5.03*height)  # assuming height in cm
    elif row['Sex'] == 1:
        TEE = 387 - 7.31*age + PA*(10.9*weight + 6.607*height)
        
        
    # Assume an extra 300kcal per day if pregnant: https://pmc.ncbi.nlm.nih.gov/articles/PMC5104202/
    if preg == 1:
        TEE += 300
    
    return TEE
    
    
def energy_gap_TEE(row: pd.Series):
    
  """
  Compute the level of underreported calories for each individual based on TEE
  """
  
  TEE = total_energy_expenditure(row)
  energy_gap = TEE - row['Energykcal']

  # If self reported energy intake exseeds the TEE then there is no underreporting
  if energy_gap < 0:
    energy_gap = 0

  return energy_gap
  
def baseline_impact_adjusted_TEE(indicator: str,
                             df_baseline: pd.DataFrame):
    
  """
  Calculate the adjuisted daily impacts for each individual based on the level of underreporting
  """

  df_baseline[f"{indicator}_per_kcal"] = df_baseline[indicator]/df_baseline['Energykcal']
  df_baseline[f"{indicator}_adjusted"] = df_baseline[f"{indicator}"] + (df_baseline[f"{indicator}_per_kcal"]*df_baseline['energy_gap_TEE'])

  return df_baseline
  

def baseline_impact_adjusted(indicator: str,
                             df_baseline: pd.DataFrame):
    
  """
  Calculate the adjuisted daily impacts for each individual based on the level of underreporting
  """

  df_baseline[f"{indicator}_per_kcal"] = df_baseline[indicator]/df_baseline['Energykcal']
  df_baseline[f"{indicator}_adjusted"] = df_baseline[f"{indicator}"] + (df_baseline[f"{indicator}_per_kcal"]*df_baseline['energy_gap'])

  return df_baseline
  
def weighted_sum(group, variable, weight='Sample Weight'):
  weighted_sum = (group[variable]*group[weight]).sum()
  return weighted_sum
  
def weighted_sum(group: pd.DataFrame, 
                variable: str,
                weight: str):
  """
  Calculate the weighted sum of variable using the specified weights
  """
  weighted_sum = (group[variable]*group[weight]).sum()
  return weighted_sum


def calculate_within_psu_variance(variable: str,
                                  group: pd.DataFrame):
    # variance within each psu
    n_hj = len(group)  # Number of observations in PSU
    if n_hj > 1:
        weighted_mean = (group[variable] * group['Sample Weight']).sum() / group['Sample Weight'].sum()
        within_variance = ((group['Sample Weight'] * (group[variable] - weighted_mean)) ** 2).sum() / (n_hj - 1)
    else:
        within_variance = 0  # Cannot estimate variance with a single observation

    group['within_psu_variance'] = within_variance
    return group


# variance between psus in a single strata
def calculate_between_psu_variance(variable: str, group: pd.DataFrame):
    
    n_h = group['psu'].nunique()  # Number of PSUs in stratum

    if n_h > 1:
        strata_psus = group.groupby('psu')
        psu_means = strata_psus[[variable, 'Sample Weight']].apply(lambda g: weighted_sum(group=g, variable=variable, weight='Sample Weight'))

        stratum_mean = group[variable].mean()
        within_strata_variance = ((psu_means - stratum_mean) ** 2).sum() / (n_h - 1)
    else:
        within_strata_variance = 0  # Cannot estimate variance with a single PSU

    group['within_strata_variance'] = within_strata_variance

    return group

# combined variance of the within stratum variance and the variance within each psu in the stratum
def stratum_variance(group):
    n_h = group['psu'].nunique()
    total_strata_variance = group['within_strata_variance'].unique()[0] + (1 / n_h) * group['within_psu_variance'].sum()
    group['strata variance'] = total_strata_variance
    return group

def survey_error_sum(df_baseline: pd.DataFrame):
    
  """
  Calculate the survey error on the weighted sum of  
  """

  total_variance = 0
  for strata in df_baseline['strata'].unique():
    df_strata = df_baseline[df_baseline['strata']==strata]
    n_h = df_strata['psu'].nunique()
    strata_variance = df_strata['strata variance'].unique()[0]
    total_variance += (n_h / (n_h-1)) * strata_variance

  return total_variance
  
def weighted_impact(variable: str, 
                    df_baseline: pd.DataFrame):

  # The within item error on the calorie adjusted values are the same as the original values
  if 'adjusted' in variable:
    original_variable = variable.replace('_adjusted', '')
    df_baseline[f'sd_{variable}']  = df_baseline[f'sd_{original_variable}']

  # Group by PSU to compute within-PSU variances
  df_group = df_baseline.groupby(['psu'])
  df_group = df_group[[variable, 'Sample Weight']].apply(lambda g: calculate_within_psu_variance(variable=variable, group=g)).reset_index(level=0, drop=True)
  df_baseline['within_psu_variance'] = df_group.loc[:, 'within_psu_variance']

  # Group by strata to compute the within strata variance between psu's in a stratum
  df_strata = df_baseline.groupby(['strata'])
  df_strata = df_strata[[variable, 'psu', 'Sample Weight']].apply(lambda g: calculate_between_psu_variance(variable=variable, group=g)).reset_index(level=0, drop=True)
  df_baseline['within_strata_variance'] = df_strata.loc[:, 'within_strata_variance']

  # Combine teh within psu and within strata variances to obtain an estimate of teh total variance within each stratum
  df_strata_total = df_baseline.groupby(['strata'])
  df_strata_total = df_strata_total[['psu','within_strata_variance', 'within_psu_variance']].apply(lambda g: stratum_variance(group=g)).reset_index(level=0, drop=True)
  df_baseline['strata variance'] = df_strata_total.loc[:, 'strata variance']

  # Estimate the survey variance over all strata
  survey_variance = survey_error_sum(df_baseline=df_baseline)

  # Estimate the variance from the within item uncertainty
  within_item_variance = (df_baseline['Sample Weight']**2 * df_baseline[f'sd_{variable}']**2).sum()

  # Combine the variances for the yearly estimate for the standard deviation
  sd = 365*(within_item_variance + survey_variance)**0.5

  weighted_sum = (df_baseline[f"{variable}"]*df_baseline['Sample Weight']).sum()*365
  ci_lower = weighted_sum - 1.96*sd
  ci_upper = weighted_sum + 1.96*sd

  print(f"Weighted Sum: {weighted_sum}")
  print(f"95% Confidence Interval: ({ci_lower}, {ci_upper})")

  return
  
  
  