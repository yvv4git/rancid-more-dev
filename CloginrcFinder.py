#!/usr/bin/python
#-*- coding: utf-8 -*-
import re

class CloginrcFinder:
	def __init__(self):
		self.clfile_path = '/home/admin/.cloginrc'
	
	def GetListAcks(self):
		list_acks = open(self.clfile_path, "r").readlines()
		list_tmp = []
		list_rez = []
		
		for l in list_acks:
			s = re.sub( '\s+', '\t', l )
			s = s.replace('\n', '')
			if ((s != '') and (s[:1] != '#')):
				list_tmp.append(s)
		
		for l in list_tmp:
			l_list = l.split('\t')
			if (len(l_list)>4):
				list_rez.append(l_list)
		
		return list_rez
	
	def FindAck(self, host_ip, list_acks):
		login = None
		paswd = None
		enpaswd = None
		for l in list_acks:
			if (l[2] == host_ip):
				if (l[1] == 'user'):
					login = l[3]
				elif (l[1] == 'password'):
					if (l[4] != ''):
						paswd = l[3]
						enpaswd = l[4]
					else:
						paswd = l[3]

		return login, paswd, enpaswd

