import configparser
import click
import requests
import pprint
import re
import time

@click.command()
@click.option('--config','-c', default="auth.conf", help='Configuration file with authorization tokens.')
@click.option('--repository','-r', default='MI-PYT-TestRepo',help='Target repository which going to be processed.')
@click.option('--rules','-f',default='rules.conf',help='File with rules.')
@click.option('--rate','-x',default=60,help="How long to wait to another run (in seconds).")
@click.option('--default','-d',default="default",help="Default label if none of rules will match.")
@click.option('--comments','-k',is_flag="True",help="Controls if you also search in comments.")

def run(config,repository,rules,rate,default,comments):
	print("Config: "+config+", repository: "+repository+", file with rules: "+rules+", rate: "+str(rate)+", default label:"+default+", process comments flag: "+str(comments))
	token,username=readConfig(config)
	session=createSession(token)
	
	while True:
		print("Checking issues...")
		labelIssues(session,repository,username,rules,default,comments)
		time.sleep(rate)
	



def readConfig(config):
	tokenConfig = configparser.ConfigParser()
	tokenConfig.read(config)
	#TODO osetrit neexistujici konfig
	token=tokenConfig["github"]["token"]
	username=tokenConfig["github"]["username"]
	#TODO osetrit neexistujici direktivy
	return token,username
	
def readRules(rules):
	with open(rules) as f:
		content = f.readlines()
	return content


def createSession(token):
	session=requests.Session()
	session.headers={'Authorization': 'token ' + token, 'User-Agent': 'Python'}
	return session
	
def labelIssues(session,repository,username,rules,default,comments):

	#get all issues of specified repository
	query = "https://api.github.com/repos/"+username+"/"+repository+"/issues"
	r = session.get(query)
	
	#TODO osetrit chyby
	
	#read all rules
	content=readRules(rules)
	
	for issue in r.json():	
		
		#issue doesnt have a label
		if not issue["labels"]:
			
			#for each rule
			matched=False
			for line in content:
				line=line.strip()
				if line.startswith("#") or line == "":
					continue
					
				#parse rule and label with color
				rule,labelAndColor = line.split("=")
				rule = rule.strip()
				label,color = labelAndColor.split(",")
				label=label.strip()
				color=color.strip()
				
				#prepare regex
				pattern = re.compile(rule)
				
				#test body of issue if matches regex
				if pattern.search(issue["body"]):
					print("Match!")
					matched=True
					
					#check if label with this name exists
					if not getLabel(session,repository,username,label):
						#if label doesnt exist, create it
						print("Creating new label...")
						createLabel(session,repository,username,label,color)
					else:
						print("Label "+label+" already exists...")
					#add label to issue	
					print("Adding label: "+label+" to issue: "+issue["title"])
					addLabel(session,repository,username,label,issue["number"])
						
				else:
					print("No match.")
			
			#if no rule matched this issue, we add default label
			if not matched:
				#check if default label already exists
				if not getLabel(session,repository,username,label):
					#if default label doesnt exists, create it
					createLabel(session,repository,username,default,"7a7a7a")
				#add default label
				addLabel(session,repository,username,default,issue["number"])
	
def getLabel(session,repository,username,name):
	query="https://api.github.com/repos/"+username+"/"+repository+"/labels/"+name
	r=session.get(query)
	if r.status_code == 404:
		return False
	else:
		return True		

def createLabel(session,repository,username,label,color):
	query="https://api.github.com/repos/"+username+"/"+repository+"/labels"
	print("creating label: "+label+" with color: "+color)
	session.post(query,data='{"name": "'+label+'", "color": "'+color+'"}')
	#TODO navratovy kod
	
def addLabel(session,repository,username,label,number):
	query="https://api.github.com/repos/"+username+"/"+repository+"/issues/"+str(number)+"/labels"
	session.post(query,data='["'+label+'"]')
	#TODO navratovy kod
	
	
	

if __name__ == '__main__':
	run()
	
