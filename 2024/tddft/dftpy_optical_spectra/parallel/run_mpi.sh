#!/bin/bash

#SBATCH --job-name=OS_mpi
#SBATCH --nodes=1
#SBATCH --ntasks=36
#SBATCH -p RM
#SBATCH -t 3-00:00:00
#SBATCH --output=slrum.%N.%j.out
#SBATCH --error=slrum.%N.%j.err
#SBATCH --mem=80GB                                                       

module load intel python
module load openmpi
source /ocean/projects/che240027p/shared/software/Team_RU/env.bash

srun -n 36 python optical_spectra.py > "optical_spectra".out
