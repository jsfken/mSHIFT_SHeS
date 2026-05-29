import pandas as pd
import numpy as np 
import regex as re


def load_data(path_to_data):

  if path_to_data.endswith('.csv'):
    try:
      data = pd.read_csv(path_to_data, low_memory=False, encoding = 'IBM819')
    except:
      print('try different encoding')

  return data
  
# define a function to convert a string to a float if it contains a float
def convert_to_float(row: pd.Series, 
                     variable: str):
                         
  s=row[variable]
  pattern = re.compile(r'^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$')
  if pattern.match(s):
      return float(s)
  else:
      return np.nan

def add_sex(row: pd.Series):

  value = row['Sex']
  if value == 'Male':
    value=0
  elif value == 'Female':
    value=1
  else:
    value = np.nan

  return value

def add_height(row: pd.Series):

  value = row['Height']

  if value == 'Not applicable':
    return np.nan
  else:
    value = convert_to_float(value)
    return value

def convert_binary(row: pd.Series, variable: str):

  value = row[variable]
  if value == 'Yes' or value == 'Taking drug' or value == 'Drank in the last 12 months and in the last week':
    return 1
  elif value == 'No':
    value = 0
  else:
    return np.nan

def convert_binary_no_nan(row: pd.Series, variable: str):

  value = row[variable]
  if value == 'Yes' or value == 'Taking drug' or value == 'Drank in the last 12 months and in the last week' or value == 1.0:
    return 1
  else:
    value = 0
  return value


def income(df: pd.DataFrame):
    
    # Creating new columns based on SIMD_labels
  inc_mapping = {
    '£10,400<£13,000': ('income<20', 1),
    '£13,000<£15,600': ('income<20', 1),
    '£33,800<£36,400': ('20<income<50', 1),
    '£60,000<£70,000': ('50<income<100', 1),
    '£150,000+': ('100<income', 1),
    '£20,800<£23,400': ('20<income<50', 1),
    '£5,200<£7,800': ('income<20', 1),
    '£7,800<£10,400': ('income<20', 1),
    '£36,400<£41,600': ('20<income<50', 1),
    'Refused': ('20<income<50', 1),
    '£18,200<£20,800': ('income<20', 1),
    "Don't know": ('20<income<50', 1),
    '£31,200<£33,800': ('20<income<50', 1),
    '£78,000<£90,000': ('50<income<100', 1),
    '£46,800<£52,000': ('20<income<50', 1),
    '£15,600<£18,200': ('income<20', 1),
    '£26,000<£28,600': ('20<income<50', 1),
    '£110,000<£120,000': ('100<income', 1),
    '£28,600<£31,200': ('20<income<50', 1),
    '£3,600<£5,200': ('income<20', 1),
    '£52,000<£60,000': ('50<income<100', 1),
    '£23,400<£26,000': ('20<income<50', 1),
    '£120,000<£130,000': ('100<income', 1),
    '£90,000<£100,000': ('50<income<100', 1),
    '£41,600<£46,800': ('20<income<50', 1),
    '£70,000<£78,000': ('50<income<100', 1),
    '£2,600<£3,600': ('income<20', 1),
    '£1,600<£2,600': ('income<20', 1),
    '£130,000<£140,000': ('100<income', 1),
    '£100,000<£110,000': ('100<income', 1),
    '£140,000<£150,000': ('100<income', 1),
    'Not applicable': ('20<income<50', 1)
}


  for new_col in ['income<20','20<income<50' ,'50<income<100', '100<income']:
      df[new_col] = 0

  for index, row in df.iterrows():
      label = row['totinc']
      if label in inc_mapping:
          col, value = inc_mapping[label]
          df.at[index, col] = value

  return df

def SIMD(df: pd.DataFrame):
    
    # Creating new columns based on SIMD_labels
  simd_mapping = {
      'Most deprived': ('SIMD1', 1),
      '4th': ('SIMD2', 1),
      '3rd': ('SIMD3', 1),
      '2nd': ('SIMD4', 1),
      'Least deprived': ('SIMD5', 1)
  }

  for new_col in ['SIMD1', 'SIMD2', 'SIMD3', 'SIMD4', 'SIMD5']:
      df[new_col] = 0

  for index, row in df.iterrows():
      label = row['SIMD_labels']
      if label in simd_mapping:
          col, value = simd_mapping[label]
          df.at[index, col] = value

  return df

def ethnicity(df: pd.DataFrame):

    # Creating new columns based on SIMD_labels
  eth_mapping = {
      'White: Scottish': ('white_scot', 1),
      'White: Other British': ('white_OB', 1),
      'Asian': ('asian', 1),
      'White: Other': ('white_oth', 1),
      'Other minority ethnic': ('oth_min_eth', 1)
  }

  for new_col in ['white_scot', 'white_OB', 'asian', 'white_oth', 'oth_min_eth']:
      df[new_col] = 0

  for index, row in df.iterrows():
      label = row['eth']
      if label in eth_mapping:
          col, value = eth_mapping[label]
          df.at[index, col] = value

  return df


def add_variable(row: pd.Series, variable: str, core_data: pd.DataFrame):

  id = row.name
  ind = core_data[core_data['Cpseriala']==id]
  value = ind[variable].values[0]

  return value
  
  
def healthy(row):

  if row['Diabetes'] == 1:
    value = 0
  elif row['CVD'] == 1:
    value = 0
  else:
    value = row['Sample Weight']

  return value
  
