# -*- coding: utf-8 -*-
#!/usr/bin/python
import paramiko 
import argparse
import string
import re




#################### ФУНКЦИИ И ПРОЦЕДУРЫ ###############################
# Обработчик параметров, переданных скрипту
parser = argparse.ArgumentParser(description='This is ssh mikrotik config fetcher!')
parser.add_argument('host')
parser.add_argument('--timeout', '-t')
parser.add_argument('--command', '-c')
args = parser.parse_args()


# Возвращает результат выполнения комманды по ssh с mikrotik
def Print_fetch_ssh(host, user, secret, commanda, time_out):

	port = 22
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	client.connect(host, username=user, password=secret, allow_agent=False, look_for_keys=False, timeout=time_out)
	stdin, stdout, stderr = client.exec_command(commanda)
	data = stdout.read() + stderr.read()
	client.close()
	print data				# Данные попадают в stdout

# Возвращает логин и пароль для данного хоста(ip)
def Get_account_from_file(file_name, ip_addr):
	#print file_name
	#print ip_addr
	login = ''
	paswd = ''
	f = open(file_name)
	for line in f:
		if (line.find(ip_addr) is not -1):			# функция find возвращает позицию вхождения или -1
			if (line.find('add user') is not -1):
				line = re.sub(r"\s+", " ", line)
				line = re.sub(r"\t+", " ", line)
				list_line = line.split(' ')
				#print list_line[3] # логин
				login = list_line[3]
			if (line.find('add password') is not -1):
				line = re.sub(r"\s+", " ", line)
				line = re.sub(r"\t+", " ", line)
				list_line = line.split(' ')
				#print list_line[3] # пароль
				paswd = list_line[3]
	return login, paswd

# Возвращает путь к дириктории пользователя
def Get_home_path():
	from os.path import expanduser
	home = expanduser("~")
	return home

# Возвращает список комманд в формате списка "list"
def Parse_cmds_string(cmds_str):
	return cmds_str.split(';')


######################### MAIN #########################################
# Обработка параметров коммандной строки
def main():
	if (str(args.timeout) != 'None') and (str(args.command) != 'None'):
		home_path = Get_home_path()
		login,paswd = Get_account_from_file( home_path + '/.cloginrc', args.host)
		
		if ((login is not '') and (paswd is not '')):
			list_cmds = Parse_cmds_string(args.command)
			for cmd_s in list_cmds:
				print "### CMD:", cmd_s
				Print_fetch_ssh(args.host, login, paswd, cmd_s, args.timeout)
		else:
			print "Account not found in .cloginrc"



###################### ТОЧКА ВХОДА В ПРОГРАММУ #########################
if __name__ == "__main__":
	main()

