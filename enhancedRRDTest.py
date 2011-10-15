import os, sys
from record import Record  #This is chen's file, should be included in the dir
from optparse import OptionParser
import conf
from updater import *  #This is chen's file, should be included in the dir

def updateTestRRDDb(dbname, r, items):
	command =	'rrdtool update ' + dbname + ' '\
				'N:' + ':'.join([r.d[x] for x in items])
	print command
	os.popen(command)

def readFromSout():
	input = sys.stdin
	return Record(input)


def _optParser(parser):

	parser.add_option("-d", "--database", dest = "dbname", default = 'test.rrd',
						help = 'Specify a name for the rrd db.\t[default=%default]')
	parser.add_option("-s", "--step", dest = "step", default = '1000',
						help = 'Specify the step length\n'+\
						'For <create>\t[default=%default]')
	parser.add_option("-b", "--start", dest = "start", default = '-500000',
						help = 'start time to plot. default is 50000 sec before now\t[default=%default]')
	parser.add_option("-e", "--end", dest = "end", default = 'N',
						help = 'end time to plot. default is NOW\t[default=%default]')
	parser.add_option("-t", "--from", dest = "interval", default = 'no',
						help = "for <plot>&<plotall> most helpful time interval selection."+\
						"e.g. -t lastmonth see or change choices in conf.py")
	parser.add_option("-p", "--protocol", dest = "protocol", default = 'tcp',
						help = "For <dump> tcp or udp?\t[default=%default]")
	return parser.parse_args()


def main():
	usage = '''
			python enhancedRRDTest.py [create|update|plot|plotall|dump] [options]
			Example1:
				python enhancedRRDTest.py create -d test.rrd --step 250
				while doing the bwctl test:
					cat bwctloutput | python enhancedRRDTest.py update -d test.rrd
				python enhancedRRDTest.py plot -d test.rrd -t lastweek
			Example2: Dump from a mysqldb. (customized by conf.py)
				python enhancedRRDTest.py dump -p tcp
				python enhancedRRDTest.py plotall -t lastday
				python enhancedRRDTest.py plotall --start 1313000000 --end 1313130000
			'''
	
	p = OptionParser(usage=usage)
	(options, args) = _optParser(p)
	if len(args) == 0: 
		print 'try: python <scriptname> -h'
		sys.exit(1)
	if args[0] == 'create': createTestRRDDb(options.dbname, options.step, conf._items)
	elif args[0] == 'update': 
		r = readFromSout()
		updateTestRRDDb(options.dbname, r, conf._items)
	elif args[0] == 'plot': 
		plotTestRRDDb(options.start, options.end, options.dbname, options.interval, conf._items)
	elif args[0] == 'plotall':
		for pairs in permutateHosts(conf._hosts):
			rrdname = pairs[0].split('.')[0] + pairs[1].split('.')[0]+'.rrd'
			plotTestRRDDb(options.start, options.end, rrdname, options.interval, conf._items)
		os.popen('scp *.png huoc@student.cs.uni.edu:~/')
	elif args[0] == 'dump': 
		dumpFromMySQL(conf._items, options.step, options.protocol)
	else: print 'try: python <scriptname> -h'

if __name__ == '__main__':
	main()

