import datetime as dt


def getDatefromDate(date,delta,strfmt='%Y%m%d'):
	if type(date)==str:
		date=stringToDate(date,strfmt)
	return (date + dt.timedelta(delta)).strftime(strfmt)

def getDateFromToday(delta,strfmt='%Y%m%d'):
	""" Returns a string that represents a date n numbers of days from today.
	Parameters:
	-----------
		delta : int 
			number of days
		strfmt : string
			format in which the date will be represented
	"""
	return (dt.date.today() + dt.timedelta(delta)).strftime(strfmt)

def stringToDate(stringDate,strfmt='%Y%m%d'):
	""" Converts a string format date into datetime
	Parameters:
	-----------
		stringDate : string 
			date in string format
		strfmt : string
			format in which the input date is represented
	"""
	return dt.datetime.strptime(stringDate,strfmt).date()

def intToDate(intDate):
	""" Converts an int format date into datetime
	Parameters:
	-----------
		intDate : int
			date in int format
	Example:
		intDate(20151023)
	"""
	return stringToDate(str(intDate))

def dateToInt(date,strfmt='%Y%m%d'):
	""" Converts a datetime date into int
	Parameters:
	-----------
		date : datetime
			date in datetime format
		strfmt : string
			format in which the int date will be generated
	Example:
		dateToInt(dt.date(2015,10,23),'%Y')
	"""
	return int(date.strftime(strfmt))

def dateToString(date,strfmt='%Y%m%d'):
	return dt.datetime.strftime(date,strfmt)

def stringToString(date,from_strfmt='%d%b%y',to_strfmt='%Y%m%d'):
	return dt.datetime.strftime(stringToDate(date,from_strfmt),to_strfmt)


	