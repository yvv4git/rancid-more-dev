#!/usr/bin/python
#-*- coding: utf-8 -*-

import pexpect
import time
import re
import sys


class RwrTelnetConfig:
	def __init__(self):
		self.host = '192.16.191.56'
		self.login_patterns = ['UserName:', 'Username:', 'username:', 'Login:', 'login:']
		self.paswd_patterns = ['PassWord:', 'Password:', 'password:']
		self.time_out = 10		# sec
		
		self.login = 'root'
		self.paswd = 'XXXXX'
		self.prompt = ['>']
		self.cmd = 'config show'
		
		
	def Parser(self, stroka):
		list_str = stroka.split("\n")
		
		list_rez = []
		for stroka in list_str:
			stroka = re.sub(r'[^.a-zA-Z0-9!#\s\/\-\+\,\.]', "", stroka)
			stroka = stroka.strip()
			list_rez.append(stroka)
			
			
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			list_rez.append(stroka.lstrip(' '))
		
		
		return list_rez
		
		
	def GetConnect(self, host, login, paswd):
		#print 'Login:', login
		#print 'Paswd:', paswd
		header = ''
		self.host = host
		self.login = login
		self.paswd = paswd
		sys.stderr.write(self.host + ' START\n')
		pe = pexpect.spawn('telnet ' + self.host)
		
		try:
			pe.expect(self.login_patterns, timeout=self.time_out)
		except pexpect.TIMEOUT:
			sys.stderr.write(self.host + ' TIMEOUT: login\n')
			exit(0)
		header = header + pe.before
		#print header
		
		# send login
		pe.sendline(self.login + '\r')
		try:
			pe.expect(self.paswd_patterns, timeout=self.time_out)
		except pexpect.TIMEOUT:
			sys.stderr.write(self.host + ' TIMEOUT: password\n')
			exit(0)
		header = header + pe.before
		#print header
		
		# send password
		pe.sendline(self.paswd + '\r')
		try:
			pe.expect(self.prompt, timeout=self.time_out)
		except pexpect.TIMEOUT:
			sys.stderr.write(self.host + ' TIMEOUT: prompt >   MAY BE WRONG ACCOUNT\n')
			exit(0)
		header = header + pe.before
		#print header
		
		return pe
	
	
	def DoCmd(self, pe, cmd):
		sys.stderr.write(self.host + ' COMMAND:' + cmd + '\n')
		self.cmd = cmd
		pe.sendline(self.cmd + '\r')
		rez = ''
		i = 1
		n = 1
		while 1:
			try:
				idx = pe.expect(['>', '-- more --'], timeout=self.time_out) # _exact
				if idx == 0:
					sys.stderr.write(self.host + '<<< PROMPT(>)' + str(i) + ' ' + str(n) +'\n')
					rez = rez + pe.before
					
					#print rez
					m = re.search('(.+?)#[0-9]', rez)
					if m:
						sys.stderr.write(self.host + ' EXIT BY PROMPT\n')
						break
				if idx == 1:
					sys.stderr.write(self.host + '<<< -- more --' + str(i)  + ' ' + str(n) +'\n')
					rez = rez + pe.before
					pe.sendline(chr(32) + '\r')
			except pexpect.TIMEOUT:
				sys.stderr.write(self.host + 'TIMEOUT: prompt > or -- more --'  + ' ' + str(n) +'\n')
				n += 1
				
				if n > 10:
					break
			
			rez = rez + pe.before
			i += 1
		return rez
	
	def DoDisconnect(self,pe):
		pe.sendline('exit\r')
		try:
			pe.expect_exect(pexpect.EOF, timeout=self.time_out)
		except:
			pass
		pe.close()


