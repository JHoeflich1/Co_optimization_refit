#!/bin/bash
#SBATCH -J vdw-valence-fit
#SBATCH --nodes=1            # One node
#SBATCH --ntasks=1           # One task (serial job)
#SBATCH --cpus-per-task=1    # One core (FB is serial)
#SBATCH --gres=gpu:1         # One GPU (used by Evaluator/OpenMM)
#SBATCH --mem=10000mb        # Memory for the node
#SBATCH --partition=blanca-shirts
#SBATCH --qos=blanca-shirts
#SBATCH --account=blanca-shirts
#SBATCH -t 07:00:00
#SBATCH --export=ALL
#SBATCH -o logs/master-%A.out
#SBATCH -e logs/master-%A.err


# Execute a force field optimization job using SLRUM for job scheduling and FB for computational tasks. Manages workflow by setting up a temp directory, activating a conda environemnt, and handling data transfers. 
ml anaconda
conda_env="co-optimization-cuda" #"evaluator-co-test" "sep-2024-env" and evaluator-test-matt
source $HOME/.bashrc
conda activate $conda_env

# Creates a temporary directory to isolate job files and prevent conflicts with other jobs
TMPDIR=/scratch/alpine/juho8819/tmp/$SLURM_JOB_ID
export SLURM_SUBMIT_DIR=$(pwd)

#create logs folder if missing
mkdir -p logs

rm -rf $TMPDIR
mkdir -p $TMPDIR || { echo "Failed to create TMPDIR"; exit 1; }
cd $TMPDIR


# Copies files from the submission directory to the temp directory
rsync -av  $SLURM_SUBMIT_DIR/{optimize.in,targets.tar.gz,forcefield}     $TMPDIR
tar -xzf targets.tar.gz


echo $CONDA_PREFIX > $SLURM_SUBMIT_DIR/env.path
echo $(hostname) > $SLURM_SUBMIT_DIR/host

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1


# create results dir and placeholder
mkdir -p result/optimize
touch result/optimize/force-field.offxml

#launch evaluator and FB
python $SLURM_SUBMIT_DIR/run_evaluator.py > $SLURM_SUBMIT_DIR/logs/evaluator.log 2>&1
