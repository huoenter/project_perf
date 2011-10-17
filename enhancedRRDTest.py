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
	parser.add_option("-b", "--start", dest = "start", default = 'no',
						help = 'start time to plot. default is 50000 sec before now\t[default=%default]')
	parser.add_option("-e", "--end", dest = "end", default = 'N',
						help = 'end time to plot. default is NOW\t[default=%default]')
	parser.add_option("-t", "--from", dest = "interval", default = 'no',
						help = "for <plot>. most helpful time interval selection."+\
						"e.g. -t lastmonth see or change choices in conf.py")
	parser.add_option("-p", "--protocol", dest = "protocol", default = 'tcp',
						help = "For <dump> tcp or udp?\t[default=%default]")
	parser.add_option("-a", "--all", action= "store_true", dest = "all", default = False,
						help = "if set, when plot or update, do for all. Based on permutation on hosts.")
	parser.add_option("-m", "--mysql", action= "store_true", dest = "mysql", default = False,
						help = "When get the output, also update mysqldb")
	parser.add_option("-v", "--verbose", action="store_true", dest = "verbose", default = False)
	return parser.parse_args()


def main():
	usage = '''
			python enhancedRRDTest.py [create|update|plot|dump] [options]
			Note: plotall has been replaced by 'plot -a'
			Example1:
				python enhancedRRDTest.py create -d test.rrd --step 250
				while doing the bwctl test:
					cat bwctloutput | python enhancedRRDTest.py update -d test.rrd
				python enhancedRRDTest.py plot -d test.rrd -t lastweek
			Example2: Dump from a mysqldb. (customized by conf.py)
				python enhancedRRDTest.py dump -p tcp
				python enhancedRRDTest.py plot -t lastday
				python enhancedRRDTest.py plot -a --start 1313000000 --end 1313130000
			'''
	
	p = OptionParser(usage=usage)
	(options, args) = _optParser(p)
	if len(args) == 0: 
		print 'try: python <scriptname> -h'
		sys.exit(1)
	v = options.verbose
	if args[0] == 'create': createTestRRDDb(options.dbname, options.step, conf._items)
	elif args[0] == 'update': 
	#	r = readFromSout()
		if options.all == True:
			for pairs in permutateHosts(conf._hosts):
				if options.protocol == 'tcp': bwc = conf._bwctcp
				else: bwc = conf._bwcudp
				bwcommand = bwc % pairs
				if v: print bwcommand
				output = os.popen(bwcommand)
				#output = open('test.perf')
				r = Record(output)
				if options.mysql == True: update_MySQL(r.d, conf._mysqlConf)
				rrdname = r.d['sender'].split('.')[0] + r.d['catcher'].split('.')[0]+options.protocol+'.rrd'
				update_RRD_1(rrdname, r.d, conf._items)
		else:
			r = readFromSout()
			if options.mysql == True: update_MySQL(r.d, conf._mysqlConf)
			update_RRD_1(options.dbname, r.d, conf._items)
	elif args[0] == 'plot' and options.all == False: 
		plotTestRRDDb(options.start, options.end, options.dbname, options.interval, conf._items)
	elif args[0] == 'plot' and options.all == True:
		for pairs in permutateHosts(conf._hosts):
			rrdname = pairs[0].split('.')[0] + pairs[1].split('.')[0]+options.protocol+'.rrd'
			plotTestRRDDb(options.start, options.end, rrdname, options.interval, conf._items)
#		os.popen('scp *.png huoc@student.cs.uni.edu:~/')
	elif args[0] == 'dump': 
		dumpFromMySQL(conf._items, options.step, options.protocol)
	else: print 'try: python <scriptname> -h'

if __name__ == '__main__':
	main()

