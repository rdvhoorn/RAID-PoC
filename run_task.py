from tasks.slurm_tasks import run_slurm_inference

result = run_slurm_inference.delay("abc123")
print("SLURM job submitted...")

print("Waiting for result:")
print(result.get(timeout=60))