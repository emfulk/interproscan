# Parallelizing Interproscan with slurm

These scripts enable batch submission of multiple independent Interproscan analyses that are run in parallel using minimized amounts of computing resources and user oversight.

A wrapper script (ips_stage.py) pulls a user-specified number of input files (in amino acid FASTA format) and writes an individual job submission for each input file (ips_slurm_template_render.py) based on a template (ips_template.sbatch). For jobs that are successfully completed (i.e. where Interproscan generates a output file with results), the input FASTA file and Interproscan output are moved to a new directory. Input files with jobs that do not successfully complete with the allotted computational resources are retained in a failures folder to be re-run with more resources.

![2302_readme](https://user-images.githubusercontent.com/63920521/219883990-601c660e-2034-4535-9964-c2db0cb1863a.png)

This strategy enables analysis of large datasets of genomes with less manual oversight by the user. The instructions here are customized for the Rice NOTS cluster, which uses the SLURM job scheduler.

## Installation

1. Download repo into /projects

    `git clone https://github.com/rice-crc/`

2. Following the [Interproscan installation instructions](https://interproscan-docs.readthedocs.io/en/latest/UserDocs.html?highlight=initial_setup.py):
    1. First launch an interactive job

        `srun --pty --ntasks=1 --mem-per-cpu=1000m --time=00:30:00 /bin/bash --partition=interactive`
    
    2. Then load requisite modules and run the initial setup script

        `module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 
        python3 initial_setup.py`  

3. Some settings specific to the Rice NOTS system:

    1. The XALT_EXECUTABLE_TRACKING variable in the slurm script is to disable the xalt tracking feature - it is not necessary and causes the Perl scripts to crash and fail
    2. [Cluster mode](https://interproscan-docs.readthedocs.io/en/latest/ImprovingPerformance.html?highlight=cluster%20mode#running-interproscan-in-cluster-mode) appears not to work
    3. Requisite modules:
        1. Java>11
        2. CGGcore/8.3.0
        3. Python/3.7.2
        4. Perl/5.30.0

## Executing in slurm

1. Define paths for Interproscan and storage and temporary directories hardcoded in ips_slurm_settings.py.
2. Define computational resources in ips_slurm_template_render.py. Example slurm settings:

    #SBATCH --partition=scavenge
    #SBATCH --ntasks=1
    #SBATCH --nodes=1
    #SBATCH --cpus-per-task=4
    #SBATCH --threads-per-core=1
    #SBATCH --mem-per-cpu=2GB
    #SBATCH --time=01:00:00
    #SBATCH --export=ALL

    module load Java/12.0.2 GCCcore/8.3.0 Python/3.7.2 Perl/5.30.0

    ips_slurm_template_render.py renders the template for individual jobs. Note the following:
    1. Turns off xalt tracking
    2. Limits the work to 1 node, but with multiple CPUs
    3. Includes some stdoutput for logging
    4. Input variable is hard-coded
    5. Paths are dependent on username/netids and require having Interproscan in the /projects directory

3. Generate and submit batches of N files for Interproscan analysis by running `python ips_stage.py N`

## Description of files

| filename | Description |
| --- | --- |
| ips_slurm_settings.py | This is where you define your filepaths for storage and temporary directories and for Interproscan. |
| ips_slurm_template_render.py | This renders the job template for each input file, and where you specify computational resources (partition, CPUs, memory, runtime, etc.).  |
| ips_template.sbatch | This is the template. At the start of the job, it moves the input file from the inbox to the failures folder. When the job finishes, it checks for a corresponding .tsv file and, if the job is successful in generating a .tsv output, moves the input file to the outbox.
| ips_stage.py | This file accepts a single integer argument (e.g. 'ips_stage.py 20') and and pulls the specified number of input files from /work/.../inbox folder to the /scratch/.../inbox/folder. It then renders templates and submits slurm files for each of these jobs. Before moving and submitting new input files, it moves any files in /scratch/.../failures , /scratch/.../outbox, and all .sbatch and slurm*.out files back to the respective /work... folders. |

## Directory structure

Five subdirectories are created to store input files (in amino acid FASTA format), Interproscan outputs (in tsv format), and SLURM files.

1. faa_inbox: contains input files to be analyzed, in amino acid fasta (.faa) format.
2. faa_outbox: contains successfully analyzed input files.
3. faa_failures: contains unsuccessfully analyzed input files.
4. slurm_files: contains slurm*.out and *.slurm files.
5. tsv_outputs: contains .tsv outputs from Interproscan.

## Why these settings were chosen, and ideas for future optimization

The above settings were chosen based on the following parameters of Interproscan runs:
1. In generating matches between the protein sequences and Interproscan signatures, the java process spawns threads (probably talking to the remote database).
2. Interproscan creates lots of small temporary files/databases, which runs fastest if it writes to /tmp instead of /scratch (3 vs. 1-1.5 hours). It appears to multithread well if running on a single node.
3. Input and output files are relatively small and can be read/written to/from /scratch.

We moved away from job array checkpointing to a slurm template write. With additional work, this protentially enables jobs be to dynamically set with memory, CPUs, and job time according to the relationship between input filesize and resources needed. It could also be possible to set up a local instance of the Interpscan database, reducing the overhead related to network latency in querying the remote Interproscan database.
