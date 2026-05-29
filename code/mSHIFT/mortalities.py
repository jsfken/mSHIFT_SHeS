import numpy as np


mortality_table = {0: {0: 0.003455, 1: 0.000234, 2: 0.000131, 3: 0.000104, 4: 5.7e-05,
                            5: 5.6e-05, 6: 6.6e-05, 7: 5.4e-05, 8: 8.6e-05, 9: 3.2e-05,
                            10: 0.000108, 11: 8.7e-05, 12: 0.0001, 13: 9.1e-05, 14: 0.000195,
                            15: 0.000222, 16: 0.000406, 17: 0.000562, 18: 0.00075, 19: 0.000604,
                            20: 0.000593, 21: 0.000755, 22: 0.000706, 23: 0.000903, 24: 0.000906,
                            25: 0.001046, 26: 0.000928, 27: 0.000897, 28: 0.001069, 29: 0.001251,
                            30: 0.001149, 31: 0.001188, 32: 0.001471, 33: 0.001584, 34: 0.001706,
                            35: 0.001798, 36: 0.002163, 37: 0.002251, 38: 0.002166, 39: 0.002318,
                            40: 0.002773, 41: 0.003022, 42: 0.003124, 43: 0.003356, 44: 0.003614,
                            45: 0.003849, 46: 0.004412, 47: 0.003821, 48: 0.004312, 49: 0.004761,
                            50: 0.004784, 51: 0.004964, 52: 0.005508, 53: 0.005703, 54: 0.005896,
                            55: 0.005874, 56: 0.006803, 57: 0.007216, 58: 0.008131, 59: 0.008971,
                            60: 0.00941, 61: 0.010775, 62: 0.011864, 63: 0.012977, 64: 0.012623,
                            65: 0.015322, 66: 0.01636, 67: 0.017408, 68: 0.019163, 69: 0.02092,
                            70: 0.022447, 71: 0.024373, 72: 0.02702, 73: 0.029552, 74: 0.034599,
                            75: 0.039394, 76: 0.043128, 77: 0.047578, 78: 0.053299, 79: 0.059096,
                            80: 0.065635, 81: 0.07058, 82: 0.078341, 83: 0.088943, 84: 0.097022,
                            85: 0.106888, 86: 0.118068, 87: 0.130198, 88: 0.146281, 89: 0.164981,
                            90: 0.17234, 91: 0.193808, 92: 0.217899, 93: 0.219901, 94: 0.244077,
                            95: 0.268376, 96: 0.282451, 97: 0.299923, 98: 0.341686, 99: 0.330366, 100: 0.345324},

                   1: {0: 0.002878, 1: 0.000275, 2: 0.000127, 3: 0.000135, 4: 3.6e-05, 5: 3.5e-05,
                              6: 0.000116, 7: 7.9e-05, 8: 0.000101, 9: 3.3e-05, 10: 6.7e-05, 11: 5.7e-05,
                              12: 9.2e-05, 13: 9.5e-05, 14: 0.000133, 15: 0.00016, 16: 0.000176, 17: 0.00025,
                              18: 0.000303, 19: 0.000197, 20: 0.000249, 21: 0.000328, 22: 0.000348, 23: 0.000359,
                              24: 0.000328, 25: 0.000294, 26: 0.000264, 27: 0.000403, 28: 0.000453, 29: 0.000573,
                              30: 0.000482, 31: 0.00053, 32: 0.000706, 33: 0.000697, 34: 0.000844, 35: 0.000811,
                              36: 0.001117, 37: 0.001085, 38: 0.001082, 39: 0.001652, 40: 0.001554, 41: 0.001668,
                              42: 0.00161, 43: 0.002, 44: 0.001797, 45: 0.002078, 46: 0.002279, 47: 0.002466,
                              48: 0.002374, 49: 0.002581, 50: 0.002983, 51: 0.003169, 52: 0.003135, 53: 0.003476,
                              54: 0.003876, 55: 0.004085, 56: 0.004386, 57: 0.004834, 58: 0.005081, 59: 0.006079, 60: 0.00656,
                              61: 0.007066, 62: 0.007942, 63: 0.008068, 64: 0.00913, 65: 0.010515, 66: 0.010829, 67: 0.012136,
                              68: 0.012965, 69: 0.014384, 70: 0.015987, 71: 0.016698, 72: 0.019296, 73: 0.021451, 74: 0.024112,
                              75: 0.027602, 76: 0.029187, 77: 0.034152, 78: 0.038309, 79: 0.041441, 80: 0.046367, 81: 0.055412,
                              82: 0.059557, 83: 0.064741, 84: 0.074319, 85: 0.081573, 86: 0.096265, 87: 0.106511, 88: 0.119194,
                              89: 0.132388, 90: 0.151158, 91: 0.16676, 92: 0.185459, 93: 0.201369, 94: 0.224628, 95: 0.24461,
                              96: 0.259589, 97: 0.292501, 98: 0.304631, 99: 0.326948, 100: 0.379903}}

def mortality_prob(row, mortality_table, with_diabetes, with_CVD):

    age =row['age']
    sex =row['Sex']

    if age < 100:
        mortality_prob = mortality_table[sex][age]
    else:
        mortality_prob =0.99

    if with_CVD:
        RR_CVD = np.random.normal(2.0, 0.05)
        mortality_prob = mortality_prob *RR_CVD


    if with_diabetes:
        if age < 55:
            RR_Diabetes = np.random.normal(2.35, 0.085)
        elif age < 65:
            RR_Diabetes = np.random.normal(1.79, 0.03)
        elif age < 75:
            RR_Diabetes = np.random.normal(1.46, 0.015)
        else:
            RR_Diabetes = np.random.normal(1.19, 0.005)

        mortality_prob = mortality_prob *RR_Diabetes

    mortality_calibration_values = [
        (15, 19, 0.9),
        (20, 24, 1.02),
        (25, 29, 1.08),
        (30, 34, 1.2),
        (35, 39, 1.25),
        (40, 44, 1.05),
        (45, 49, 0.85),
        (50, 54, 1.53),
        (55, 59, 1.26),
        (60, 64, 1.6),
        (65, 69, 1.4),
        (70, 74, 1.44),
        (75, 79, 1.85),
        (80, 84, 1.13),
        (85, 89, 1.05),
        (90, 200, 0.6)
    ]


    for lower_bound, upper_bound, value in mortality_calibration_values:
        if lower_bound <= row['age'] <= upper_bound:
            mortality_prob /= value
            break  # exit loop once calibration is applied
        else:
            pass

    return mortality_prob

def CRC_mortality_prob(row):

    # age =row['Age']
    # sex =row['Sex']
    #
    # if sex == 0:
    #     if age < 50:
    #         mortality_probability = 0.0236
    #     elif age > 49 and age < 65:
    #         mortality_probability = 0.247
    #     elif age > 64 and age < 80:
    #         mortality_probability = 0.0226
    #     else:
    #         mortality_probability = 0.0796
    #
    # elif sex == 1:
    #     if age < 50:
    #         mortality_probability = 0.0426
    #     elif age > 49 and age < 65:
    #         mortality_probability = 0.0118
    #     elif age > 64 and age < 80:
    #         mortality_probability = 0.0347
    #     else:
    #         mortality_probability = 0.0308

    return 0


def expected_healthy_mortalities(row):
    expected_healthy_mortalities = 0

    if row['Diabetes'] == 1 or row['CVD'] == 1 or row['CRC'] == 1:
        pass
    else:
        expected_healthy_mortalities = row['healthy'] * row['Healthy mortality risk']

    return expected_healthy_mortalities


def expected_diabetes_mortalities(row):
    # Post-disease calculates additional mortalities among those that aquired the disease in that year
    ## Those that die that have diabetes, could have additional diseases ##

    exp_diabetes_mortalities = 0

    if row['CRC'] == 1 and row['Diabetes'] == 1:
        exp_diabetes_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    elif row['CRC'] == 1 and row['Diabetes'] != 1:
        exp_diabetes_mortalities += row['New diabetes and CRC cases'] * row['CRC mortality risk']

    elif row['Diabetes'] == 1 and row['CVD'] != 1:
        # Just have diabetes
        SW_diabetes_only = row['Sample Weight'] - row['New CRC cases'] - row['New CVD cases'] + row[
            'New CVD and CRC cases']
        exp_diabetes_mortalities += SW_diabetes_only * row['diabetes mortality risk']
        # New CVD cases without CRC
        exp_diabetes_mortalities += (row['New CVD cases'] - row['New CVD and CRC cases']) * row[
            'diabetes and CVD mortality risk']
        # New CRC cases
        exp_diabetes_mortalities += row['New CRC cases'] * row['CRC mortality risk']

    elif row['CVD'] == 1 and row['Diabetes'] != 1:
        exp_diabetes_mortalities += (row['New diabetes cases'] - row['New diabetes and CRC cases']) * row[
            'diabetes and CVD mortality risk']
        exp_diabetes_mortalities += row['New diabetes and CRC cases'] * row['CRC mortality risk']

    elif row['Diabetes'] == 1 and row['CVD'] == 1:
        exp_diabetes_mortalities += (row['Sample Weight'] - row['New CRC cases']) * row[
            'diabetes and CVD mortality risk']
        exp_diabetes_mortalities += row['New CRC cases'] * row['CRC mortality risk']

    elif row['Diabetes'] != 1 and row['CVD'] != 1:

        SW_diabetes_only = row['New diabetes cases'] - row['New diabetes and CRC cases'] - row[
            'New diabetes and CVD cases'] + row['New diabetes and CVD and CRC cases']
        exp_diabetes_mortalities += SW_diabetes_only * row['diabetes mortality risk']
        exp_diabetes_mortalities += (row['New diabetes and CVD cases'] - row['New diabetes and CVD and CRC cases']) * \
                                    row['diabetes and CVD mortality risk']
        exp_diabetes_mortalities += row['New diabetes and CRC cases'] * row['CRC mortality risk']

    return exp_diabetes_mortalities


def expected_CVD_mortalities(row):
    exp_mortalities = 0

    if row['CRC'] == 1 and row['CVD'] == 1:
        exp_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    elif row['CRC'] == 1 and row['CVD'] != 1:
        exp_mortalities += row['New CVD and CRC cases'] * row['CRC mortality risk']

    elif row['CVD'] == 1 and row['Diabetes'] != 1:
        # Just have CVD
        SW_CVD_only = row['Sample Weight'] - row['New CRC cases'] - row['New diabetes cases'] + row[
            'New diabetes and CRC cases']
        exp_mortalities += SW_CVD_only * row['CVD mortality risk']
        # New diabetes cases without CRC
        exp_mortalities += (row['New diabetes cases'] - row['New diabetes and CRC cases']) * row[
            'diabetes and CVD mortality risk']
        # New CRC cases
        exp_mortalities += row['New CRC cases'] * row['CRC mortality risk']

    elif row['Diabetes'] == 1 and row['CVD'] != 1:
        # New CVD cases
        exp_mortalities += (row['New CVD cases'] - row['New CVD and CRC cases']) * row[
            'diabetes and CVD mortality risk']
        # New CRC cases
        exp_mortalities += row['New CVD and CRC cases'] * row['CRC mortality risk']


    elif row['Diabetes'] == 1 and row['CVD'] == 1:
        exp_mortalities += (row['Sample Weight'] - row['New CRC cases']) * row['diabetes and CVD mortality risk']
        exp_mortalities += row['New CRC cases'] * row['CRC mortality risk']

    elif row['Diabetes'] != 1 and row['CVD'] != 1 and row['CRC'] != 1:
        SW_CVD_only = row['New CVD cases'] - row['New CVD and CRC cases'] - row['New diabetes and CVD cases'] + row[
            'New diabetes and CVD and CRC cases']
        exp_mortalities += SW_CVD_only * row['CVD mortality risk']
        exp_mortalities += (row['New diabetes and CVD cases'] - row['New diabetes and CVD and CRC cases']) * row[
            'diabetes and CVD mortality risk']
        exp_mortalities += row['New CVD and CRC cases'] * row['CRC mortality risk']

    return exp_mortalities


def expected_CRC_mortalities(row):
    exp_mortalities = 0

    if row['CRC'] == 1:
        exp_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    else:
        exp_mortalities += row['New CRC cases'] * row['CRC mortality risk']

    return exp_mortalities


def expected_diabetes_CVD_mortalities(row):
    exp_mortalities = 0

    if row['CRC'] == 1 and row['Diabetes'] == 1 and row['CVD'] == 1:
        exp_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    elif row['CRC'] == 1:
        exp_mortalities += row['New diabetes and CVD cases'] * row['CRC mortality risk']
    elif row['Diabetes'] == 1 and row['CVD'] == 1:
        exp_mortalities += (row['Sample Weight'] - row['New CRC cases']) * row[
            'diabetes and CVD mortality risk']
        exp_mortalities += row['New CRC cases'] * row['CRC mortality risk']
    else:
        exp_mortalities += (row['New diabetes and CVD cases'] - row['New diabetes and CVD and CRC cases']) * row[
            'diabetes and CVD mortality risk']
        exp_mortalities += row['New diabetes and CVD and CRC cases'] * row['CRC mortality risk']

    return exp_mortalities


def expected_diabetes_CRC_mortalities(row):
    exp_mortalities = 0

    if row['CRC'] == 1 and row['Diabetes'] == 1:
        exp_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    else:
        exp_mortalities += row['New diabetes and CRC cases'] * row['CRC mortality risk']

    return exp_mortalities


def expected_CVD_CRC_mortalities(row):
    exp_mortalities = 0

    if row['CRC'] == 1 and row['CVD'] == 1:
        exp_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    else:
        exp_mortalities += row['New CVD and CRC cases'] * row['CRC mortality risk']

    return exp_mortalities


def expected_diabetes_CVD_CRC_mortalities(row):
    exp_mortalities = 0

    if row['Diabetes'] == 1 and row['CRC'] == 1 and row['CVD'] == 1:
        exp_mortalities += row['Sample Weight'] * row['CRC mortality risk']
    else:
        exp_mortalities += row['New diabetes and CVD and CRC cases'] * row['CRC mortality risk']

    return exp_mortalities