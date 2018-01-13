#!/usr/bin/python
#-*- coding: utf-8 -*-

import pexpect
import argparse
import time
import sys
from CloginrcFinder import CloginrcFinder
from DlinkTelnet import DlinkTelnetConfig


class Dlogin:
	
	def __init__(self):
		parser = argparse.ArgumentParser(description='D-LINK module for Rancid')
		parser.add_argument('host')
		parser.add_argument('--user', '-u')
		parser.add_argument('--pasw', '-p')
		parser.add_argument('--commands', '-c')
		parser.add_argument('--timeout', '-t')
		
		args = parser.parse_args()
		
		# host
		self.host = args.host
		
		# login, paswd, enpaswd
		if (str(args.user) != 'None') and (str(args.pasw) != 'None'):
			self.login = args.user
			self.paswd = args.pasw
		else:
			c = CloginrcFinder()
			list_acks = c.GetListAcks()
			self.login, self.paswd, self.enpaswd =  c.FindAck(self.host, list_acks)
		
		# commands
		if (str(args.commands) != 'None'):
			self.cmd_list = args.commands.split(';')
		else:
			self.cmd_list = ['show time', 'show switch', 'show config current_config']
		
		# timeout
		if (str(args.timeout) != 'None'):
			self.time_out = int(args.timeout)
		else:
			self.time_out = 120
		
		if (self.login == None and self.paswd == None):
			print "NOT FOUND ACCOUNT FOR:", self.host
			sys.stderr.write(self.host + ' NOT FOUND ACCOUNT IN .cloginrc \n')
			exit(0)
		
		#self.prompt = ['[#\$]', self.login + '#', pexpect.EOF, ':.+#', ':.+\#', '#', '[:.+#]'] # for example admin#    | for example EOF    | :4#
		self.prompt = [':.+#']
		self.login_patterns = ['UserName:', 'Username:', 'username:']
		self.paswd_patterns = ['PassWord:', 'Password:', 'password:']
		#self.cmd_exit = 'logout'
		
		
	def PrintParams(self):
		print 'Host:', self.host
		print 'Login:', self.login
		print 'Password:', self.paswd
		#print 'EnPassword:', enpaswd
		print 'Commands:', self.cmd_list
		print 'Timeout:', self.time_out
		pass

	def GetConfig(self):
		rez = ''
		#print self.host
		#print self.login_patterns
		#print self.paswd_patterns
		#print self.time_out
		#print self.login
		#print self.paswd
		#print self.prompt
		#print self.cmd_exit
		
		# connect
		start = time.time()
		for cmd in self.cmd_list:
			print "COMMAND:", cmd
			dlink_telnet = DlinkTelnetConfig()
			pe = dlink_telnet.GetConnect(self.host, self.login, self.paswd)
			text = dlink_telnet.DoCmd(pe, cmd)
			dlink_telnet.DoDisconnect(pe)
			list_config = dlink_telnet.Parser(text)
			for config_str in list_config:
				#pass
				print config_str
			
		endtime = str(time.time() - start)
		sys.stderr.write(self.host + ' TIME SPEND ' + endtime +'\n')


# Тут обязательно должен быть этот код. Инициализация модуля и запуск сбора конфига.
# Ибо данный файл сразу запускается из perl скрипта rancid
c = Dlogin()
c.GetConfig()
