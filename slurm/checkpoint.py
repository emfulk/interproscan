import os
import re
#define the output and input file paths here
tsv_finished_filepath='............./ips/fasta_files/tsv_outputs'
faa_unfinished_filepath='.........../ips/fasta_files/in'
faa_limbo_filepath='............./ips/fasta_files/limbo'
slurmout_filepath='/scratch/....../ips'
faa_finished_filepath='........./ips/fasta_files/out'

for directory in [tsv_finished_filepath,faa_unfinished_filepath,faa_limbo_filepath,slurmout_filepath,faa_finished_filepath]:
	if not os.path.exists(directory):
		os.makedirs(directory)

finished_tsv_files=[i for i in os.listdir(tsv_finished_filepath) if i.endswith('.tsv')]
unfinished_faa_files=[i for i in os.listdir(faa_unfinished_filepath) if i.endswith('.faa')]
limbo_faa_files=[i for i in os.listdir(faa_limbo_filepath) if i.endswith('.faa')]
slurm_outfiles=[i for i in os.listdir(slurmout_filepath) if i.endswith('.out')]

fasta_faa_id_pattern=re.compile('[0-9]+')
tsv_faa_id_pattern=re.compile('(?<=FAA\.)[0-9]+')

finished_faa_ids=[re.search(tsv_faa_id_pattern,i).group(0) for i in finished_tsv_files]
limbo_faa_ids=[re.search(fasta_faa_id_pattern,i).group(0) for i in limbo_faa_files]

slurm_faa_ids=[]
for slurm_outfile in slurm_outfiles:
	d=open(slurm_outfile,'r')
	t=d.read()
	d.close()
	slurm_faa_ids.append(re.search('[0-9]+(?=\.genes\.faa)',t).group(0))


def move_files(filenames,matchpattern,inpath,outpath,comparison_ids):
	moved_filenames=[]
	for filename in filenames:
		faa_id=re.search(matchpattern,filename).group(0)
		if faa_id in comparison_ids:
			os.rename(os.path.join(inpath,filename),os.path.join(outpath,filename))
			print(filename)
			moved_filenames.append(filename)
	return(moved_filenames)

print("files that have recently finished running:")
recently_finished = move_files(limbo_faa_files,fasta_faa_id_pattern,faa_limbo_filepath,faa_finished_filepath,finished_faa_ids)
recently_finished += move_files(unfinished_faa_files,fasta_faa_id_pattern,faa_unfinished_filepath,faa_finished_filepath,finished_faa_ids)
print("%d total\n-------" %len(recently_finished))


unfinished_faa_files=[i for i in os.listdir(faa_unfinished_filepath) if i.endswith('.faa')]
print("files that have recently started running:")
recently_started = move_files(unfinished_faa_files,fasta_faa_id_pattern,faa_unfinished_filepath,faa_limbo_filepath,slurm_faa_ids)
print("%d total\n-------" %len(recently_started))


unfinished_faa_files=[i for i in os.listdir(faa_unfinished_filepath) if i.endswith('.faa')]

print("%d unfinished faa files in " %len(unfinished_faa_files) + faa_unfinished_filepath)


d=open('unfinished.txt','w')
d.write('\n'.join(unfinished_faa_files))
d.close()
