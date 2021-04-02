#!/bin/sh
#SBATCH -t 13-23:59
#SBATCH -p dgx2q
#SBATCH --gres=gpu:1

export OMP_NUM_THREADS=4      # GCC, C-LANG, GMP etc.
export MKL_NUM_THREADS=4      # Intel MKL and VML
export NUMEXPR_NUM_THREADS=4  # Intel MKL and VML


srun python 112_FAKE_FPN_fold_0.py train --num_epochs 200
srun python 112_FAKE_FPN_fold_0.py check_val

srun python 112_FAKE_FPN_fold_1.py train --num_epochs 200
srun python 112_FAKE_FPN_fold_1.py check_val

srun python 112_FAKE_FPN_fold_2.py train --num_epochs 200
srun python 112_FAKE_FPN_fold_2.py check_val