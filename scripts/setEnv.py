#!/usr/bin/python3 -u
import fileinput

def appendLine(path, line):
	with open(path, "a") as f:
		f.write(line + "\n")

def searchAndReplace(path, pattern, value):
	for line in fileinput.input(path, inplace = True): 
	      print line.replace(pattern, value),

def setServerAddress(address):
	etm_dir = '../etm'
	env_var_name = 'ET_PUBLIC_HOST'
	env_var = env_var_name + '=' + address
	default = env_var_name + '=localhost'
	
	try:
		searchAndReplace(etm_dir + '/deploy/docker-compose-main.yml', default, env_var)
		searchAndReplace(etm_dir + '/docker/docker-compose-main.yml', default, env_var)
	except subprocess.CalledProcessError:	
		print 'Error: Environment variable could not be inserted'
		exit(1)

