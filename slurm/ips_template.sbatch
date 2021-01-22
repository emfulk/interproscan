#!/bin/sh
#SBATCH --partition={{partition}}
#SBATCH --ntasks={{ntasks}}
#SBATCH --nodes={{nodes}}
#SBATCH --cpus-per-task={{cpus-per-task}}
#SBATCH --threads-per-core={{threads-per-core}}
#SBATCH --mem-per-cpu={{mem-per-cpu}}
#SBATCH --time={{running-time}}
#SBATCH --export={{export}}

module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 

echo "Starting at : `date`"
echo "Running on hosts: $SLURM_NODELIST"
export IPSPATH={{IPSPATH}}
# make tmpdir with jobid number
export TMPD=/tmp/$SLURM_JOB_ID
echo "Temp dir: $SLURM_NODELIST : $TMPD"
export XALT_EXECUTABLE_TRACKING=no
export INP={{faa_input_filepath}}

echo $INP

$IPSPATH'/interproscan.sh' --tempdir $TMPD -i $INP -f tsv -b '{{tsv_output_filepath}}.SLURM_JOB_ID'$SLURM_JOB_ID

echo "Finished at : `date`"

if [ -f "$tsv_output"]; then
	mv {{faa_input_filepath}} {{faa_outbox}}
else
	mv {{faa_input_filepath}} {{faa_failures}}
fi

