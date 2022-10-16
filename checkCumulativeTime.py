import json
from collections import defaultdict
import webbrowser
import requests
import os

def genToken():
	# alternatively remove the .get part if the browser is causing you an issue, or just open the url yourself and save the code to a file
	webbrowser.get("x-www-browser").open("https://www.worldcubeassociation.org/oauth/authorize?client_id=5U1L9es8uMLPEPM_qbQuWWOqIY8NJiXcWC_4V1sLLgw&redirect_uri=urn%3Aietf%3Awg%3Aoauth%3A2.0%3Aoob&response_type=token&scope=manage_competitions+public",new=0)
	token = input("A browser should open. Copy the token from the URL and paste it here")
	return token

def getWcif(id):
	if not os.path.exists("authcode"):
		token = genToken()
		with open('authcode','w') as f:
			print(token,file=f)
	else:
		with open('authcode','r') as f:
			token = f.readline().strip('\n')
	header = {'Authorization':f"Bearer {token}"}
	
	wcif = requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{id}/wcif",headers=header)
	assert wcif.status_code == 200
	return wcif,header


# data = json.loads(get_wcif('HDCIIHvidovre2022').content)
response,header = getWcif('HDCIIHvidovre2022')
data = json.loads(response.content)

c = defaultdict(int)
dnfcounter = defaultdict(int)

for val in data["events"]:
    for val2 in val['rounds']:
        for val3 in val2['results']:
            for val4 in val3['attempts']:

                if val4['result'] > 0:
                    c[val3['personId']] +=val4['result']
                elif val4['result'] == -1:
                    dnfcounter[val3['personId']] += 1

translater = {}

for val in data['persons']:
    translater[val['registrantId']] = val['name']


def convert(seconds):
    seconds = seconds/100
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
      
    return "%d:%02d:%02d" % (hour, minutes, seconds)


overview = [(name,value) for name,value in c.items()]


which = 1 # 0 is by time, 1 is by name

if which == 0:
    overview.sort(key=lambda x:x[1], reverse=True)
elif which == 1:
    overview.sort(key=lambda x:translater[x[0]], reverse=False)

# for person in c:
#     print(translater[person],convert(c[person]),dnfcounter[person])

for val in overview:
    print(f"{translater[val[0]][:15]}\tTime used: {convert(c[val[0]])}\tDNFs: {dnfcounter[val[0]]}")
