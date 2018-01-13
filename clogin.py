#!/usr/bin/python
#-*- coding: utf-8 -*-

import pexpect
import argparse
import time
import sys
from CloginrcFinder import CloginrcFinder
from CiscoTelnet import CiscoTelnetConfig


class Clogin:
	
	def __init__(self):
		parser = argparse.ArgumentParser(description='CISCO module for Rancid')
		parser.add_argument('host')
		parser.add_argument('--pasw', '-u')
		parser.add_argument('--enpasw', '-e')
		parser.add_argument('--commands', '-c')
		parser.add_argument('--timeout', '-t')
		
		args = parser.parse_args()
		
		# host
		self.host = args.host
		
		# login, paswd, enpaswd
		if (str(args.pasw) != 'None') and (str(args.enpasw) != 'None'):
			self.paswd = args.pasw
			self.enpaswd = args.enpasw
		else:
			c = CloginrcFinder()
			list_acks = c.GetListAcks()
			self.login, self.paswd, self.enpaswd =  c.FindAck(self.host, list_acks)
		
		# commands
		if (str(args.commands) != 'None'):
			self.cmd_list = args.commands.split(';')
		else:
			self.cmd_list = ['show clock', 'show snmp', 'show running-config']
		
		# timeout
		if (str(args.timeout) != 'None'):
			self.time_out = int(args.timeout)
		else:
			self.time_out = 120
		
		# check account
		if (self.paswd == None and self.enpaswd == None):
			#print "NOT FOUND ACCOUNT FOR:", self.host
			sys.stderr.write(self.host + ' NOT FOUND ACCOUNT IN .cloginrc \n')
			exit(0)
	
	
	def PrintParams(self):
		print self.host
		print self.paswd
		print self.enpaswd
		print self.cmd_list
		print self.time_out
	
	
	def GetConfig(self):
		rez = ''
		
		# connect
		start = time.time()
		sys.stderr.write(self.host + ' START\n')
		for cmd in self.cmd_list:
			cisco_telnet = CiscoTelnetConfig()
			pe = cisco_telnet.GetConnect(self.host, self.paswd, self.enpaswd)
			text = cisco_telnet.DoCmd(pe, cmd)
			cisco_telnet.DoDisconnect(pe)
			list_config = cisco_telnet.Parser(text)
			for config_str in list_config:
				#pass
				print config_str
			
		endtime = str(time.time() - start)
		sys.stderr.write(self.host + ' TIME SPEND ' + endtime +'\n')




c = Clogin()
c.GetConfig()


