#!/bin/sh
#SBATCH -t 13-23:59
#SBATCH -p dgx2q
#SBATCH --gres=gpu:1

export OMP_NUM_THREADS=4      # GCC, C-LANG, GMP etc.
export MKL_NUM_THREADS=4      # Intel MKL and VML
export NUMEXPR_NUM_THREADS=4  # Intel MKL and VML


srun python test_01.py train --num_epochs 2
srun python test_01.py check_val