import pandas as pd
import numpy as np
import os
import arviz as az
from scipy.stats import gaussian_kde
from mapping_dictionary import *
from pathlib import Path


class Dataset:
    def __init__(self, path):
        """
        Initialize the Dataset object with the path to the file.

        Parameters:
        - path (str): Path to the .parquet file.
        """
        self.path = path
        self.data = self._load_data()

    def _load_data(self):
        """
        Load the data from the provided path.
        """
        readers = {
            '.csv': pd.read_csv,
            '.pkl': pd.read_pickle,
            '.parquet': pd.read_parquet
        }

        _, file_extension = os.path.splitext(self.path)
        reader = readers[file_extension]

        if reader is None:
            raise ValueError(f"Unsupported file extension '{file_extension}' for path {self.path}")

        try:
            data = reader(self.path)
            return data

        except Exception as e:
            raise ValueError(f"Error loading data from {self.path}: {str(e)}")


class Individual_level_data(Dataset):

    def __init__(self, path):
        super().__init__(path)

    def load_inference_data(self, load_path: str):
        """
        Load InferenceData from a NetCDF file.
        """
        inference_data = az.from_netcdf(load_path)
        return inference_data

    def assign_posterior_samples(self, seed: int):

        """
        :param seed: random seed parameter
        :return: Dictionary containing random samples from each of the parameter
        posterior distributions of the imputed variables
        """

        posterior_path = Path("data/posterior_samples")

        inf_data_mapping = {'Weight': posterior_path / 'weight_posterior_shes_09032026.nc',
                            'Height': posterior_path / 'height_posterior_shes_09032026.nc',
                            'Total Cholesterol': posterior_path / 'totchol_nhanes_posterior_060326.nc',
                            'HDL Cholesterol': posterior_path / 'hdl_chol_posterior_nhanes_030826.nc',
                            'Systolic Blood Pressure': posterior_path / 'sbp_posterior_nhanes_08032926.nc'}

        post_samples_dict = {'Weight': {},
                             'Height': {},
                             'Total Cholesterol': {},
                             'HDL Cholesterol': {},
                             'Systolic Blood Pressure': {}}

        np.random.seed(seed)

        for variable in ['Weight', 'Height', 'Systolic Blood Pressure', 'HDL Cholesterol', 'Total Cholesterol']:
            inference_data = self.load_inference_data(inf_data_mapping[variable])

            params = list(inference_data.posterior.keys())

            num_chains = len(inference_data.posterior[params[0]])
            num_samples = len(inference_data.posterior[params[0]][0])

            chain_sample = np.random.randint(1, num_chains)
            sample = np.random.randint(num_samples)

            for param_name in inference_data.posterior.data_vars:
                post_samples_dict[variable][param_name] = float(inference_data.posterior[param_name][chain_sample][sample])


        return post_samples_dict

    def Physical_activity_sampling(self, variable: str, seed: int):

        # only 12 mising data in MVPA so impute by random sampling from th non-missing kde distribution

        np.random.seed(seed)

        n_missing = self.data[variable].isnull().sum()
        kde = gaussian_kde(self.data[variable].dropna())

        samples = kde.resample(n_missing).flatten()
        valid_samples = [sample for sample in samples if sample >= 0]

        while len(valid_samples) < n_missing:
            extra_samples = kde.resample(n_missing - len(valid_samples)).flatten()
            valid_samples.extend([sample for sample in extra_samples if sample >= 0])

        self.data.loc[self.data[variable].isnull(), variable] = valid_samples

        return

    def Weight_model(self, post_samples_dict: dict, seed: int):

        np.random.seed(seed)
        weight_samples = post_samples_dict['Weight']

        Sex = self.data['Sex']
        age = self.data['age']
        Taking_BPM = self.data['Taking BPM']
        
        self.data.loc[self.data['weight'].isnull(), 'weight'] = (((((((Sex * weight_samples['a5']) + age) + weight_samples['a3']) * (weight_samples['a2'] + age)) * weight_samples['a11']) + Taking_BPM) * weight_samples['a8'])

        self.data['weight'] = pd.to_numeric(self.data['weight'], errors='coerce') 

        if self.data['weight'].isnull().any():
            raise TypeError("NaN values found in 'weight' column")                                                               

        self.data.loc[self.data['initial weight'].isnull(), 'initial weight'] = self.data['weight']

        if self.data['weight'].isnull().any():
            raise TypeError("NaN values found in 'weight' column")

        return

    def Height_model(self, post_samples_dict, seed):

        np.random.seed(seed)
        height_samples = post_samples_dict['Height']

        Sex = self.data['Sex']
        age = self.data['age']
        white_OB = self.data['white_OB']

        self.data.loc[self.data['height'].isnull(), 'height'] = ((age * (age * height_samples['a9'])) + (
                ((white_OB + height_samples['a5']) * Sex) + height_samples['a7']))

        self.data['height'] = pd.to_numeric(self.data['height'], errors='coerce')

        if self.data['height'].isnull().any():
            raise TypeError("NaN values found in 'height' column") 

        return

    def SBP_model(self, post_samples_dict, seed):

        np.random.seed(seed)

        SBP_samples = post_samples_dict['Systolic Blood Pressure']

        Sex = self.data['Sex']
        Age = self.data['age']
        Weight = self.data['weight']
        #Height = self.data['height']
        high_bp_diagnosis = self.data['High BP']
        #BMI = self.data['BMI']

        # self.data['Systolic Blood Pressure'] = ((((((((SBP_samples['a8'] * Sex) + Weight) 
        #                                         + ((SBP_samples['a9'] / Height) * high_SBP)) 
        #                                         + (Age * ((BMI / Weight) 
        #                                         + (Age / Weight)))) ** SBP_samples['a0']) / SBP_samples['a3']) 
        #                                         + SBP_samples['a7']) * SBP_samples['a9'])
                                                
        self.data['Systolic Blood Pressure'] =  np.exp((((((Weight / (SBP_samples['a2'] + (SBP_samples['a5'] * Age))) + SBP_samples['a1']) + np.sqrt(Age)) * SBP_samples['a7']) + (-(high_bp_diagnosis) * SBP_samples['a6'])))

        self.data['Systolic Blood Pressure'] += np.random.normal(loc=0, 
                                                                 scale=SBP_samples['sigma'],
                                                                 size=len(self.data['Systolic Blood Pressure']))

                            

        return

    def HDL_cholesterol_model(self, post_samples_dict, seed):

        np.random.seed(seed)

        HDL_samples = post_samples_dict['HDL Cholesterol']

        Age = self.data['age']
        BMI = self.data['BMI']
        Sex = self.data['Sex']
        Smoker = self.data['Current Smoker']
        Diabetes = self.data['Diabetes']

        self.data['HDL Cholesterol'] = (((((((HDL_samples['a2'] ** (np.exp(np.array(BMI)) ** HDL_samples['a12'])) / -(
            HDL_samples['a0'])) * (-(HDL_samples['a0']) ** np.array(Sex))) + (HDL_samples['a4'] ** np.array(Age))) *
                                          HDL_samples['a2']) ** (
                                                 (HDL_samples['a8'] ** np.array(Diabetes)) * HDL_samples[
                                             'a12'])) + -((HDL_samples['a5'] + np.array(Smoker))))


        self.data['HDL Cholesterol'] += np.random.normal(loc=0, scale=HDL_samples['sigma'],
                                                         size=len(self.data['HDL Cholesterol']))

        # If the sampled HDL level is less than the minimum values in the NHANES training set, set to the minimum value
        mask = self.data['HDL Cholesterol'] < 6
        self.data.loc[mask, 'HDL Cholesterol'] = 6

        return

    def tot_cholesterol_model(self, post_samples_dict, seed):

        np.random.seed(seed)

        Sex = self.data['Sex']
        medication_high_BP = self.data['Taking BPM']
        Diabetes = self.data['Diabetes']
        Age = self.data['age']
        HDL_Cholesterol = self.data['HDL Cholesterol']
        SBP = self.data['Systolic Blood Pressure']

        total_chol_samples = post_samples_dict['Total Cholesterol']

        self.data['Total Cholesterol'] = ((((((total_chol_samples['a12'] + (
                (total_chol_samples['a7'] ** Sex) + total_chol_samples['a10'])) * (
                                                      ((np.array(medication_high_BP) + (
                                                              np.array(Diabetes) ** total_chol_samples['a3'])) /
                                                       total_chol_samples['a2']) *
                                                      total_chol_samples['a7'])) + total_chol_samples['a0']) / np.array(
            Age)) ** (total_chol_samples['a4'] + (
                (np.array(Age) * total_chol_samples['a10']) * (
                (total_chol_samples['a3'] * (np.array(medication_high_BP + SBP))) ** (
                total_chol_samples['a12'] * (total_chol_samples['a6'] + np.array(HDL_Cholesterol))))))) *
                                          total_chol_samples['a8'])

        self.data['Total Cholesterol'] += np.random.normal(loc=0, scale=total_chol_samples['sigma'],
                                                           size=len(self.data['Total Cholesterol']))

        # ensure that no values are lower than the minumum value in the training data
        mask = self.data['Total Cholesterol'] < 69
        self.data.loc[mask, 'Total Cholesterol'] = 69

        return

    def impute_missing_data(self, seed):

        post_samples_dict = self.assign_posterior_samples(seed=seed)

        self.Physical_activity_sampling(variable='Avg Mins MVPA per week', seed=seed)
        self.Height_model(post_samples_dict=post_samples_dict, seed=seed)
        self.Weight_model(post_samples_dict=post_samples_dict, seed=seed)
        
        # recalculate BMI based on height and weight data 
        self.data['BMI'] = self.data['weight'] / ((self.data['height'] / 100) ** 2)
        
        self.SBP_model(post_samples_dict=post_samples_dict, seed=seed)
        self.HDL_cholesterol_model(post_samples_dict=post_samples_dict, seed=seed)
        self.tot_cholesterol_model(post_samples_dict=post_samples_dict, seed=seed)
    
        return post_samples_dict

    def initialise_BMI(self, years):

        height = self.data['height'] / 100

        for year in range(1, years + 1):
            self.data[f'BMI year {year}'] = self.data['weight'] / height ** 2

        return


class Food_item_level_data(Dataset):

    def __init__(self, path):
        super().__init__(path)


    def reduction_percentage(self, percent_reduction, food_group_reductions):

        """
        :param percent_reduction: Percentage reduction to apply
        :param food_group_reductions: Food groups to apply the percentage reduction to

        """

        # Applies the fixed percentage reduction at the food item level
        for i in food_group_reductions:
            self.data.loc[:, i + '_reduction'] = (percent_reduction / 100) * self.data[i]

        return

    def reduction_to_cutoff_random(self, cutoff: float, min_reduction: float, baseline_intake: pd.DataFrame, food_groups_to_reduce:list, seed:int):

        """
        Calculates the necessary reduction among all food groups in food_groups_to_reduce such that their average daily intake is no greater than the cutoff
        :param cutoff: Maximum daily intake of all foods in food_groups_to_reduce
        :param min_reduction: Incremental gram reduction of each food group
        :param baseline_intake: dataframe of the baseline intake of nutrients and good groups
        :param food_groups_to_reduce: list of food groups to consider in calculating a maximum daily intake
        :param seed: random seed parameter
        """



        np.random.seed(seed)

        # diet_data = diet_data.copy()
        exclude_items = ['Chicken and vegetable soup, homemade', 'Chicken liver', 'Chicken/turkey sausage']

        # extract the ids where a reduction in intake is necessary

        baseline_intake['white PM intake'] = baseline_intake.apply(lambda row: self.compute_white_PM_items(row), axis=1)
        baseline_intake['Total intake'] = baseline_intake[food_groups_to_reduce].sum(axis=1)

        # Account for white meat intake in assessing those individuals that experience a reduction.
        baseline_intake['Total intake'] -= baseline_intake['white PM intake']
        ids_to_reduce = baseline_intake[baseline_intake['Total intake'] > cutoff].index

        # initialise the variables that track the reduction at the item level
        food_group_reductions = []
        for i in food_groups_to_reduce:
            self.data[i + '_reduction'] = 0
            food_group_reductions.append(i + '_reduction')

        for id in ids_to_reduce:

            diet = self.data[self.data['Cpseriala'] == id]
            num_days = len(diet['RecallNo'].unique())

            max_consumption = cutoff * num_days  # so that the average consumption across all days equals the cutoff
            # print(max_consumption)

            # extract the columns that have a positive value in the food groups that could be reduced
            food_consumed = diet[(diet[food_groups_to_reduce] > 0).any(axis=1)]

            # manually exlcude the white meat items in Offalg and Sausagesg

            # Filter out rows with FoodDescription in exclude_items
            mask = ~food_consumed['FoodDescription'].isin(exclude_items)
            food_consumed = food_consumed[mask]

            # calculate the total amount of food consumed in the groups to be reduced at baseline
            total_food_consumed = food_consumed[food_groups_to_reduce].sum().sum()
            # calculate how many grams need to be shaved off to hit the cutoff across all food groups
            total_reduction = total_food_consumed - max_consumption
            # keep subtracting Xg from randomly selected food groups until the reduction reaches that needed for the cutoff
            count = 0

            while count < total_reduction:
                # Extract the food groups with non-zero consumption
                non_zero_columns = food_consumed[food_groups_to_reduce].columns[(food_consumed[food_groups_to_reduce] != 0).any()]
                # Randomly select one of these columns, e.g. Burgersg
                column = np.random.choice(non_zero_columns)
                # randomly select one of the items in this meat group
                non_zero_rows = food_consumed[food_consumed[column] > 0]
                # randomly select a food item to reduce
                row_index = np.random.choice(non_zero_rows.index.tolist())


                # add min_reduction to the gram weight of the reduction of the selected food group if there are more than min_reduction grams of that food group remaining
                if (count + min_reduction < total_reduction):
                    if self.data.loc[row_index, column + '_reduction'] < (self.data.loc[row_index, column] - min_reduction):
                        self.data.loc[row_index, column + '_reduction'] += min_reduction
                        count += min_reduction
                    else:
                        pass
                else:
                    break
            # Add the remainder for the remaining reduction
            remainder = total_reduction - count
            
            # Convert the reduction estiamtes to floats before including the remainder
            self.data[food_group_reductions] = self.data[food_group_reductions].astype(float)

            while count != total_reduction:
                non_zero_columns = food_consumed[food_groups_to_reduce].columns[(food_consumed[food_groups_to_reduce] !=0).any()]
                column = np.random.choice(non_zero_columns)
                non_zero_rows = food_consumed[food_consumed[column] > 0]
                row_index = np.random.choice(non_zero_rows.index.tolist())  # pick a food item to reduce

                if (self.data.loc[row_index, column] - self.data.loc[row_index, column + '_reduction']) - remainder >= 0:
                    
                    self.data.loc[row_index, column + '_reduction'] += remainder
                    count += remainder
                    break
                else:
                    pass

        if (self.data[food_group_reductions] < 0).any().any():
            raise ValueError('Magnitude of the reductions should not be negative')

        return

    def new_diet_data(self, row, food_groups_to_reduce, nutrients, df_nutrients, mapping_dict, items_to_ignore=[], dairy_reduction=None):

        """
        Computes the impact on nutrients at the food item level from the reductions computed from self.reduction_to_cutoff_random() or reduction_to_cutoff_percentage()
        :param row: Food item in item level dataset
        :param food_groups_to_reduce: list of food groups to apply the reduction to. E.g. "Beefg", "Milk_SemiSkimmed"
        :param nutrients: List of nutrients to apply the reduction to
        :param df_nutrients: Nutrients per gram of each noncomposite meat or dairy item
        :param mapping_dict: Mapping between the composite meat/dairy item and the associated meat/dairy ingredient
        :param items_to_ignore: Optional. Specify a list of individual food items in the dietary data to ignore in calculating the impact on nutrients
        :param dairy_reduction: The percent reduction in dairy
        :return:
        """

        for variable in food_groups_to_reduce:
            if row[variable + '_reduction'] > 0:
                reduction = row[variable + '_reduction']
                desc = row['FoodDescription']
                food_code = row['FoodNumber']

                # Do not include the reduction in nutrients from a list if items to ignore. For the reductions among high consumers of red meat these include processed white meat items

                if desc not in items_to_ignore:
                    # If applying the reduction of dairy items
                    if 'Milk_Skimmed' in mapping_dict.keys():
                        item_mapping = mapping_dict[variable]

                        if food_code not in df_nutrients.index:
                            ing_list = item_mapping[str(food_code)]
                        elif food_code in df_nutrients.index:
                            ing_list = [food_code]
                        else:
                            raise ValueError('Reported food code does not have ingredient data')

                        for nutr in nutrients:
                            for ing in ing_list:
                                if len(ing_list)>1:
                                    row[nutr] -= ((dairy_reduction/100) * row[variable] * df_nutrients.loc[ing, nutr])*dairy_ingredient_proportion_dict[variable][str(food_code)][ing]
                                else:
                                    row[nutr] -= ((dairy_reduction / 100) * row[variable] * df_nutrients.loc[ing, nutr])

                            # If the reduction in nutrients exceeds the total nutrient count, set to zero. Can occur due to the approximation in meat mapping
                            if row[nutr] < 0:
                                row[nutr] = 0



                    # Evaluates impact on meat groups from the ingredient mapping
                    elif 'Beefg' in mapping_dict.keys():
                        # no nearest neighbour matches for offal items. As an approx use the gram weight reduction in offal to reduce the gram weight of the whole item by that gram weight.
                        if variable == "Offalg":
                            # calculate nutrients per gram of whole item consumed
                            nutr_per_gram_offal_item = row[nutrients] / row['TotalGrams']
                            # For each nutrient take off the associated nutrients from the gram weight of the reduction
                            row[nutrients] -= row["Offalg_reduction"] * nutr_per_gram_offal_item
                        else:
                            item_mapping = mapping_dict[variable]
                            try:
                                nn = item_mapping[desc]
                            except:
                                nn = desc

                            for nutr in nutrients:
                                row[nutr] -= reduction * df_nutrients.loc[nn, nutr]
                                # If the reduction in nutrients exceeds the total nutrient count, set to zero. Can occur due to the approximation in meat mapping
                                if row[nutr] < 0:
                                    row[nutr] = 0
                    else:
                        raise ValueError('No composite or ingredient item exists -> check the mapping dictionary')

                    # take of the corresponding value of the reduction from the food group in question
                    row[variable] -= reduction

                    if row[variable] < 0:
                        raise ValueError('Magnitude of the reduction cannot be greater than that currently consumed')

            else:
                pass


        return row

    def compute_white_PM_items(self, row):

        """
        :param row:
        :return: daily white processed meat consumption for each participant
        """

        white_offal = ['Chicken and vegetable soup, homemade', 'Chicken liver']
        white_sausage = ['Chicken/turkey sausage']

        # 'Chicken and prawn paella, ready meal, reduced fat'  also has sausage, but this might refer to the chorizo?

        id = float(row.name)
        diet = self.data[self.data['Cpseriala'] == id]
        num_days = len(diet['RecallNo'].unique())

        white_PM_consumption = 0

        white_PM_consumption += diet[diet['FoodDescription'].isin(white_offal)]['Offalg'].sum() / num_days
        white_PM_consumption += diet[diet['FoodDescription'].isin(white_sausage)]['Sausagesg'].sum() / num_days

        return white_PM_consumption

    def nutrient_intake(self, row, scenario_diet_data, nutrient_list):

        """

        :param row: row in the individual level data
        :param scenario_diet_data: Food item level dataset from which to compute the impact on nutrients
        :param nutrient_list: List of nutrients to compute the overall impact
        :return:
        """

        id = float(row.name)
        diet = scenario_diet_data[scenario_diet_data['Cpseriala'] == id]
        num_days = len(diet['RecallNo'].unique())

        for nutr in nutrient_list:
            row[nutr] = float(diet[nutr].sum()) / num_days

        return row

    def finalise_nutrient_intake(self, scenario_diet_data):

        nutr_final = nutrients + food_groups
        df = pd.DataFrame(index=scenario_diet_data['Cpseriala'].unique(), columns=nutr_final)
        df = df.apply(lambda row: self.nutrient_intake(row,
                                                       scenario_diet_data=scenario_diet_data,
                                                       nutrient_list=nutr_final),
                      axis=1)

        foods_RM = ['Beefg', 'Lambg', 'Burgersg', 'Porkg','OtherRedMeatg']
        foods_RPM = ['ProcessedRedMeatg', 'Sausagesg','Offalg']

        df['white PM intake'] = df.apply(lambda row: self.compute_white_PM_items(row), axis=1)
        df['Red meat intake'] = df[foods_RM].sum(axis=1)
        df['Processed meat intake'] = df[foods_RPM].sum(axis=1) - df['white PM intake']
        df['Total RRPM meat'] = df['Red meat intake'] + df['Processed meat intake']

        return df

    def nutrient_impact_item_level_reductions_percentage(self, diet_data, df_nutrients, food_group_reductions,
                                                         mapping_dict, dairy_reduction):

        scenario_diet_data = diet_data.apply(
            lambda row: self.new_diet_data(row,
                                           food_groups_to_reduce=food_group_reductions,
                                           nutrients=nutrients,
                                           df_nutrients=df_nutrients,
                                           items_to_ignore=[],
                                           mapping_dict=mapping_dict,
                                           dairy_reduction=dairy_reduction),
            axis=1)

        return scenario_diet_data

    def nutrient_impact_item_level_reductions_cutoff(self,  food_groups_to_reduce, df_nutrients, mapping_dict):

        white_PM_items = ['Chicken and vegetable soup, homemade', 'Chicken liver', 'Chicken/turkey sausage']

        scenario_diet_data = self.data.apply(
            lambda row: self.new_diet_data(row, food_groups_to_reduce=food_groups_to_reduce, nutrients=nutrients,
                                           df_nutrients=df_nutrients, mapping_dict=mapping_dict,
                                           items_to_ignore=white_PM_items),
            axis=1)

        return scenario_diet_data
