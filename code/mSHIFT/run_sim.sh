#!/usr/bin/env bash

# list of percent level meat reductions
reductions=(20 35)
# list of maximum intake thresholds
max_intake_list=(70 60 31)
# percent level dairy reduction
dairy_reduction=20

start_seed=0
# set to 51 to reproduce submitted reults
end_seed=51

# Specifiy reductions in red meat and/or processed meat
red_meat=True
processed_meat=True

# Set test mode -- if True runs the simulation for 50 test individuals
test_mode=False

# Number of years to run the simulation for
years=10

# Path to the unimputed health data
path="data/df_SHeS_unimputed.parquet"

echo 'mSHIFT -- micro-Simulation of the Health Impacts of Food Transformations'



##################### Scenarios reduction red and processed meat intake among high consumers alone ########################################


######## Accounting for weight loss #########

#shellcheck disable=SC2068
for max_intake in ${max_intake_list[@]}; do
 for seed in $(seq $start_seed $end_seed); do
  python code/mSHIFT/main.py --path_to_df $path  --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change True --years $years --max_intake $max_intake --dairy_reduction $dairy_reduction --test_mode $test_mode
 done
done


######### Assuming isocaloric substitution #########

#shellcheck disable=SC2068
for max_intake in ${max_intake_list[@]}; do
 for seed in $(seq $start_seed $end_seed); do
  python code/mSHIFT/main.py --path_to_df $path  --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change False --years $years --max_intake $max_intake --dairy_reduction $dairy_reduction --test_mode $test_mode
 done
done



################### Baseline health simulation with no dietary change ########################

#shellcheck disable=SC2068
for seed in $(seq $start_seed $end_seed); do
    python code/mSHIFT/main.py --path_to_df $path --percent_reduction 0 --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change True --years $years --dairy_reduction 0 --test_mode $test_mode
done


############## CCC 2030 and CCC 2050 scenarios #######################

######## Accounting for weight loss #########

#shellcheck disable=SC2068
for reduction in ${reductions[@]}; do
  for seed in $(seq $start_seed $end_seed); do
    python code/mSHIFT/main.py --path_to_df $path --percent_reduction "$reduction" --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change True --years $years --dairy_reduction $dairy_reduction --test_mode $test_mode
  done
done

######### Assuming isocaloric substitution #########

#shellcheck disable=SC2068
for reduction in ${reductions[@]}; do
  for seed in $(seq $start_seed $end_seed); do
    python code/mSHIFT/main.py --path_to_df $path --percent_reduction "$reduction" --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change False --years $years --dairy_reduction $dairy_reduction --test_mode $test_mode
  done
done

################### 20% reduction in dairy alone ########################


######## Accounting for weight loss #########

#shellcheck disable=SC2068
for seed in $(seq $start_seed $end_seed); do
    python code/mSHIFT/main.py --path_to_df $path --percent_reduction 0 --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change True --years $years --dairy_reduction 20 --test_mode $test_mode
done

######### Assuming isocaloric substitution #########

#shellcheck disable=SC2068
for seed in $(seq $start_seed $end_seed); do
    python code/mSHIFT/main.py --path_to_df $path --percent_reduction 0 --seed "$seed" --red_meat $red_meat --processed_meat $processed_meat --bmi_change False --years $years --dairy_reduction 20 --test_mode $test_mode
done


