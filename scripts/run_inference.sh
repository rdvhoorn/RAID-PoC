#!/bin/bash
#SBATCH --job-name=raid_infer
#SBATCH --output=%x-%j.out       # %x = job name, %j = job ID (will move this later)
#SBATCH --time=00:01:00
#SBATCH --mem=512M

WSI_ID=$1
OUTPUT_DIR=$2

echo "Starting fake AI inference on WSI: $WSI_ID"
sleep 5

mkdir -p "$OUTPUT_DIR"

# Move stdout to the output folder manually
mv "$SLURM_JOB_NAME-$SLURM_JOB_ID.out" "$OUTPUT_DIR/slurm_$WSI_ID.out"

# Write result JSON to output directory
echo "{\"wsi_id\": \"$WSI_ID\", \"status\": \"COMPLETED\"}" > "$OUTPUT_DIR/$WSI_ID.json"


# This is a script that SLURM will execute to simulate a model run.
# Accepts a WSI ID as argument
# Sleeps for 5 seconds
# Writes a fake JSON result to /tmp/raid_result_<wsi_id>.json
