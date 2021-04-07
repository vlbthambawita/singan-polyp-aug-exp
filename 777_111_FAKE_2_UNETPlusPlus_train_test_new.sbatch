#!/bin/sh
#SBATCH -t 13-23:59
#SBATCH -p dgx2q
#SBATCH --gres=gpu:1

export OMP_NUM_THREADS=4      # GCC, C-LANG, GMP etc.
export MKL_NUM_THREADS=4      # Intel MKL and VML
export NUMEXPR_NUM_THREADS=4  # Intel MKL and VML

exp_name="FAKE_2_UNETPlusPlus_128" 

num_epochs=300

model="UnetPlusPlus"

train_csvs_fold_0="/work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_2_fold_1.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_2_fold_2.csv"
val_csvs_fold_0="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_0.csv"
test_csvs_fold_0="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_0.csv"

train_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_2_fold_0.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_2_fold_2.csv"
val_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv"
test_csvs_fold_1="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_1.csv"

train_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_2_fold_0.csv /work/vajira/DL/singan-polyp-aug-exp/notebooks/FAKE_scale_0_num_img_2_fold_1.csv"
val_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"
test_csvs_fold_2="/work/vajira/DL/singan-polyp-aug-exp/notebooks/REAL_fold_2.csv"


exp_name_fold_0="{$exp_name}_fold_0" 
exp_name_fold_1="{$exp_name}_fold_1" 
exp_name_fold_2="{$exp_name}_fold_2" 



srun python 777_all_in_one_v1.py train --exp_name $exp_name_fold_0 --num_epochs $num_epochs --train_CSVs $train_csvs_fold_0 --val_CSVs $val_csvs_fold_0 --model $model --test_CSVs $test_csvs_fold_0
srun python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_0 --test_CSVs $test_csvs_fold_0 --model $model

srun python 777_all_in_one_v1.py train --exp_name $exp_name_fold_1 --num_epochs $num_epochs --train_CSVs $train_csvs_fold_1 --val_CSVs $val_csvs_fold_1 --model $model --test_CSVs $test_csvs_fold_1
srun python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_1 --test_CSVs $test_csvs_fold_1 --model $model

srun python 777_all_in_one_v1.py train --exp_name $exp_name_fold_2 --num_epochs $num_epochs --train_CSVs $train_csvs_fold_2 --val_CSVs $val_csvs_fold_2 --model $model --test_CSVs $test_csvs_fold_2
srun python 777_all_in_one_v1.py check_val --exp_name $exp_name_fold_2 --test_CSVs $test_csvs_fold_2 --model $model