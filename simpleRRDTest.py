import os, sys
from record import Record  #This is chen's file, should be included in the dir
from optparse import OptionParser

ARG_MAX = os.popen('getconf ARG_MAX').read()

def createTestRRDDb(dbname, step):
	command = 	'rrdtool create ' + dbname + ' '\
				'--start N ' + \
				'--step ' + str(step) + ' '\
				'DS:bw:GAUGE:'+str(step*5)+':0:U '+ \
				'RRA:AVERAGE:0.5:1:500 ' + \
				'RRA:AVERAGE:0.5:5:500 ' + \
				'RRA:AVERAGE:0.5:10:500'
				
	print command
	os.popen(command)

def updateTestRRDDb(dbname, r):
	command =	'rrdtool update ' + dbname + ' '\
				'N:' + r.d['numBytes']
	print command
	os.popen(command)

def readFromSout():
	input = sys.stdin
	return Record(input)

def plotTestRRDDb(start, end, dbname):
	command =	'rrdtool gragh test.png ' + \
				'--start '+start+'--end '+end + ' '\
				'DEF:bw='+dbname+':bw:AVERAGE ' + \
				'LINE2:bw#FF5555'

def _optParser(parser):

	parser.add_option("-d", "--database", dest = "dbname", default = 'test.rrd',
						help = 'Specify a name for the rrd db.\t[default=%default]')
	parser.add_option("-s", "--step", dest = "step", default = '1000',
						help = 'Specify the step length\n'+\
						'NOTE: Step is suggested to be at least longer than your actual test interval\t[default=%default]')
	parser.add_option("-b", "--start", dest = "start", default = '-500000',
						help = 'start time to plot. default is 50000 sec before now\t[default=%default]')
	parser.add_option("-e", "--end", dest = "end", default = 'N',
						help = 'end time to plot. default is NOW\t[default=%default]')
	return parser.parse_args()

def main():
	usage = '''IMPORTANT: record.py must be in the directory
		#1 python simpleRRDTest.py create [-d databasename] [-s steplenthofrrddb]
		#2 (get sth on stdout) | python simpleRRDTest.py update [-d databasename]
		e.g.:   cat testouput | python simpleRRDTest.py update
		#3 python simpleRRDTest.py plot [-b begintime] [-e endtime] [-d databasename]
			'''
	
	p = OptionParser(usage=usage)
	(options, args) = _optParser(p)

	if args[0] == 'create': createTestRRDDb(options.dbname, options.step)
	elif args[0] == 'update' or len(args) == 0: 
		r = readFromSout()
		updateTestRRDDb(options.dbname, r)
	elif args[0] == 'plot': plotTestRRDDb(options.start, options.end, options.dbname)

if __name__ == '__main__':
	main()

