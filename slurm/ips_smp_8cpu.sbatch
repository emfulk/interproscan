#!/bin/sh

#SBATCH --account=commons
#SBATCH --partition=commons
#SBATCH --ntasks=1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --threads-per-core=1
#SBATCH --mem-per-cpu=2GB
#SBATCH --time=01:20:00
#SBATCH --export=ALL

module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 

echo "Starting at : `date`"
echo "Running on hosts: $SLURM_NODELIST"
export IPSPATH=/projects/joff/interproscan-5.48-83.0
export SCR=/scratch/YOURNETID
# make tmpdir with jobid number
export TMPD=/tmp/$SLURM_JOB_ID
export XALT_EXECUTABLE_TRACKING=no
export INP=2832985738.genes.faa
$IPSPATH/interproscan.sh --tempdir $TMPD -i $SCR/$INP -f tsv -b $SCR/$SLURM_JOB_ID 



