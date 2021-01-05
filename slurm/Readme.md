# Parallelizing interproscan with slurm

The instructions here are customized for the Rice NOTS cluster

## I. Installation

A. Download repo into /projects

    git clone https://github.com/rice-crc/
    
B. Following [interproscan installation instructions](https://interproscan-docs.readthedocs.io/en/latest/UserDocs.html?highlight=initial_setup.py):

First launch an interactive job

    srun --pty --ntasks=1 --mem-per-cpu=1000m --time=00:30:00 /bin/bash --partition=interactive
    
Then load requisite modules and run the initial setup script

    module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 
    python3 initial_setup.py    

(should we include a testing step here before exiting?)

C. Some settings specific to our system:

1. The XALT_EXECUTABLE_TRACKING variable in the slurm script is to disable this feature - it is not necessary and causes the Perl scripts to crash and fail
1. [Cluster mode](https://interproscan-docs.readthedocs.io/en/latest/ImprovingPerformance.html?highlight=cluster%20mode#running-interproscan-in-cluster-mode) appears not to work. More on this below.
1. Requisite modules:
   1. Java > 11
   1. CGGcore/8.3.0
   1. Python/3.7.2
   1. Perl/5.30.0

## II. Executing in slurm

Example slurm script. Note the following:

1. Turns off xalt tracking
1. Limits the work to 1 node, but with multiple CPU's
1. Includes some stdoutput for logging
1. Input variable is hard-coded
1. Paths are dependent on usernames/netids and require having interproscan in the /projects directory (more below)

	```#!/bin/sh

	#SBATCH --account=commons
	#SBATCH --partition=commons
	#SBATCH --ntasks=1
	#SBATCH --nodes=1
	#SBATCH --cpus-per-task=4
	#SBATCH --threads-per-core=1
	#SBATCH --mem-per-cpu=2GB
	#SBATCH --time=01:20:00
	#SBATCH --export=ALL

	module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 

	echo "Starting at : `date`"
	echo "Running on hosts: $SLURM_NODELIST"
	export IPSPATH=/projects/SPONSORNETID/interproscan-5.48-83.0
	export SCR=/scratch/YOURNETID
	# make tmpdir with jobid number
	export TMPD=/tmp/$SLURM_JOB_ID
	export XALT_EXECUTABLE_TRACKING=no
	export INP=2832985738.genes.faa
	$IPSPATH/interproscan.sh --tempdir $TMPD -i $SCR/$INP -f tsv -b $SCR/$SLURM_JOB_ID 

This directory contains 3 example slurm scripts:
* 4 CPU's
 * ips_smp_4cpu.sbatch (4cpu example that runs on commons)
  * plus outputs in subdirectory for examination
 * ips_smp_4cpu.scavenge (4cpu example that runs on scavenge queue)
* 8 CPU's
 * ips_smp_8cpu.sbatch

Which would be submitted, for example, with `sbatch ips_smp_4cpu_scavenge.sbatch`

### III. Next Steps

1. Validate outputs
1. Need better documentation on the file structure
1. Trying different node settings (using the same input file) for:
 1. Resource basic requirements (how few cores & how little RAM can you run this with)
 1. Performance improvement on resources (how much does this speed up your job)
 1. Consider this on scavenge queue in order to get results faster
 1. Consider ssh'ing into nodes to check resource usage in real time
1. How much variability do we see--use a random selection of a few input files to:
 1. See if your basic requirements change -- does it crash? -- very unlikely
 1. See how much your run-time varies -- does it change? -- likely


### IV. Anticipated steps for making this a job array:

Mostly, this is about determining where the input and output files go specifically

1. Probably want to set --tasks-per-core=1 and nodes=ntasks
1. Make INP variable into a parameter rather than a hard-coded filename
1. Change output filename to correspond to that INP variable


### V. Extra notes

Why the above settings were chosen:

1. Why job arrays? because cluster mode does not appear to work with slurm
1. in generating matches:
 1. java process spawns threads, probably talking to the remote database
1. creates tons of small temp files, databases, etc.
 1. which runs fastest if it's writing to /tmp instead of /scratch (3 vs. 1-1.5 hours)
 1. and if it's running on a single node, where it appears to multithread well
1. input and output files, relatively small, can be read/written to/from /scratch

Potential down-the-road optimization:

1. we could maybe set up a local instance of the database that has to go out to England as a query, to reduce the overhead that's reliant on network latency.
1. either way, could we avoid re-running the first database query step every single time to the external database to cut down on the overhead?
