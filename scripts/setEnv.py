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
	except IOError:	
		print 'Error: Environment variable could not be inserted'
		exit(1)

def replaceEnvVarValue(var_name, new_value, old_value, files_paths):
	env_var_name = var_name
	new_env_var = env_var_name + '=' + new_value
	old_env_var = env_var_name + '=' + old_value
	
	try:
		for file_path in files_paths:
			searchAndReplace(file_path, old_env_var, new_env_var)
	except IOError:
		print 'Error: Environment variable could not be inserted'
		exit(1)

def replaceKeyValue(key_name, new_value, old_value, files_paths):
	new_key_entry = key_name + ': ' + new_value
	old_key_entry = key_name + ': ' + old_value
	
	try:
		for file_path in files_paths:
			searchAndReplace(file_path, old_key_entry, new_key_entry)
	except IOError:
		print 'Error: Environment variable could not be inserted'
		exit(1)

