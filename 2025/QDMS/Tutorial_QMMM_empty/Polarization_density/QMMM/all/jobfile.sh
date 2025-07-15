#!/bin/bash
#SBATCH --job-name="edftpy"
#SBATCH --output="edftpy.%j.%N.out"
#SBATCH --error="edftpy.%j.%N.err"
#SBATCH --partition=shared
#SBATCH --reservation=QDMS-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=3
#SBATCH --mem=50GB
#SBATCH --account=csd973
#SBATCH --export=ALL
#SBATCH -t 03:00:00

env=edftpy_qmmm
software=software
mbx_type=mbx-python-old

module purge
module load slurm
module load cpu/0.17.3b  gcc/10.2.0/npcyll4
module load python/3.8.12/7zdjza7
module load intel-mkl/2020.4.304/ghfk3mu    intel-mpi/2019.10.317/kdx4qap
module load gsl/2.7

export I_MPI_PMI_LIBRARY=/cm/shared/apps/slurm/23.02.7/lib64/libpmi.so

export TMPDIR=/expanse/lustre/projects/csd973/jmartinez2/scratch/jmartinez2/tmp_$SLURM_JOB_ID
mkdir -p $TMPDIR

export FFTW_HOME=/expanse/lustre/projects/csd973/jmartinez2/software/fftw
export FFTW_DIR=$FFTW_HOME
export FFTW_LIB_DIR=$FFTW_DIR/lib
export FFTW_INCLUDE_DIR=$FFTW_DIR/include
export LD_LIBRARY_PATH=$FFTW_HOME/lib:$LD_LIBRARY_PATH

source /expanse/lustre/projects/csd973/jmartinez2/software/$env/bin/activate
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/expanse/lustre/projects/csd973/jmartinez2/$software/q-e/external/devxlib/src
export qedir="/expanse/lustre/projects/csd973/jmartinez2/$software/q-e"
export MBX_HOME=/expanse/lustre/projects/csd973/jmartinez2/$software/$mbx_type/
export PYTHONPATH=$PYTHONPATH:${MBX_HOME}/plugins/python/mbx

NODES=$SLURM_JOB_NUM_NODES
NTASKS=$SLURM_NTASKS

export OMP_NUM_THREADS=1
export USE_SIMPLE_THREADED_LEVEL3=1

echo "$NODES"
echo "$NTASKS"

echo "Python version: $(python --version)"

export LIBXC_DIR=/expanse/lustre/projects/csd973/jmartinez2/software/libxc
export LD_LIBRARY_PATH=$LIBXC_DIR/lib:$LD_LIBRARY_PATH
export CPATH=$LIBXC_DIR/include:$CPATH

srun -n $NTASKS python -m mpi4py.bench helloworld
srun -N $NODES -n $NTASKS python -m edftpy --run mbx.ini --mpi4py  |tee output.out
cp  sub_ks.out   sub_ks1.rec
cp  sub_mm.out   sub_mm2.rec
cp  sub_ks.xsf   sub_qm_1.xsf
cp  sub_mm.xsf   sub_mm_2.xsf

