#!/bin/bash
#SBATCH --time=3-00:00:00
#SBATCH --partition=price-pi
#SBATCH --job-name=gluc
#SBATCH --nodelist=haln084
#SBATCH --ntasks=64                # Total # of tasks across all nodes
#SBATCH --mem=220G                   # Real memory (RAM) required          
#SBATCH --output=slurm.%N.%j.out     # STDOUT output file
#SBATCH --error=slurm.%N.%j.err      # STDERR output file (optional)
#SBATCH --export=ALL                 # Export you current env to the job env
#SBATCH --cluster=amareln

module load python/3.8.5-gc563 intel/19.1.1 gsl/2.5-bd387 libffi/3.3-gc563
source /projectsn/mp1009_1/motas/3_QMMM/software/edftpy_qmmm/bin/activate
export LD_PRELOAD=/opt/sw/packages/intel/19.1.3/mkl/lib/intel64/libmkl_rt.so
export LD_LIBRARY_PATH="/opt/sw/packages/intel/19.1.3/mkl/lib/intel64/:$LD_LIBRARY_PATH"
export LDFLAGS="-L//opt/sw/packages/intel/19.1.3/mkl/lib/intel64"
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/projectsn/mp1009_1/motas/3_QMMM/software/q-e/external/devxlib/src
export qedir='/projectsn/mp1009_1/motas/3_QMMM/software/q-e'
export MBX_HOME=/projectsn/mp1009_1/motas/3_QMMM/software/mbx-python-old/
export PYTHONPATH=$PYTHONPATH:${MBX_HOME}/plugins/python/mbx
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/projectsn/mp1009_1/motas/3_QMMM/software/dftd3/lib64/

#source /projectsn/mp1009_1/venv/intel19dev/bin/env.sh
#export MBX_HOME=/projectsn/mp1009_1/motas/3_QMMM/software/mbx-python-old/
#export PYTHONPATH=$PYTHONPATH:${MBX_HOME}/plugins/python/mbx

NODES=$SLURM_JOB_NUM_NODES
NTASKS=$SLURM_NTASKS
ulimit -n 4096

export OMP_NUM_THREADS=1
export USE_SIMPLE_THREADED_LEVEL3=1

srun -N $NODES -n $NTASKS --mpi=pmi2 python3 relax.py &> log
#srun -N $NODES -n $NTASKS --mpi=pmi2 python3 -m edftpy qeho.ini &> log
