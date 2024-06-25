#!/bin/bash

#SBATCH --job-name=QEpy_mpi
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH -p RM
#SBATCH -t 3-00:00:00
#SBATCH --output=slrum.%N.%j.out
#SBATCH --error=slrum.%N.%j.err
#SBATCH --mem=80GB                                                       

module load intel python
module load intelmpi
source /ocean/projects/che240027p/shared/software/Team_RU/env.bash

mpirun -n 36 python tddft_c6h6_mpi.py > "tddft_c6h6_mpi".out
