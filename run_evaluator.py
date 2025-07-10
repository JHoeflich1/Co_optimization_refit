import os
import subprocess
import shutil
import logging
from forcebalance.evaluator_io import Evaluator_SMIRNOFF
from openff.units import unit
from openff.evaluator.client import RequestOptions
from openff.evaluator.properties import Density, EnthalpyOfVaporization
from openff.evaluator.backends import ComputeResources
from openff.evaluator.backends.dask import DaskLocalCluster
from openff.evaluator.server import EvaluatorServer

# Setup logging
log_filename = "evaluator_detailed.log"
logging.basicConfig(
    filename=log_filename,
    filemode='w',  # overwrite on each run
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s: %(message)s",
)

logger = logging.getLogger()
logger.info("Evaluator script started")

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

logger.info("Starting DaskLocalCluster backend...")
calculation_backend = DaskLocalCluster(
    number_of_workers=1,
    resources_per_worker=ComputeResources(
        number_of_threads=1,
        number_of_gpus=1,
        preferred_gpu_toolkit=ComputeResources.GPUToolkit.CUDA,
    ),
)
calculation_backend.start()
logger.info("Calculation backend started.")

logger.info("Starting EvaluatorServer...")
evaluator_server = EvaluatorServer(calculation_backend=calculation_backend)
evaluator_server.start(asynchronous=True)
logger.info("EvaluatorServer started asynchronously.")

logger.info("Running ForceBalance.py optimize.in ...")
exit_code = os.system("ForceBalance.py optimize.in")
if exit_code == 0:
    logger.info("ForceBalance.py completed successfully.")

    # Tar optimize.tmp directory if it exists
    optimize_dir = "optimize.tmp"
    tarball_name = "optimize.tmp.tar.gz"
    if os.path.isdir(optimize_dir):
        print(f"Creating tarball {tarball_name} from {optimize_dir} ...")
        subprocess.run(["tar", "-czf", tarball_name, optimize_dir])
    else:
        print(f"Warning: {optimize_dir} directory does not exist, skipping tarball creation.")

    # Rsync from TMPDIR to SLURM_SUBMIT_DIR with exclusions
    tmpdir = os.environ.get("TMPDIR")
    submit_dir = os.environ.get("SLURM_SUBMIT_DIR")
    if tmpdir and submit_dir:
        print(f"Syncing files from {tmpdir} to {submit_dir} ...")
        rsync_cmd = [
            "rsync", "-azIi", "-rv",
            "--exclude=optimize.tmp",
            "--exclude=optimize.bak",
            "--exclude=fb*",
            "--exclude=targets*",
            f"{tmpdir}/", f"{submit_dir}/"
        ]
        subprocess.run(rsync_cmd)
    else:
        print("Warning: TMPDIR or SLURM_SUBMIT_DIR environment variables not set; skipping rsync.")

    # Remove TMPDIR directory
    if tmpdir and os.path.isdir(tmpdir):
        print(f"Removing temporary directory {tmpdir} ...")
        shutil.rmtree(tmpdir)
    else:
        print("Warning: TMPDIR directory does not exist or not set; skipping removal.")
else:
    logger.error(f"ForceBalance.py exited with errors. Exit code: {exit_code}")

logger.info("Evaluator script finished.")

