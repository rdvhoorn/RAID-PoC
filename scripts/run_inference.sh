#!/bin/bash
#SBATCH --job-name=raid_infer
#SBATCH --output=%x-%j.out       # %x = job name, %j = job ID (will move this later)
#SBATCH --time=00:01:00
#SBATCH --mem=512M

OUTPUT_DIR=$1
JOB_ID=$2

echo "Starting fake AI for job $JOB_ID"
sleep 10

mkdir -p "$OUTPUT_DIR"

# Move stdout to the output folder manually
mv "$SLURM_JOB_NAME-$SLURM_JOB_ID.out" "$OUTPUT_DIR/slurm_$JOB_ID.out"

# Write result JSON to output directory
echo "{\"job_id\": \"$JOB_ID\", \"status\": \"COMPLETED\"}" > "$OUTPUT_DIR/$JOB_ID.json"

# Notify server of completion
python3 scripts/notify_finalize_job.py "$JOB_ID"