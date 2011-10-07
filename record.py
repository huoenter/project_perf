import re
import socket, time

class Record(dict):

	code	 =	{
				'intervalEnd'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[2].split('-')[1],	#1
				'intervalStart'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[2].split('-')[0],	#1
				'intervalUnit'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[3],					#1
				'numBytes'					:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[4],					#1
				'numBytesUnits'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[5],					#1
				'value'						:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[6],					#1
				'valueUnits'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec',s) and s.split()[7],					#1
				'udpJitter'					:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec.*\d+',s) \
															and s.split()[8] or None,													#1.1
				'udpJitterUnit'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec.*\d+',s) \
															and s.split()[9] or None,													#1.1
				'udpPacketLoss'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec.*\d+',s) \
															and s.split()[10].split('/')[0] or None,									#1.1
				'udpPacketSent'				:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec.*\d+',s) \
															and s.split()[10].split('/')[1] or None,									#1.1
				'udpPacketLossPercentage'	:	lambda s: re.findall(r'.*\d+\.\d-\d+.\d sec.*/sec.*\d+',s) \
															and s.split()[11][1:-1] or None,											#1.1
				'sender'					:	lambda s: re.findall(r'local.*with',s) and \
															socket.gethostbyaddr(s.split('local ')[1].split()[0])[0],					#2
				'catcher'					:	lambda s: re.findall(r'local.*with',s) and \
															socket.gethostbyaddr(s.split('with ')[1].split()[0])[0],				#2
				'udpOutOfOrder'				:	lambda s: re.findall(r'.*datagrams received out-of-order.*',s) and s.split()[4] or None,		#3
				'udpBufferSize'				:	lambda s: re.findall(r'^UDP.*',s) and s.split()[3] or None,								#4
				'udpBufferUnit'				:	lambda s: re.findall(r'^UDP.*',s) and s.split()[4] or None,								#4
				'udpDatagramSize'			:	lambda s: re.findall(r'^Receiving .*datagrams',s) and s.split()[1] or None,						#5
				'udpDatagramUnit'			:	lambda s: re.findall(r'^Receiving .*datagrams',s) and s.split()[2] or None,						#5
				'metadataId'				: 	lambda s: re.findall(r'.*iperf .*',s) and s.split()[0][:-1],							#6
				'tcpAdapterType'			:	lambda s: re.findall(r'.*MSS size',s) and s.split()[9] or None,									#7
				'tcpMSSSize'				:	lambda s: re.findall(r'.*MSS size',s) and s.split()[4] or None,									#8
				'tcpMTUUnit'				:	lambda s: re.findall(r'.*MSS size',s) and s.split()[8][:-1] or None,							#8
				'tcpMTUSize'				:	lambda s: re.findall(r'.*MSS size',s) and s.split()[7][:-1] or None,							#8
				'tcpWindowSize'				:	lambda s: re.findall(r'TCP window size:',s) and s.split()[3] or None,							#9
				'tcpWindowUnit'				:	lambda s: re.findall(r'TCP window size:',s) and s.split()[4] or None,							#9
				'timeType'					:	'NULL',
				'timeValue'					:	lambda s: time.time()
				}

	def __init__(self, text):
		self.text = text
		self.d = {}
		self.parse()

	def __str__(self):
		for k, v in self.d.items():
			return k, '\t\t:\t', v

	def parse(self):
		txt = self.text
		#just initialize the d
		for k in self.code.keys(): self.d[k] = ''

		for line in txt.readlines()[1:-1]:
#			print 'A new line:'
			for k, v in self.code.items():
				try:
					if not self.d[k]:
						try: self.d[k] = self.code[k](line)
						except ValueError, AttributeError: pass 
#					print 'Try key:\t'+k+'\twith content:\t'+self.d[k]
				except TypeError: pass
	
if __name__ == '__main__':
	testcase = open('test.perf')
	r = Record(testcase)
	for k, v in r.d.items():
		print k, '\t=>\t', v
