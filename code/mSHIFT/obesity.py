import numpy as np


def Resting_Metabolic_Rate(row):

  weight = row['initial weight']
  height = row['height']
  age = row['age']

  if row['Sex'] == 0:
      #male
      RMR = 10*weight + 6.25*height -4.92*age + 5  # weight (kg), height (cm), age (yr)  -- kcal/day
  else:
      #female
      RMR = 10*weight + 6.25*height -4.92*age -161

   #convert to kJ
  RMR = 4.18*RMR

  return RMR


def welk_recalibration(row):
    
    """
    Applies the calibration equations to adjust self reported moderate PA to measured values, taken from in Table 2 of Calibration of Self-Report Measures of Physical Activity and Sedentary Behavior, Welk et. al 2017, using the equation that does not include education level as a covariate.  
    """

    mvpa = row['MVPA']
  # Only apply the regression to participans with moderate physical activity self-report.
    if abs(mvpa) < 1e-4:
        return 0
    else:
        sed = row['Sedentary non-sleep']
        sex = row['Sex'] # 1: Female, 0: Male
        age = row['age']
        BMI = row['BMI']
        
        params = {'mvpa': {'param': 0.211,
                               'se':0.016},
    
                      'sed': {'param': -1.117,
                               'se':0.271},
    
                      'sex': {'param': 0.537,
                              'se': 0.239},
    
                      'age': {'param': -0.017,
                              'se': 0.002},
    
                      'BMI': {'param': -0.183,
                              'se': 0.054},
    
                      'sed_BMI': {'param': 0.024,
                              'se': 0.009},
    
                      'sex_BMI': {'param': -0.045,
                                  'se': 0.008}
                      }
        
        mvpa_sample = params['mvpa']['param']
        sed_sample = params['sed']['param']
        sex_sample = params['sex']['param']
        age_sample = params['age']['param']
        BMI_sample = params['BMI']['param']
        sed_BMI_sample = params['sed_BMI']['param']
        sex_BMI_sample = params['sex_BMI']['param']
        
        intercept = 12.504 
        
        mu = intercept + (mvpa_sample*np.log(mvpa)) + (sed_sample*np.log(sed)) + (sex_sample*sex) + (age_sample*age) + (BMI_sample*BMI) + (sed_BMI_sample*np.log(sed)*BMI) + (sex_BMI_sample*sex*BMI)
        mvpa_calibrated = np.exp(mu)
        
        return mvpa_calibrated


### Setting a cap on maximum daily mdoerate and vig activity -- still have outliers -- NOT USED ###
def Physical_Activity_Level(row, rng):

    weight = row['initial weight']
    height = row['height']
    age = row['age']
    sex= row['Sex']

    mpa = row['Moderate PA']
    vpa = row['Vigorous PA']
    sed_non_sleep = row['Sedentary non-sleep']
    
    met_min_dict = {'Moderate PA': mpa,
                    'Vigorous PA': vpa,
                    'Sedentary non-sleep': sed_non_sleep,
                    'Sedentary sleep': 420  # Assume 7 hours sleep per night on average
    }
    
    # Equations from Gerrior et al 2006
    # Units of kcal. Assumes the height is in cm, age in yrs, weight in kgs
    if sex==0:
        # male
        BEE = 293-3.8*age + 4.564*height + 10.12*weight    
    else:
        # female
        BEE = 247-2.67*age + 4.015*height + 8.6*weight
        
    #Daily resting O2 consumption (ml/(kg*min)) : assuming 1000mlO2/5kcal ==> (BEE (kcal/day)* (1/1440) * (1000/5)) = BEE/7.2  (ml/min)
    resting_VO2 = BEE / (7.2 * weight)
    
    # Kozey et al 2010 correction factor that adjusts MET scores for different activities based on resting_VO2. 
    correction_factor = min(resting_VO2 / 3.5, 1.0)
    
    MET_dict = {
        'Moderate PA': (3.0 + rng.beta(a=2, b=5))*correction_factor,  
        'Vigorous PA': (6.0 + rng.beta(a=2, b=5))*correction_factor,   
        'Sedentary non-sleep': max((1.1 + 1.5 * rng.beta(a=2.5, b=6))*correction_factor, 1.11), # ensure that sedentary non-sleep does not fall below the limit of a non-sleep MET score.
        'Sedentary sleep': 1.0
    }

    DeltaPAL = 0

    denominator = BEE/(0.0175*1440*weight)

    total_mins = 0
    for activity in MET_dict.keys():
        
        mins_spent = met_min_dict.get(activity)
        total_mins += mins_spent

        numerator = (MET_dict[activity] - 1)*((1.15/0.9)*mins_spent)/1440
        DeltaPAL_i = numerator/denominator
        DeltaPAL += DeltaPAL_i
        
    if abs(total_mins-1440) > 1e-3:
        print(f"Total mins: {total_mins}, ID: {row.name}")
        raise ValueError("Error in total daily minutes")
         
    PAL = 1.1 + DeltaPAL
    # Cap the maximum daily PAL at 2.2 - above this is elitle athlete territory
    PAL = np.clip(PAL, 1.111, 2.2)
    
    return PAL


def Phys_Act_Energy_Expenditure(row):

    initial_weight = row['initial weight']
    #PAL = Physical_Activity_Level(row, seed, rng)
    # PAL now calculated initially in the run_sampling function
    PAL = row['PAL']
    delta = ((0.9*PAL - 1)*Resting_Metabolic_Rate(row)) / initial_weight

    return delta
    
def calculate_initial_fat_mass(row):
    """
    Estimates initial fat mass (F0) using Jackson et al. equations 
    as defined in the Hall 2011 paper.
    """
    BW = row['initial weight'] # in kg
    H = row['height'] / 100    # convert cm to meters
    age = row['age']
    
    # BMI formulation used inside the log: BW / H^2
    bmi_factor = np.log(BW / (H**2))
    
    if row['Sex'] == 0:
        # Male
        F0 = (BW / 100) * (0.14 * age + 37.31 * bmi_factor - 103.94)
    else:
        # Female
        F0 = (BW / 100) * (0.14 * age + 39.96 * bmi_factor - 102.01)
        
    return F0

def constants_for_Hall_eqn(row, seed):
    """
    Calculates rho and epsilon strictly using kJ and kg to avoid unit mismatch.
    """
    F0 = calculate_initial_fat_mass(row)
    
    # Constants from Hall et al 2011 supplementary material
    eta_f = 750        # Fat synthesis efficiency (kJ/kg)
    rho_f = 39500      # Energy content of fat (kJ/kg)
    eta_l = 960        # Protein synthesis efficiency (kJ/kg)
    rho_l = 7600       # Energy content of lean tissue (kJ/kg)
    beta = 0.24        # Adaptive thermogenesis + TEF (0.14 + 0.1)
    gamma_l = 92       # RMR of lean tissue (kJ/kg/day)
    gamma_f = 13       # RMR of fat tissue (kJ/kg/day)
    
    # Forbes parameter, linear approximation relies on initial fat mass
    alpha = 10.4 / F0  
    delta_i = Phys_Act_Energy_Expenditure(row)     
    
    # Effective energy density (rho)
    rho = (eta_f + rho_f + alpha * (eta_l + rho_l)) / ((1 - beta) * (1 + alpha))
    
    # Energy expenditure dependence on BW (epsilon)
    x = (gamma_f + alpha * gamma_l) / (1 + alpha)
    epsilon = (1 / (1 - beta)) * (delta_i + x)

    return rho, epsilon



def update_weight(row, year, seed):
    """
    Solves the linearized differential equation for weight change over time.
    """
    rho, epsilon = constants_for_Hall_eqn(row, seed)
    M0 = row['initial weight']
    
    # chi must be in kJ/day, derivied from the decrease in energy intake from meat and dairy
    chi = row['Change in energy kJ'] 
    
    # Solution to the linearsied Hall equation for weight loss given a hange in energy intake and physical activity level
    weight = M0 + (chi / epsilon) * (1 - np.exp(-365 * year * epsilon / rho))
    
    return np.round(weight, 3)

def compute_BMI(row, year):
    height = row['height'] / 100
    BMI = row[f'weight year {year}'] / height ** 2
    return BMI