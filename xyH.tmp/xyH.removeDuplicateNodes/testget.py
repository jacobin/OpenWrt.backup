import sys
import getopt

#Remove the file name from the commandline arguments
argumentList = sys.argv[1:]
short_options ="h:m:o:"
long_options = ["Help=", "My_file=","Output="]
#Parsing arguments -extract meaningful information from command line arguments
try:
	arguments, values=getopt.getopt(argumentList, short_options, long_options)
except getopt.error as err:
	print(str(err))
	sys.exit(2)
		
print('arguments:', arguments)
print('values:',values)
for currentArgument,currentValue in arguments:
	print('currentArgument:',currentArgument)
	print('currentValue:',currentValue)
	if currentArgument in ("-h", "--Help"):
		print('Help message')
	
	elif currentArgument in ("-m", "--My_file"):
		print('File name:',sys.argv[0])
		
	elif currentArgument in ("-o","--Output"):
		print('Showing output:',currentValue)