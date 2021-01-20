#!/bin/sh
#SBATCH --partition=scavenge
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --threads-per-core=1
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:30:00
#SBATCH --export=ALL

module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 

echo "Starting at : `date`"
echo "Running on hosts: $SLURM_NODELIST"
export IPSPATH=............/interproscan-5.48-83.0
export SCR=............/ips/fasta_files
# make tmpdir with jobid number
export TMPD=/tmp/$SLURM_JOB_ID.$SLURM_ARRAY_TASK_ID
echo "Temp dir: $SLURM_NODELIST : $TMPD"
export XALT_EXECUTABLE_TRACKING=no
export INP=$(sed $SLURM_ARRAY_TASK_ID'!d' unfinished.txt)
FAA_ID=$(echo $INP | awk -F. '{print $1}')

echo $INP
echo $FAA_ID

$IPSPATH'/interproscan.sh' --tempdir $TMPD -i $SCR'/in/'$INP -f tsv -b $SCR'/tsv_outputs/'$SLURM_JOB_ID'.'$SLURM_ARRAY_TASK_ID'.FAA.'$FAA_ID



