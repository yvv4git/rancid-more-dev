#!/usr/bin/python
#-*- coding: utf-8 -*-

import pexpect
import argparse
import time
import sys
from CloginrcFinder import CloginrcFinder
from RwrTelnet import RwrTelnetConfig


class Rlogin:
	def __init__(self):
		parser = argparse.ArgumentParser(description='RWR module for Rancid')
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
			self.cmd_list = ['config show']
		
		# timeout
		if (str(args.timeout) != 'None'):
			self.time_out = int(args.timeout)
		else:
			self.time_out = 120
		
		if (self.login == None and self.paswd == None):
			print "NOT FOUND ACCOUNT FOR:", self.host
			sys.stderr.write(self.host + ' NOT FOUND ACCOUNT IN .cloginrc \n')
			exit(0)
	
	
	def PrintParams(self):
		print 'Host:', self.host
		print 'Login:', self.login
		print 'Password:', self.paswd
		print 'Commands:', self.cmd_list
		print 'Timeout:', self.time_out
	
	
	def GetConfig(self):
		rez = ''
		
		# connect
		start = time.time()
		for cmd in self.cmd_list:
			print "COMMAND:", cmd
			rwr_telnet = RwrTelnetConfig()
			pe = rwr_telnet.GetConnect(self.host, self.login, self.paswd)
			text = rwr_telnet.DoCmd(pe, cmd)
			rwr_telnet.DoDisconnect(pe)
			list_config = rwr_telnet.Parser(text)
			for config_str in list_config:
				print config_str
			
		endtime = str(time.time() - start)
		sys.stderr.write(self.host + ' TIME SPEND ' + endtime +'\n')


c = Rlogin()
c.GetConfig()
