#!/usr/bin/python
#-*- coding: utf-8 -*-

import pexpect
import time
import re
import sys


class DlinkTelnetConfig:
	def __init__(self):
		self.host = '172.16.100.30'
		self.login_patterns = ['UserName:', 'Username:', 'username:', 'Login:', 'login:']
		self.paswd_patterns = ['PassWord:', 'Password:', 'password:']
		self.time_out = 15		# sec

		self.login = 'admin'
		self.paswd = 'polka'
		self.prompt = ['Next Entry', ':.+#', ":.+#", "#$", "#\$", self.login + '#', '[#\$]', '[:.+#]',':4#', ':3#', '>']
		self.cmd = 'show config current_config'
	
	def Parser(self, stroka):
		list_str = stroka.split("\n")
		list_rez = []
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
		#DES-3526:
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			m = re.search('DES-(.+?):(.+?)$', stroka)
			if not m:
				list_rez.append(stroka)
		#********
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			m = re.search('(\*+?)', stroka)
			if not m:
				list_rez.append(stroka)
		#Command:
		list_str = list_rez
		list_rez = []
		for stroka in list_str:
			m = re.search('Command:', stroka)
			if not m:
				list_rez.append(stroka)
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
		#print pe.before
		
		try:
			pe.expect(self.login_patterns)
		except pexpect.TIMEOUT:
			sys.stderr.write(self.host + ' ERR: may be this is CISCO ---> no login prompt find\n')
			exit(0)
		header = header + pe.before
		
		# send login
		pe.sendline(self.login)
		try:
			pe.expect_exact(self.paswd_patterns)
			header = header + pe.before
		except:
			sys.stderr.write(self.host + ' MAY BE THIS IS CISCO\n')
		
		# send password
		pe.sendline(self.paswd)
		try:
			pe.expect__exact(self.prompt)
			header = header + pe.before
		except:
			#print pe.before
			#special prompt
			m = re.search(':(.+?)#', pe.before)
			if m:
				sys.stderr.write(self.host + ' SPECIAL PROMPT: :(:?)#\n')
			m = re.search('Fail', pe.before)
			if m:
				sys.stderr.write(self.host + ' ACCOUNT FAILURE\n')
				pe.close()
				exit(0)
		
		return pe
	
	
	def DoCmd(self, pe, cmd):
		sys.stderr.write(self.host + ' COMMAND:' + cmd + '\n')
		self.cmd = cmd
		pe.sendline(cmd)
		rez = ''
		i = 0
		
		time.sleep(2) # некоторые устройства тормозят и не сразу могут среагировать
		while 1:
			i += 1
			
			try:
				idx = pe.expect(['>(.*)$', '#$', '# $', 'Next Entry'], timeout=self.time_out)
				tmp_buffer = pe.before
				rez = rez + tmp_buffer
				#print '----------------->', tmp_buffer
				#print '==========idx========', idx
				
				# Next Entry
				if idx == 3:
					pe.sendline('a')
					sys.stderr.write(self.host + ' SEND a FOR Next Entry\n')
				
				elif idx < 3:
					#System locked by other session!
					m = re.search('System locked by other session', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   System locked by other session!\n')
						break
					# Invalid input detected.at
					m = re.search('Invalid input', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   Invalid input detected.at  --> MAY BE WRONG COMMAND\n')
						break
					
					# Next Entry with timoeout
					m = re.search('Next Entry', tmp_buffer)
					if m:
						pe.sendline('a')
						sys.stderr.write(self.host + ' SEND A AND BREAK   Next Entry\n')
						break
					
					##### specific prompt
					# B.Khmeln itsky133:admin#
					m = re.search(':admin$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   :admin$\n')
						break
					# B.Khmeln itsky133:root#
					m = re.search(':root$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   :root$\n')
						break
					#
					m = re.search('DGS-\d+-\d+$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   DGS-D-D\n')
						break
					#
					m = re.search('DES-\d+-\d+$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   DES-D-D\n')
						break
					#
					m = re.search('DES-\d+-\d+:(.+)$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   DES-D-D:USER$\n')
						break
					# DES-3526:admin#
					m = re.search('DES-\d+(.+)$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   DES-D:USER$\n')
						break
					# DGS-1210-10/ME:5#
					m = re.search('DGS-\d+-\d+(.+)ME:(.+)$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   DGS-D-D\\ME:\D$\n')
						break
					# DGS-3420-28SC:admin#
					m = re.search('DGS-\d+-\w+:(.+)$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   DGS-D-D\\ME:\D$\n')
						break
					# Bel-BS4-sw02:5#
					m = re.search('\w-\w+-\w+:(.+)$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   W-W-W:D$\n')
						break
					# Bel-K amazst21:4#
					m = re.search(':\d$', tmp_buffer)
					if m:
						sys.stderr.write(self.host + ' EXIT BY MATCHES:   W-W-W:D$\n')
						break
				
				# other
				sys.stderr.write(self.host + ' NO MATCHES - LOOP\n')
			except pexpect.TIMEOUT:
				sys.stderr.write(self.host + ' TIMOUT:' + str(i) + '\n')
			
			tmp_buffer = pe.before
			rez = rez + tmp_buffer

			# в самом жестком случае завершаем loop, если количество итераций слишком большое
			# максимальное количество итерайций ожидания prompt'а
			if i>10:	# 10
				sys.stderr.write(self.host + ' EXIT BY TIMEOUT\n')
				break
			
			# Incorrect Login/Password
			m = re.search('Incorrect Login/Password', tmp_buffer)
			if m:
				sys.stderr.write(self.host + ' ERR: ACCOUNT FAULURE\n')
				break
		
		return rez
	
	
	def DoDisconnect(self,pe):
		pe.sendline('logout')
		try:
			pe.expect_exect(pexpect.EOF, timeout=self.time_out)
		except:
			pass
		sys.stderr.write(self.host + ' END FETCH CONFIGURATION\n')
		pe.close()
