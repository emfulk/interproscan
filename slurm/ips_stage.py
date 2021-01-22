import os
import re
import sys
from ips_slurm_settings import *
import ips_slurm_template_render as slurm_render

array_size=int(sys.argv[1])
print("requested job array size:",array_size)

#establish the base directories in ips_slurm_settings.py
#e.g.:
##scratch_dir='/scratch/ips/files/path/'
##work_dir='/work/ips/files/path'

#FIRST, MAKE SURE THIS SCRIPT IS BEING RUN ON /SCRATCH
pwd=os.getcwd()
if not re.match('/scratch',pwd,re.I):
	print('ERROR: this script must be run on your scratch subdirectory')
	exit()

#then check for appropriate subdirs in base directories

def dircheck(base_dir,sub_dirs,essential=0):
	for sub_dir in sub_dirs:
		fullpath=os.path.join(base_dir,sub_dir)
		if not os.path.exists(fullpath):
			if essential==1:
				print('essential directory missing: ',fullpath)
				exit()
			else:
				print('creating: missing supporting directory: ',fullpath)
				os.makedirs(fullpath)

dircheck(work_dir,essential_work_subdirs,essential=1)
dircheck(work_dir,supporting_work_subdirs,essential=0)
dircheck(scratch_dir,supporting_scratch_subdirs,essential=0)

#cleanup previous work
failures=[i for i in os.listdir(os.path.join(scratch_dir,faa_failures)) if i.endswith('.faa')]
successes=[i for i in os.listdir(os.path.join(scratch_dir,faa_outbox)) if i.endswith('.faa')]
tsv_outfiles=[i for i in os.listdir(os.path.join(scratch_dir,tsv_outputs)) if i.endswith('.tsv')]
slurm_outfile_dictionary={}
slurm_outfiles=[i for i in os.listdir(scratch_dir) if i.endswith('.out')]
for f in slurm_outfiles:
	d=open(f,'r')
	t=d.read()
	d.close()
	try:
		faa_id=re.search('[0-9]+(?=\.genes\.faa)',t).group(0)
		slurm_outfile_dictionary[faa_id]=f
	except:
		pass

def ship_out(filenames,faa_id_pattern,inpath,outpath,include_slurm=1):
	for f in filenames:
		os.system('mv %s %s' %(os.path.join(inpath,f),os.path.join(outpath,f)))
		if include_slurm==1:
			faa_id=re.search(faa_id_pattern,f).group(0)
			slurm_outfile=slurm_outfile_dictionary[faa_id]
			print(slurm_outfile)
			sbatch_file=faa_id+'.sbatch'
			print(f,slurm_outfile,sbatch_file)
			for s in [slurm_outfile,sbatch_file]:
				os.system('mv %s %s' %(os.path.join(scratch_dir,s),os.path.join(work_dir,slurm_files,s)))

print("moving finished files to /work")

print(len(failures),'failures:')
ship_out(failures,re.compile('[0-9]+'),os.path.join(scratch_dir,faa_failures),os.path.join(scratch_dir,faa_failures))
print(len(successes),'successes')
ship_out(successes,re.compile('[0-9]+'),os.path.join(scratch_dir,faa_outbox),os.path.join(scratch_dir,faa_outbox))
ship_out(tsv_outfiles,re.compile('(?<=FAA_ID)[0-9]+'),os.path.join(scratch_dir,tsv_outputs),os.path.join(work_dir,tsv_outputs),include_slurm=0)
	


#get the first N unprocessed faa files from /work
unprocessed_faa_files=[i for i in os.listdir(os.path.join(work_dir,faa_inbox)) if i.endswith('.faa')]
unproc=len(unprocessed_faa_files)
if unproc==0:
	"no faa files found. exiting."
	exit()
elif unproc<array_size:
	"only %d unprocessed faa files found. reducing job array size." %unproc
	array_size=unproc

#keeping it simple for now.
#make the file list, stage them in, create the slurm file, execute
array_files=unprocessed_faa_files[:array_size]

for array_filename in array_files:
	os.system("mv %s %s" %(os.path.join(work_dir,faa_inbox,array_filename),os.path.join(scratch_dir,faa_inbox,array_filename)))
	slurmfile=slurm_render.render_template(array_filename)
	os.system("sbatch " + slurmfile)


