#!/usr/bin/python
#-*- coding: utf-8 -*-

import pexpect
import time
import re
import sys


class CiscoTelnetConfig:
	def __init__(self):
		self.host = '10.90.90.100'
		self.paswd_patterns = ['PassWord:', 'Password:', 'password:']
		self.enter_patterns = ['>']
		self.enenter_patterns = ['#']
		self.time_out = 10		# sec

		self.paswd = 'JumbI'
		self.enpaswd = 'JumbI'
		#self.prompt = ['>']
		self.cmd = 'show clock'
	
	
	def Parser(self, stroka):
		list_str = stroka.split("\n")
			
		list_rez = []
		for stroka in list_str:
			stroka = re.sub(r'[^.a-zA-Z0-9!#\s\/\-\+\,\.]', "", stroka)
			list_rez.append(stroka)
		
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			list_rez.append(stroka.lstrip(' '))
		
		'''
		for stroka in list_str:
			m = re.search('DES-(.+?)-(.+?):$', stroka)
			if not m:
				list_rez.append(stroka)
		#
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			m = re.search('System Uptime(.+?):', stroka)
			if not m:
				list_rez.append(stroka)
		#
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			m = re.search('Next Page', stroka)
			if not m:
				list_rez.append(stroka)
		'''
		return list_rez
	
	
	def GetConnect(self, host, paswd, enpaswd):
		#print host
		#print paswd
		#print enpaswd
		self.host = host
		self.paswd = paswd
		self.enpaswd = enpaswd
		
		# connect by telnet
		header = ''
		sys.stderr.write('HOST:' + self.host + '\n')
		pe = pexpect.spawn('telnet ' + self.host)
		#print pe.before
		
		try:
			pe.expect_exact(self.paswd_patterns, timeout=self.time_out)
			header = header + pe.before
		except:
			sys.stderr.write('HOST:' + self.host + ' CONNECT FAILURE\n')
			pe.close()
			exit(0)
		#print pe.before
		
		# send password
		pe.sendline(self.paswd)
		try:
			pe.expect_exact(self.enter_patterns, timeout=self.time_out)
			header = header + pe.before
		except:
			sys.stderr.write('HOST:' + self.host + ' PASSWORD FAILURE\n')
			pe.close()
			exit(0)
		#print pe.before
		
		# send enable
		pe.sendline('enable')
		try:
			pe.expect_exact(self.paswd_patterns, timeout=self.time_out)
			header = header + pe.before
		except:
			sys.stderr.write('HOST:' + self.host + ' ENABLE FAILURE\n')
			pe.close()
			exit(0)
		#print pe.before
		
		# send enable password
		pe.sendline(self.enpaswd)
		try:
			pe.expect_exact(self.enenter_patterns, timeout=self.time_out)
			header = header + pe.before
		except:
			sys.stderr.write('HOST:' + self.host + ' ENABLE-PASSWORD FAILURE\n')
			pe.close()
			exit(0)

		return pe
	
	
	def DoCmd(self, pe, cmd):
		sys.stderr.write(self.host + ' COMMAND:' + cmd + '\n')
		self.cmd = cmd
		pe.sendline(cmd)
		rez = ''
		i = 0
		n = 0
		while 1:
			i += 1
			
			try:
				idx = pe.expect_exact([pexpect.EOF, '#', '--More--'], timeout=self.time_out) #expect_exact self.enenter_patterns pexpect.EOF  self.time_out ['#']
				if idx == 0:
					sys.stderr.write(self.host + '<<< EOF' + self.cmd + '\n')
					break
				elif idx == 1:
					sys.stderr.write(self.host + '<<< PROMPT ENABLE' + self.cmd + '\n')
					break
				elif idx == 2:
					sys.stderr.write(self.host + '<<< --More--' + self.cmd + ' ' + str(i) + ' ' + str(n) + '\n')
					pe.send(chr(32)) # Send space
			except:
				pass
				sys.stderr.write(self.host + ' TIMEOUT' + self.cmd + '\n')
				n += 1
				if n>10:
					sys.stderr.write(self.host + ' EXIT BY TIMEOUT\n')
					break
			
			rez = rez + pe.before
			
			time.sleep(1)
		
		return rez

	def DoDisconnect(self,pe):
		pe.sendline('exit')
		try:
			pe.expect_exect(pexpect.EOF, timeout=self.time_out)
		except:
			pass
		pe.close()

