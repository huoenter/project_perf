import MySQLdb
import os, sys

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
		else: right += '\''+value+'\''+','

	updateCommand = 'INSERT INTO clmp_bwctl (' + left[:-1] + \
					') values (' + right[:-1] + ')'
	cursor.execute(updateCommand)
	print updateCommand 

	cursor.close()
	conn.commit()
	conn.close()

def update_RRD(row):
	command = 'rrdtool update test.rrd '
	time = 900000300
	for r in row:
		command += str(time)+':'+str(r).strip('(),\'sec') + ' '
		time += 300

	if len(command) > int(ARG_MAX):
		print 'fatal: # of args = '+str(len(command)) + ' exceeds the OS limit: ' + ARG_MAX
		sys.exit(1)
	os.popen(command)

def create_RRD(name, length):
	command = 'rrdtool create test.rrd \
				--step 300 \
				--start 900000000 \
				DS:bw:GAUGE:600:0:1000000000 \
				RRA:AVERAGE:0.5:1:'+str(length)
	os.popen(command)

def sample_RRD():
	command = 'rrdtool update test.rrd '
	time = 900000300
	for i in range(200):
		c = command+str(time)+':'+str(i*500)
		os.popen(c)
		time += 300

def plot_RRD(e, size):
	command = 'rrdtool graph bw.png \
				--start '+str(e-size*300)+' --end '+str(e)+ ' \
				DEF:bw=test.rrd:bw:AVERAGE \
				LINE2:bw#FF0000'
	os.popen(command)

def test():
	#update_MySQL({})
	size = 1000
	os.popen('rm --force test.rrd')
	create_RRD('haha',size)
	cursor = conn_MySQL().cursor()
	selectCommand = 'select numBytes from clmp_bwctl where sender=\'itt128.perfsonar.uni.edu\' and catcher=\'perfsonar.its-ns.uni.edu\''
	cursor.execute(selectCommand)
	row = cursor.fetchall()
	r = row[:7000]
#	for a in str(r).split(',),'): print r
	t = 900000000 + len(r)*300
	update_RRD(r) or  plot_RRD(t, size)
#	sample_RRD() or plot_RRD(900060000)
	os.popen('scp bw.png huoc@student.cs.uni.edu:~/')


if __name__ == '__main__':
	test()
