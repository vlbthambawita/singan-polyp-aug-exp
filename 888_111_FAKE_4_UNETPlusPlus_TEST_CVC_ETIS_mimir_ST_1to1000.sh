#!/bin/sh

exp_name="FAKE_4_UNETPlusPlus_128_ST_1to1000" 

record_name="CVC"

num_epochs=300

gpuID=0

model="UnetPlusPlus"


test_csvs_fold_0="/work/vajira/DL/singan-polyp-aug-exp/notebooks/CVC_Clinic_DB.csv"
test_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/CVC_Clinic_DB.csv"
test_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/CVC_Clinic_DB.csv"


exp_name_fold_0="{$exp_name}_fold_0" 
exp_name_fold_1="{$exp_name}_fold_1" 
exp_name_fold_2="{$exp_name}_fold_2" 



python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_0 --test_CSVs $test_csvs_fold_0 --model $model --device_id $gpuID --record_name $record_name
python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_1 --test_CSVs $test_csvs_fold_1 --model $model --device_id $gpuID --record_name $record_name
python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_2 --test_CSVs $test_csvs_fold_2 --model $model --device_id $gpuID --record_name $record_name


#######################

record_name="ETIS"

test_csvs_fold_0="/work/vajira/DL/singan-polyp-aug-exp/notebooks/ETIS_Larib_DB.csv"
test_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/ETIS_Larib_DB.csv"
test_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/ETIS_Larib_DB.csv"


python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_0 --test_CSVs $test_csvs_fold_0 --model $model --device_id $gpuID --record_name $record_name
python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_1 --test_CSVs $test_csvs_fold_1 --model $model --device_id $gpuID --record_name $record_name
python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_2 --test_CSVs $test_csvs_fold_2 --model $model --device_id $gpuID --record_name $record_name
