#This list maintains the data entries that you will create in the new rrd dbs
_items = ['value']

_color = ['FF0000', '00FF00', '0000FF', 'FF0055', '5500FF']
_d = {
		'lasthour': '-3600',
		'last12hours': '-43200',
		'lastday': '-86400',
		'last3days': '-259200',
		'lastweek' : '-604800',
		'lastmonth': '-2419200',
		'last3months': '-7257600'
	}

_mysqlConf = ('localhost','root', 'temp@123', 'perfsonar_ma')
_table = 'clmp_bwctl'
_hosts = ['itt128.perfsonar.uni.edu', 'perfsonar.its-ns.uni.edu', 'srl006.perfsonar.uni.edu', 'sec119.perfsonar.uni.edu','cbb019.perfsonar.uni.edu', 'dan123.perfsonar.uni.edu']
_bwctcp = 'bwctl -s %s -c %s'
_bwcudp = 'bwctl -u -s %s -c %s'
