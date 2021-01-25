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

	#!/bin/sh

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

### III. Templating
(Jan 22)

Moved away from job array checkpointing to a slurm template writer.

This will allow us, down the line, to dynamically set memory, CPU's, wall-time according to the job's needs, once we have a clear idea of the relation between resources and input filesize.

(Jan 24)
Tested and debugged the scripts. 4 components:
* ips_slurm_settings.py -- this is where you define your paths
* ips_slurm_template_render.py -- this renders the template
* ips_template.sbatch -- this is the template
   * note: when the job kicks off it moves all the .faa files from /scratch/.../inbox to /scratch/.../failures
   * and when it finishes, it checks to see if there is a correponding tsv file in /scratch/.../tsv_outputs and moves the .genes.faa input fileto /scratch/.../outbox
   * in other words the default is a failed job. This appears to work but I am very much open to there being a case that breaks it.
* ips_stage.py
   * invoked with a single integer argument, e.g. `ips_stage.py 7`
   * pulls in N '...genes.faa' files from the /work/.../inbox folder to the /scratch/.../inbox/folder
   * then templates and submits the slurm files for each of these jobs
      * we opted against job arrays, because this way you can do something clever, down the line, in terms of making the ips_slurm_template_render.py file feed in different cpu, ram, and time wall settings according to the anticipated need (probably based on file size)
   * but before it does the above 2 steps it:
      * looks for files in /scratch/.../failures and /scratch/.../outbox
      * moves these and all the .sbatch and slurm*.out files back to respective /work... folders
			
### IV. Still need
	
1. Trying different node settings (using the same input file) for:
   1. Resource basic requirements (how few cores & how little RAM can you run this with)
   1. Performance improvement on resources (how much does this speed up your job)
   1. Consider this on scavenge queue in order to get results faster
   1. Consider ssh'ing into nodes to check resource usage in real time
1. How much variability do we see--use a random selection of a few input files to:
   1. See if your basic requirements change -- does it crash? -- very unlikely
   1. See how much your run-time varies -- does it change? -- likely

### V. Extra notes

Why the above settings were chosen:

1. in generating matches:
   1. java process spawns threads, probably talking to the remote database
1. creates tons of small temp files, databases, etc.
   1. which runs fastest if it's writing to /tmp instead of /scratch (3 vs. 1-1.5 hours)
   1. and if it's running on a single node, where it appears to multithread well
1. input and output files, relatively small, can be read/written to/from /scratch

Potential down-the-road optimization:

1. we could maybe set up a local instance of the database that has to go out to England as a query, to reduce the overhead that's reliant on network latency.
1. either way, could we avoid re-running the first database query step every single time to the external database to cut down on the overhead?
