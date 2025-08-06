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

tmpdir =os.environ["TMPDIR"]
print(f"Working in TMPDIR: {tmpdir}")

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

calculation_backend = DaskLocalCluster(
    number_of_workers=1,
    resources_per_worker=ComputeResources(
        number_of_threads=1,
        number_of_gpus=1,
        preferred_gpu_toolkit=ComputeResources.GPUToolkit.CUDA,
    ),
)
calculation_backend.start()

evaluator_server = EvaluatorServer(calculation_backend=calculation_backend, delete_working_files=False)
evaluator_server.start(asynchronous=True)

exit_code = os.system("ForceBalance.py optimize.in")
if exit_code == 0:
    print("-- Force field done --")
else:
    print("ForceBalance.py exited with errors.")
