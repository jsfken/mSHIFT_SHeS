


def expected_new_diabetes_cases(row):

    exp_cases = 0

    if row['Diabetes'] != 1:
        exp_cases = row['Diabetes risk'] * (row['Sample Weight'] - row['New diabetes cases'])
    else:
        pass

    return exp_cases


def expected_new_CVD_cases(row):
    exp_cases = 0

    if row['CVD'] != 1:
        if row['Diabetes'] != 1:
            exp_cases += row['CVD risk no diabetes'] * (
                        row['Sample Weight'] - row['New diabetes cases'] - row['New CVD cases'] + row[
                    'New diabetes and CVD cases'])
            exp_cases += row['CVD risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CVD cases'])
        else:
            exp_cases += row['CVD risk with diabetes'] * (row['Sample Weight'] - row['New CVD cases'])
    else:
        pass

    return exp_cases


def expected_new_CRC_cases(row):
    exp_cases = 0

    if row['CRC'] != 1:
        if row['Diabetes'] != 1:
            exp_cases += row['CRC risk no diabetes'] * (
                        row['Sample Weight'] - row['New diabetes cases'] - row['New CRC cases'] + row[
                    'New diabetes and CRC cases'])
            exp_cases += row['CRC risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CRC cases'])
        else:
            exp_cases += row['CRC risk with diabetes'] * (row['Sample Weight'] - row['New CRC cases'])
    else:
        pass

    return exp_cases


def expected_new_diabetes_CVD_cases(row):
    exp_cases = 0

    if row['CVD'] != 1 and row['Diabetes'] != 1:
        exp_cases += row['Diabetes and CVD risk'] * (
                    row['Sample Weight'] - row['New diabetes cases'] - row['New CVD cases'] + row[
                'New diabetes and CVD cases'])
        exp_cases += row['Diabetes risk'] * (row['New CVD cases'] - row['New diabetes and CVD cases'])
        exp_cases += row['CVD risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CVD cases'])

    elif row['CVD'] == 1 and row['Diabetes'] != 1:
        exp_cases += row['Diabetes risk'] * (row['Sample Weight'] - row['New diabetes cases'])
    elif row['CVD'] != 1 and row['Diabetes'] == 1:
        exp_cases += row['CVD risk with diabetes'] * (row['Sample Weight'] - row['New CVD cases'])
    else:
        pass

    return exp_cases


def expected_new_diabetes_CRC_cases(row):
    exp_cases = 0

    if row['CRC'] != 1 and row['Diabetes'] != 1:
        exp_cases += row['Diabetes and CRC risk'] * (
                    row['Sample Weight'] - row['New diabetes cases'] - row['New CRC cases'] + row[
                'New diabetes and CRC cases'])
        exp_cases += row['Diabetes risk'] * (row['New CRC cases'] - row['New diabetes and CRC cases'])
        exp_cases += row['CRC risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CRC cases'])

    elif row['CRC'] == 1 and row['Diabetes'] != 1:
        exp_cases += row['Diabetes risk'] * (row['Sample Weight'] - row['New diabetes cases'])

    elif row['CRC'] != 1 and row['Diabetes'] == 1:
        exp_cases += row['CRC risk with diabetes'] * (row['Sample Weight'] - row['New CRC cases'])
    else:
        pass

    return exp_cases


def expected_new_CVD_CRC_cases(row):
    exp_cases = 0

    if row['Diabetes'] == 1:
        if row['CRC'] != 1 and row['CVD'] != 1:
            exp_cases += row['CVD and CRC risk with diabetes'] * (
                        row['Sample Weight'] - row['New CVD cases'] - row['New CRC cases'] + row[
                    'New CVD and CRC cases'])
            exp_cases += row['CVD risk with diabetes'] * (row['New CRC cases'] - row['New CVD and CRC cases'])
            exp_cases += row['CRC risk with diabetes'] * (row['New CVD cases'] - row['New CVD and CRC cases'])
        elif row['CRC'] == 1 and row['CVD'] != 1:
            exp_cases += row['CVD risk with diabetes'] * (row['Sample Weight'] - row['New CVD cases'])

        elif row['CRC'] != 1 and row['CVD'] == 1:
            exp_cases += row['CRC risk with diabetes'] * (row['Sample Weight'] - row['New CRC cases'])
        else:
            pass
    else:
        if row['CRC'] != 1 and row['CVD'] != 1:
            # risk of getting both CVD and CRC in one year, not having diabetes
            exp_cases += row['CVD and CRC risk no diabetes'] * row['healthy']
            # risk of getting CVD and CRC for people who just have diabetes
            exp_cases += row['CVD and CRC risk with diabetes'] * (
                        row['New diabetes cases'] - row['New diabetes and CVD cases'] - row[
                    'New diabetes and CRC cases'] + row['New diabetes and CVD and CRC cases'])
            # Risk of getting CRC among those that just have CVD
            exp_cases += row['CRC risk no diabetes'] * (
                        row['New CVD cases'] - row['New CVD and CRC cases'] - row['New diabetes and CVD cases'] + row[
                    'New diabetes and CVD and CRC cases'])
            # Risk of getting CRC among those that have diabetes and CVD
            exp_cases += row['CRC risk with diabetes'] * (
                        row['New diabetes and CVD cases'] - row['New diabetes and CVD and CRC cases'])
            # Risk of getting CVD among those that just have CRC
            exp_cases += row['CVD risk no diabetes'] * (
                        row['New CRC cases'] - row['New CVD and CRC cases'] - row['New diabetes and CRC cases'] + row[
                    'New diabetes and CVD and CRC cases'])
            # Risk of getting CVD among those that have diabetes and CRC
            exp_cases += row['CVD risk with diabetes'] * (
                        row['New diabetes and CRC cases'] - row['New diabetes and CVD and CRC cases'])


        elif row['CRC'] == 1 and row['CVD'] != 1:
            exp_cases += row['CVD risk no diabetes'] * (
                        row['Sample Weight'] - row['New diabetes cases'] - row['New CVD cases'] + row[
                    'New diabetes and CVD cases'])
            exp_cases += row['CVD risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CVD cases'])

        elif row['CRC'] != 1 and row['CVD'] == 1:
            exp_cases += row['CRC risk no diabetes'] * (
                        row['Sample Weight'] - row['New CRC cases'] - row['New diabetes cases'] + row[
                    'New diabetes and CRC cases'])
            exp_cases += row['CRC risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CRC cases'])
        else:
            pass

    return exp_cases


def expected_new_diabetes_CVD_CRC_cases(row):
    exp_cases = 0

    if row['Diabetes'] == 1:
        if row['CRC'] != 1 and row['CVD'] != 1:
            exp_cases += row['CVD and CRC risk with diabetes'] * (
                        row['Sample Weight'] - row['New CVD cases'] - row['New CRC cases'] + row[
                    'New CVD and CRC cases'])
        elif row['CRC'] == 1 and row['CVD'] != 1:
            exp_cases += row['CVD risk with diabetes'] * (row['Sample Weight'] - row['New CVD cases'])
        elif row['CRC'] != 1 and row['CVD'] == 1:
            exp_cases += row['CRC risk with diabetes'] * (row['Sample Weight'] - row['New CRC cases'])
        else:
            pass

    else:
        if row['CRC'] != 1 and row['CVD'] != 1:
            # start healthy and get all three diseases in one year
            exp_cases += row['Diabetes and CVD and CRC risk'] * row['healthy']
            # Those that get diabetes after getting CVD and CRC in previous years
            exp_cases += row['Diabetes risk'] * (
                        row['New CVD and CRC cases'] - row['New diabetes and CVD and CRC cases'])
            # Those that get CRC after getting diabetes and CVD in previous years
            exp_cases += row['CRC risk with diabetes'] * (
                        row['New diabetes and CVD cases'] - row['New diabetes and CVD and CRC cases'])
            # Those that get CVD after getting diabetes and CVD in previous years
            exp_cases += row['CVD risk with diabetes'] * (
                        row['New diabetes and CRC cases'] - row['New diabetes and CVD and CRC cases'])
            # Those that get diabetes and CRC in one year after getting CVD only in previous years
            exp_cases += row['Diabetes and CRC risk'] * (
                        row['New CVD cases'] - row['New CVD and CRC cases'] - row['New diabetes and CVD cases'] + row[
                    'New diabetes and CVD and CRC cases'])
            # Those that get CRC and CVD in one year after getting diabetes only in previous years
            exp_cases += row['CVD and CRC risk with diabetes'] * (
                        row['New diabetes cases'] - row['New diabetes and CRC cases'] - row[
                    'New diabetes and CVD cases'] + row['New diabetes and CVD and CRC cases'])
            # Those that get diabetes and CVD after only getting CRC in a previous year
            exp_cases += row['Diabetes and CVD risk'] * (
                        row['New CRC cases'] - row['New CVD and CRC cases'] - row['New diabetes and CRC cases'] + row[
                    'New diabetes and CVD and CRC cases'])

        elif row['CRC'] == 1 and row['CVD'] != 1:
            # New diabetes and CVD cases among those that have neither diabetes nor CVD
            exp_cases += row['Diabetes and CVD risk'] * (
                        row['Sample Weight'] - row['New diabetes cases'] - row['New CVD cases'] + row[
                    'New diabetes and CVD cases'])
            # New diabetes cases among those that previous just aquired CVD
            exp_cases += row['Diabetes risk'] * (row['New CVD cases'] - row['New diabetes and CVD cases'])
            # New CVD cases among those that previous just aquired diabetes
            exp_cases += row['CVD risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CVD cases'])

        elif row['CRC'] != 1 and row['CVD'] == 1:
            # New diabetes and CRC cases among those that still just have CVD
            exp_cases += row['Diabetes and CRC risk'] * (
                        row['Sample Weight'] - row['New diabetes cases'] - row['New CRC cases'] + row[
                    'New diabetes and CRC cases'])
            # New diabetes cases among those that previous just aquired CRC
            exp_cases += row['Diabetes risk'] * (row['New CRC cases'] - row['New diabetes and CRC cases'])
            # New CVD cases among those that previous just aquired diabetes
            exp_cases += row['CRC risk with diabetes'] * (row['New diabetes cases'] - row['New diabetes and CRC cases'])

        else:
            pass

    return exp_cases


def healthy_pop(row):

    healthy = 0

    if row['Diabetes'] == 1 or row['CVD'] == 1 or row['CRC'] == 1:
        pass
    else:
        with_disease = row['New diabetes cases'] + row['New CVD cases'] + row['New CRC cases'] - row[
            'New diabetes and CVD cases'] - row['New diabetes and CRC cases'] - row['New CVD and CRC cases'] + row[
                           'New diabetes and CVD and CRC cases']
        healthy = row['Sample Weight'] - with_disease

    return healthy