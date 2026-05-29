# mSHIFT SHeS (Scottish Health Survey 2021)

## Overview

mSHIFT (micro-Simulation of the Health Impacts of Food Transformations) is a microsimulation that quantifies the impacts of dietary change on several indicators, including nutrient intake, cost, environmental and health outcomes. It was originally developed to quantify health outcomes following reductions in red and processed meat consumption in the United States ([Kennedy et al. 2024](https://www.thelancet.com/journals/lanplh/article/PIIS2542-5196%2824%2900118-9/fulltext)). In this version, we apply mSHIFT to data from the ([Scottish Health Survey (SHeS) 2021](https://www.gov.scot/publications/scottish-health-survey-2021-volume-1-main-report/)) to assess the impacts on several indicators should the [UK Climate Change Committee's recommendations for meat and dairy reduction] (https://www.theccc.org.uk/wp-content/uploads/2020/12/The-Sixth-Carbon-Budget-The-UKs-path-to-Net-Zero.pdf) be realised in the Scottish adult (16+) population via multiple dietary pathways. The associated publication can be found at https://doi.org/10.21203/rs.3.rs-5820769/v1

The file structure is as follows:

```
+---code
|   
|   +---mSHIFT # core simulation script for health impacts and nutrient intake   
|   \---notebooks # Data preparation, foodDB indicator analysis and results analysis.
|       \---notebook_code # Source code for running the scripts in the notebooks.  
+---data # Input data for the model and data produced in the data preparation notebooks.  
|   +---dairy_disag # Data needed for including dairy disaggregation
|   +---dairy_RR # Data for estimating the relative risk association of dairy intake and type-2 diabetes risk
|   +---demographic_groups # Data for extracting participants belonging to different demographic groups
|   +---foodDB_data_processing # Data for processing the matched foodDB data
|   +---indicator_lists # Lists of the relevant indicators used in the analysis.
|   +---mappings # A collection of useful dictionaries
|   +---NDB_data # Nutrient Databank 2022 data
|   +---posterior_samples # samples from the posterior distributions of the imputation models
|   +---shes_data_raw # Scottish health survey 2021 participant level and food item level data
|   \---substitute_items # Lists of bean items and oily fish items in SHeS used in the analysis of the weighted composite substitutes.
\---results #Results of the analysis will be stored here.
```
___


## How to run

This project is configured to run on the Code Ocean platform. If you wish to run the project in a different environment, please refer to the `Dockerfile` for the environment specification.

For full reproducibility take the following steps:

1. Launch a Jupyter notebook environment and run the notebooks NB1-NB10. Ensure that the notebooks are run in the order specified by the number at the start of the notebook description as some notebooks rely on output from other notebooks that should be run earlier in the analysis.
2. Perform a reproducible run via the main `run` script. This runs the health and nutrient simulations, the simulations of each foodDB indicator, the substitute analysis and the results analysis including some example plots and the supplementary tables.
3. Launch a Jupyter notebook environment and run the notebooks NB15 and NB16.

For the purposes of saving computational time, both the number of iterations which sample of the sources of uncertainty (the `end_seed` and `max_seed` parameters) and the number of years in the health simulations have been set to lower values that the submitted results. To fuly reproduce the results, the both the `end_seed` and `max_seed` parameters should be set to `51` and the `years` parameter to `10`.   

## Data preparation

All data preparation steps are performed in the Jupyter notebooks NB1 - NB10. These notebooks are not included in `code/run`, but can be run within a Jupyter notebook environment. All primary input data necessary to run the notebooks are provided in the `data/` directory, with the outputs that are subsequently used as input to mSHIFT saved in the `/data` directory. All notebooks should be run in the indicated order in the notebook file name, starting with NB1 and ending with NB10.

 The data preparation notebooks are as follows:

1. **NB1_foodDB_data_processing.ipynb**

    Takes the collated data from the Nutrient Databank 2022 to FoodDB matching performed in a separate analysis, and performs some additional processing steps for the impacts and costs per 100g.  

2. **NB2_shes_impact_data.ipynb**  

    Incorporates the foodDB matching data into the SHeS 2021 dietary data.

3. **NB3_dairy_disaggregation_processing.ipynb**  

    Includes the dairy disaggregation data into the SHeS 2021 impact data.

4. **NB4_baseline_per_capita_indicators.ipynb**  

    Calculates the baseline indicators (nutrients + foodDB indicators) at the participant level.

5. **NB5_meat_dairy_ingredient_data_processing.ipynb**  

    Calculates the nutrient content and impacts of each meat and dairy ingredient in SHeS to be used as input data for the reduction simulation.  

6. **NB6_substitute_processing.ipynb**  

    Calculates the nutrient content and impacts per gram of all the meat and dairy substitute foods to be used in the substitution simulations. Also includes the computation of the nutrient content and impacts of the weighted composite meat and dairy replacements.

7. **NB7_high_consumer_reduction_thresholds.ipynb**

    Calculates the maximum intake levels of red and red processed meat per day that is equivalent to an overall percentage reduction in all meat.

8. **NB8_mSHIFT_health_data_prep.ipynb**  

    Combines the participant level data and dietary data and extracts all the variables that are used as covariates in the disease risk models implemented within the mSHIFT health modules.  

9. **NB9_dairy_RR.ipynb**  

    Derives the relative risk association between dairy intake and type-2 diabetes risk that is subsequently sampled in the health simulation.

10. **NB10_Predicting_Missing_Variables.ipynb**

    Takes the output from the Bayesian Machine Scientist algorithm on predicting systolic blood pressure, total cholesterol and HDL cholesterol from the US based National Health and Nutrition Examination Survey and evaluates the imputation model performance. Also includes the script to run the MCMC algorithms that estimate parameter uncertainty for each imputation model.


## mSHIFT

### Health and nutrient intake impacts

The simulations of the health and nutrient impacts of each dietary scenario are performed in the primary mSHIFT directory. Simulation parameters for the meat and dairy reduction simulations are set in the bash script `run_sim.sh`. The two primary reduction pathways are specified by setting values in the following lists:

```
reductions=(20 35)
max_intake_list=(70 60 31)
```

The values in `reductions` indicate the blanket percentage meat reduction scenarios across all meat food groups that are considered in the simulation, while the values in `max_intake` list specify the maximum daily intake of red and red processed meat for a given scenario. To ensure reproducibility, each iteration of mSHIFT in a given scenario is associated with a random seed parameter that ensures that all random sampling performed in a single run is deterministic for a given value of the random seed parameter. The number of iterations is set with the following variables

```
start_seed=1
end_seed=51
```
 The value of `end_seed`  sets the total number of iterations to perform for a given scenario, with the submitted results corresponding to an `end_seed` parameter of 51. To save computational resources on Code Ocean, the `max_seed` parameter has been set to 3. The `red_meat` and `processed_meat` parameters determine whether the reductions apply to unprocessed red meat items and processed meat items respectively. In all scenarios both `red_meat` and `processed_meat` are set to `True`. The parameter `dairy_reduction` determines the percentage reduction of all dairy, which is set to `20` for all modelled dietary scenarios. The `years` parameter sets the number of years over which to run the health simulations which is set to 10 in the submitted results, but is set to `2` on the Code Ocean platform to save computational resources. Finally, it is necessary to set the path to the participant level data that includes all necessary variables for the health simulations
 ```
# Path to the unimputed health data
path="../../data/df_SHeS_unimputed.parquet"
 ```
where `df_SHeS_unimputed.parquet` is the output of running the notebook `/notebooks/NB8_mSHIFT_health_data_prep.ipynb`. The baseline health simulation is performed by setting the `percent_reduction` parameter to 0.    

### Notebooks

The remaining notebooks in the `code/notebooks` directory from NB11-NB16 contain the relevant code for evaluating the results of each dietary scenario on the indicators from foodDB, the subsequent impact of gram-for-gram meat and dairy replacements and the scripts for analysing the simulation output. The relevant notebooks are as follows:

1. **NB11_env_indicators_reduction_simulations.ipynb**

    Takes the food item level data and the associated meat and dairy reductions from the nutrient impact simulations and computes the associated impact on the foodDB indicators.

2. **NB12_substitution_simulations.ipynb**

    Takes the participant level data on nutrient intake and the foodDB indicators and computes the impact of replacing the reduced meat and dairy with each substitute. To save the output from the substitution simulations outside of the primary run script in a Jupyter notebook environment, set `results_path = Path(../../data/results_test)`. The parameters for each scenario, including the specification of the meat and dairy replacements and the level of meat and dairy reduction are defined in `/data/mappings/scenario_dict.json`.

3. **NB13_results_plots.ipynb**

    Reproduces the plots that demonstrate the net impact on each indicator in each scenario in different demographic groups. The data used to produce the plots is an output of running `NB21_substitution_simulations.ipynb`. To produce plots of the simulation results outside of the primary run script, it is necessary to set the `results_path = Path(../../data/results_test)`.

4. **NB14_results_tables.ipynb**

    Reproduces the tables with both the absolute new level of intake and environmental impact as well as the change from the baseline in both the overall population and in different demographic groups. To reproduce the results from the preprint, it is necessary to set `num_seeds=51` and `years=10` in `code/notebooks/notebook_code/results_tables.py` script. For this to run successfully, the parameter `end_seed` should also be set to `51` in `/code/mSHIFT/run_rim.sh`. To reproduce the results tables outside of the primary run script, set `results_path = Path(../../data/results_test)`, with the tables saved in the `/data/results_test/Tables` directory.     

5. **NB15_food_group_contributions.ipynb**

    Computes the relative contribution of each food group in SHeS 2021 to both nutrient intake and total environmental impact.

6. **NB16_energy_adjusted_impacts.ipynb**

    Calculates the population level environmental impacts of each foodDB indicator after adjusting for daily average energy intake.  

The notebooks NB11-NB14 are included in the main run script, while NB15 and NB16 can be run in a Jupyter notebook environment. If a user wishes to analyse the simuation results and produce the supplementary tables outside of the primary run script it is necessary to change the path to the results directory from `'../../results'` to `../../data/results_test` where example outputs from mSHIFT are saved.   

## data

Open source data used as input to both the primary mSHIFT script and in the data preparation pipeline are provided in subdirectories within the `/data` directory. All datasets that are produced in the data preparation stage of the analysis are saved directly in the `/data` directory. The dataset containing estimated environmental impacts and cost for each item in the NDB is available via Edinburgh DataShare: (DOI: https://doi.org/10.7488/ds/8131). The 2021 Scottish health survey data are available via the UK Data Service: doi: 10.5255/UKDA‐SN‐9048‐2. Due t storage limits the food item level dataset SHeS_2021_food_level_condensed.csv and the individual level data shes21i_eul.csv are not provided in the github repo but should be placed in the shes_data_raw directory for the purposes of reproducing the analysis in the notebooks that require them.

Due to github storage limits the full health results across the 50 simulation iterations are not provided in the repo. We have provided the results for all scenarios for three simulation iterations which can be found under the results/Output/ directory. The data used to produce all plots of change in per capita indicators are available under results/Scenarios/Scenario[X]/ where X is the numerical label for the scenario provided in Table 1 of the manuscript
