import MySQLdb
import os, sys, conf
import itertools

size = 20
step = 1000
sample = 8000
ARG_MAX = os.popen('getconf ARG_MAX').read()

def conn_MySQL(host = 'localhost', user = 'root', passwd = 'temp@123' \
							, db = 'perfsonar_ma'):
	conn = MySQLdb.connect(host, user, passwd, db)
	return conn

def update_MySQL(d, lst):
	conn = apply(conn_MySQL, tuple(lst))
	cursor = conn.cursor()
	#combine the command
	left = ''
	right = ''
	for key, value in d.items():
		left += key+','
		if value == None: right += '\''+'NULL'+'\''+','
		else: right += '\''+str(value)+'\''+','

	updateCommand = 'INSERT INTO clmp_bwctl (' + left[:-1] + \
					') values (' + right[:-1] + ')'
	cursor.execute(updateCommand)
	print updateCommand 

	cursor.close()
	conn.commit()
	conn.close()

def update_RRD(row, dbname='test.rrd'):
	command = 'rrdtool update ' + dbname+ ' '
	for r in row:
#		command += r[0].strip('(),\'sec')+':'+r[1].strip('(),\'sec') + ' '
		command += r[0].strip('(),\'sec')
		for rr in r[1:]: command += ':'+rr
		command += ' '

#	print command
	print len(command.split())
	if len(command) > int(ARG_MAX):
		print 'fatal: # of args = '+str(len(command)) + ' exceeds the OS limit: ' + ARG_MAX
		sys.exit(1)
	os.popen(command)

#def create_RRD(begin):
#	command = 'rrdtool create test.rrd \
#				--start '+str(int(begin)-step)+' \
#				--step '+str(step)+ ' \
#				DS:bw:GAUGE:'+str(step*5)+':0:10000000000 RRA:AVERAGE:0.5:1:'+str(size)
#	os.popen(command)
##
#def sample_RRD():
#	command = 'rrdtool update test.rrd '
#	time = 900000300
#	for i in range(200):
#		c = command+str(time)+':'+str(i*500)
#		os.popen(c)
#		time += 300
#
#def plot_RRD(begin,e):
#	print 'End time is ' + str(e)
#	command = 'rrdtool graph bw.png \
#				--start '+str(begin)+' --end '+str(e)+ ' \
#				DEF:bw=test.rrd:bw:AVERAGE \
#				LINE2:bw#FF5555'
#	print command
#	os.popen(command)

def createTestRRDDb(dbname, step, items):
	

	command = 	'rrdtool create ' + dbname + ' '\
				'--start 900000000 ' + \
				'--step ' + str(step) + ' '
	for i in items:
		command += 'DS:'+i+':GAUGE:'+str(step*3)+':0:U '
	for k, v in conf._d.items():
		command += 'RRA:AVERAGE:0.5:1:'+str(int(v)//int(step)*-1)+' '
#	command +=	'RRA:AVERAGE:0.5:1:500 ' + \
#				'RRA:AVERAGE:0.5:5:500 ' + \
#				'RRA:AVERAGE:0.5:10:500'
				
	print command
	os.popen(command)

def sortByTime(rows):
	'time is the first field in row in rows'
	r = sorted(rows, key=lambda t : t[0])
	last = rows[0][0]
	rr = []
	for x in r[1:]:
		if x[0] !=  last:
			rr.append(x)
		last = x[0]
	return rr

def inspectDiff(row):
	last = int(row[0][0])
	for r in row[1:]:
		print str(int(r[0])-last),
		last = int(r[0])

def rrdFetch(begin, end):
	command = 'rrdtool fetch test.rrd AVERAGE --start '+str(begin)+' --end '+str(end)
	print os.popen(command).read()

def permutateHosts(hosts):
	try:
		for p in itertools.permutations(hosts, 2): yield p
	except:
		print 'Please update python to 2.6 or newer. Just grab first 2'
		yield (hosts[0], hosts[1])

def generateConditions(pair, items):
	table = conf._table
	command = 'select timeValue,'+','.join(items)+' from '+table+\
			' where sender=\''+pair[0]+'\' '+ \
			' and catcher=\''+pair[1]+'\' '+ \
			' and udpPacketLossPercentage=\'\''
	return command

def plotTestRRDDb(start, end, dbname, interval, items):
	if interval != 'no': start = conf._d[interval]	
	if end != 'N' and interval != 'no':
		start =str(int(end)+int(conf._d[interval]))
	command =	'rrdtool graph '+dbname.split('.')[0]+'.png ' + \
				'--start '+start+' --end '+end + ' ' + \
				'--slope-mode ' + \
				'-w 1024 -h 600 ' + \
				'--title \"' + ' and '.join(items) + '\" ' + \
				'--vertical-label \"haha\"  '
		#		'--right-axis 2:0 ' 
	j = 0
	for i in items:
		command +=	'DEF:'+i+'='+dbname+':'+i+':AVERAGE ' + \
				'LINE2:'+i+'#'+conf._color[j]+':'+'\"'+i+'\" '
		j+=1
	print command
	os.popen(command)

def dumpFromMySQL(items, step):
	for pairs in permutateHosts(conf._hosts):
		rrdname = pairs[0].split('.')[0] + pairs[1].split('.')[0]+'.rrd'
		if not os.path.exists(rrdname): createTestRRDDb(rrdname, step, items)
		cursor = apply(conn_MySQL, conf._mysqlConf).cursor()
		command = generateConditions(pairs, items)
		print command
		cursor.execute(command)
		row = cursor.fetchall()
		row = sortByTime(row)
		row = row[:sample]
		inspectDiff(row)
		update_RRD(row, rrdname)
			
def test():
	#update_MySQL({})

	os.popen('rm --force test.rrd')
	cursor = conn_MySQL().cursor()
	selectCommand = 'select timeValue, numBytes from clmp_bwctl where sender=\'itt128.perfsonar.uni.edu\' and \
				catcher=\'perfsonar.its-ns.uni.edu\' and udpPacketLossPercentage=\'\''
	cursor.execute(selectCommand)
	row = cursor.fetchall()
	r = sortByTime(row)
	inspectDiff(r[:sample])
	rr = r[:sample]
	begin = int(rr[0][0])
	end = int(rr[-1][0])
	create_RRD(begin)
	update_RRD(rr)
	plot_RRD(end -step*size,end)
#	rrdFetch(end-step*size, end)
#	sample_RRD() or plot_RRD(900060000)
	os.popen('scp bw.png huoc@student.cs.uni.edu:~/')


if __name__ == '__main__':
	generateCondition(conf._hosts, 1)
