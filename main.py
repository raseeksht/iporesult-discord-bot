import requests

import json,os,threading,time
from prettytable import PrettyTable


table = PrettyTable()
table.field_names = ['id','name','status']

url = "https://iporesult.cdsc.com.np/result/result/check"
companies = "https://iporesult.cdsc.com.np/result/companyShares/fileUploaded"


shareNo = ""

# clear only works for linux mac and termux


# con = open('boid.json','r').read()
# boids = json.loads(str(con))

colors  =  {
	"red":"\u001b[31m",
	'reset':'\u001b[0m',
	'green':'\u001b[32m',
	'yellow':'\u001b[33m',
	'blue':'\u001b[34m',
	'magenta':'\u001b[35m',
	'cyan':'\u001b[36m',
	'white':'\u001b[37m'
}



headers = {"Content-Type" : "application/json"}


results = {}
# list 'names' will contain names of the user
# and the message/result data is stored with name of the user as key
# and corresponding msg as the value *
# loop through the list names as name and access the message using results[name]
def req(client,data,boid):
	req = client.post(url,data=data,headers=headers)
	if (req.status_code == 200):
		message = req.json()['message']
	else:
		message = "Not Yet Published in iporesult"
	results[boid[1]] = {
		"color":colors['green'] if "Congratulation" in message else colors['red'],
		"message":message,
		"isAlloted":f"{colors['green']}Alloted{colors['reset']}" if "Congratulation" in message else f"{colors['red']}Not Alloted{colors['reset']}"
	}


	
	


def withThreading(client,boids):
	threads = []
	names = [] # for showing in the same order as in boid.json file
	init = time.time()
	for boid in boids:
		data = '{"boid":"'+boid[0]+'","companyShareId":"'+shareNo+'"}'
		# format of boid = ["1301170001048665","raseek"] | type-> list
		names.append(boid[1])
		t = threading.Thread(target=req,args=(client,data,boid))
		threads.append(t)

	
	for i in range(len(boids)):
		threads[i].start()
	for i in range(len(boids)):
		threads[i].join()

	timeTaken = time.time()-init
	for index,name in enumerate(names):
		table.add_row([index+1,name,results[name]['isAlloted']])





	

	


