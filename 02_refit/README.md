## Second attempt to co-optimize a force field with OpenFF Evaluator and Force Balance: 02_refit

Modifications were made to openff/evaluator/workflow/workflow.py code to solve issue in `../01_refit`, this is now refelcted in the env `co-optimization-cuda` that is used in this repo. So notice, OpenFF Evaluator is installed from my forked repository rather than the official release.

Error documented in `./logs/evaluator.logs`

### To replicate error:

You will need files/folders:
- forcefield/force_field_tagged.offxml
- targets.tar.gz
- optimize.in
- run_evaluator.py
- hpc3_master.sh
  
Create environment: co-optimization-cuda\
`mamba env create -f env-co-optimization.yaml`\
\
In 02_refit:
You will need to modify slurm commands in `hpc3_master.sh`. currently contains SLURM directives for CU Boulder’s HPC cluster.
Update these directives to match your own HPC systems resource specs.\
\
Run `sbatch hpc3_master.sh`\
This is sufficient to reproduce the error — the worker job script `submit_hpc3_worker_local.sh` does not need to be run.
