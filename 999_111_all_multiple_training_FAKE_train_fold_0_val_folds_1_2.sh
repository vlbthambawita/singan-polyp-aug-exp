#!/bin/sh

exp_name="FAKE_UNETPlusPlus_128_ST_1to1000_multi" 

num_epochs=100

gpuID=1

model="UnetPlusPlus"

train_csvs="/work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_10_ST_1to1000_selected_50_fold_0.csv"
train_amounts="50 100 150 200 250 300 350 400 450 500" 

val_csvs="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"
test_csvs="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"

#train_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_4_ST_1to1000_fold_0.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_4_ST_1to1000_fold_2.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_0.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"
#val_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv"
#test_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv"

#train_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_4_ST_1to1000_fold_0.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_4_ST_1to1000_fold_1.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_0.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv"
#val_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"
#test_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"


exp_name="{$exp_name}" 
#exp_name_fold_1="{$exp_name}_fold_1" 
#exp_name_fold_2="{$exp_name}_fold_2" 



python 999_all_multiple_training.py train_multi --exp_name $exp_name --num_epochs $num_epochs --train_CSVs $train_csvs --val_CSVs $val_csvs --model $model --test_CSVs $test_csvs --device_id $gpuID --train_amounts $train_amounts
python 999_all_multiple_training.py check_val_multi --exp_name $exp_name --test_CSVs $test_csvs --model $model --device_id $gpuID --train_amounts $train_amounts

#python 777_all_in_one_v1.py train --exp_name $exp_name_fold_1 --num_epochs $num_epochs --train_CSVs $train_csvs_fold_1 --val_CSVs $val_csvs_fold_1 --model $model --test_CSVs $test_csvs_fold_1 --device_id $gpuID
#python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_1 --test_CSVs $test_csvs_fold_1 --model $model --device_id $gpuID

#python 777_all_in_one_v1.py train --exp_name $exp_name_fold_2 --num_epochs $num_epochs --train_CSVs $train_csvs_fold_2 --val_CSVs $val_csvs_fold_2 --model $model --test_CSVs $test_csvs_fold_2 --device_id $gpuID
#python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_2 --test_CSVs $test_csvs_fold_2 --model $model --device_id $gpuID