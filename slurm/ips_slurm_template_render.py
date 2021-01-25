import re
import os
from ips_slurm_settings import *

def render_template(faa_input_filename):
	
	d=open(slurm_template,'r')
	slurm_text=d.read()
	d.close()
	#hard-coding these parameters for now
	#but values like memory and wall time could be turned into functions of the input file size
	#would put that in a function in this file
	slurm_header_params= {
	'partition':'commons',
	'ntasks':'1',
	'nodes':'1',
	'cpus-per-task':'4',
	'threads-per-core':'1',
	'mem-per-cpu':'2GB',
	'running-time':'01:00:00',
	'export':'ALL'
	}
		
	for header in slurm_header_params:
		slurm_text=re.sub('{{%s}}' %header,slurm_header_params[header],slurm_text)
	
	faa_input_filepath=os.path.join(scratch_dir,faa_inbox,faa_input_filename)
	faa_id=re.search('[0-9]+',faa_input_filename).group(0)
	tsv_output_filepath=os.path.join(scratch_dir,tsv_outputs,'FAA_ID'+str(faa_id))
	faa_scratch_outbox=os.path.join(scratch_dir,faa_outbox)
	faa_scratch_failures=os.path.join(scratch_dir,faa_failures)
	faa_input_in_failures=os.path.join(scratch_dir,faa_failures,faa_input_filename)

	slurm_body_params={
	'IPSPATH':IPSPATH,
	'tsv_output_filepath':tsv_output_filepath,
	'faa_input_filepath':faa_input_filepath,
	'faa_scratch_outbox':faa_scratch_outbox,
	'faa_scratch_failures':faa_scratch_failures,
	'faa_input_in_failures':faa_input_in_failures
	}
	
	for param in slurm_body_params:
		slurm_text=re.sub('{{%s}}' %param,slurm_body_params[param],slurm_text)
	slurmfilename=faa_id+'.sbatch'
	print(slurmfilename)
	d=open(slurmfilename,'w')
	d.write(slurm_text)
	d.close()
	return(slurmfilename)
