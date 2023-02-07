# Parallelizing Interproscan with slurm

These scripts enable batch submission of multiple independent Interproscan analyses that are run in parallel using minimized amounts of computing resources. A user-specified number of input files (genomes) are submitted to a job scheduler as individual jobs. Successfully analyzed files are automatically moved to an outbox, while unsuccessfully analyzed files are moved to a separate folder to be re-run with more resources. This strategy enables unsupervised analysis of large datasets of genomes with less manual oversight by the user. The instructions here are customized for the Rice NOTS cluster, which uses the SLURM job scheduler.

![2302_readme](https://user-images.githubusercontent.com/63920521/217164524-d1b2515a-0855-414c-a050-9a60cd63b5cd.png)

## Installation

A. Download repo into /projects

    git clone https://github.com/rice-crc/


B. Following [interproscan installation instructions](https://interproscan-docs.readthedocs.io/en/latest/UserDocs.html?highlight=initial_setup.py):

First launch an interactive job

    srun --pty --ntasks=1 --mem-per-cpu=1000m --time=00:30:00 /bin/bash --partition=interactive
    
Then load requisite modules and run the initial setup script

    module load Java/12.0.2 GCCcore/8.3.0  Python/3.7.2  Perl/5.30.0 
    python3 initial_setup.py    

(Should we include a testing step here before exiting?)

C. Some settings specific to our system:

1. The XALT_EXECUTABLE_TRACKING variable in the slurm script is to disable this feature - it is not necessary and causes the Perl scripts to crash and fail
1. [Cluster mode](https://interproscan-docs.readthedocs.io/en/latest/ImprovingPerformance.html?highlight=cluster%20mode#running-interproscan-in-cluster-mode) appears not to work. More on this below.
1. Requisite modules:
   1. Java > 11
   1. CGGcore/8.3.0
   1. Python/3.7.2
   1. Perl/5.30.0


## Description of files

| filename | Description |
| --- | --- |
| ips_slurm_settings.py | This is where you define your filepaths for storage and temporary directories and for Interproscan. |
| ips_slurm_template_render.py | This renders the job template for each input file, and where you specify computational resources (partition, CPUs, memory, runtime, etc.).  |
| ips_template.sbatch | This is the template. At the start of the job, it moves the input file from the inbox to the failures folder. When the job finishes, it checks for a corresponding .tsv file and, if the job is successful in generating a .tsv output, moves the input file to the outbox.
| ips_stage.py | This file accepts a single integer argument (e.g. 'ips_stage.py 20') and and pulls the specified number of input files from /work/.../inbox folder to the /scratch/.../inbox/folder. It then renders templates and submits slurm files for each of these jobs. Before moving and submitting new input files, it moves any files in /scratch/.../failures , /scratch/.../outbox, and all .sbatch and slurm*.out files back to the respective /work... folders. |

## File structure

Five subdirectories are created to store input files (in amino acid FASTA format), Interproscan outputs (in tsv format), and SLURM files.

1. faa_inbox: contains input files to be analyzed, in amino acid fasta (.faa) format.
2. faa_outbox: contains successfully analyzed input files.
3. faa_failures: contains unsuccessfully analyzed input files.
4. slurm_files: contains slurm*.out and *.slurm files.
5. tsv_outputs: contains .tsv outputs from Interproscan.

## What other sections/info to include?



