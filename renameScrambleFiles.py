##################
# CHANGE THIS ONLY
compid = 'RoskildebyNight2023'
dirr = 'RbN2023' # This is the relative path (on your local PC) to where you have unpacked the initial ZIP from tnoodle.
##################

import os
import zipfile
import string
import requests,json

alphabet = string.ascii_uppercase

event_name_map = {'222':'2x2x2','333':'3x3x3','444':'4x4x4','555':'5x5x5','666':'6x6x6','777':'7x7x7',
                  '333oh':'3x3x3 One-Handed','333bf':'3x3x3 Blindfolded','333fm':'3x3x3 Fewest Moves','333mbf':'3x3x3 Multiple Blindfolded',
                  'skewb':'Skewb', 'pyram':'Pyraminx','clock':'Clock','minx':'Megaminx','sq1':'Square-1','444bf':'4x4x4 Blindfolded','555bf':'5x5x5 Blindfolded'}

group_num_to_letter = {f'{i}': f'{alphabet[i-1]}' for i in range(1,len(alphabet)+1)}


fil = json.loads(requests.get(f"https://www.worldcubeassociation.org/api/v0/competitions/{compid}/wcif/public").content)
comp_name = fil['name']

sortedRounds = sorted([(activity['startTime'],activity['activityCode']) for activity in fil['schedule']['venues'][0]['rooms'][0]['activities'] if activity['activityCode'][0] != 'o'])
        
scrambleSetsPerRound = {round['id'] : round['scrambleSetCount'] for event in fil['events'] for round in event['rounds']}

def get_prepend_size(sortedRounds:list[tuple[str,str]], scrambleSetsPerRound:dict):
    count = 0
    for _,roundN in sortedRounds:
        esplit = roundN.split('-')
        if len(esplit) == 2:
            count += scrambleSetsPerRound[roundN]
        else:
            count += scrambleSetsPerRound["-".join(roundN.split('-')[:2])]
    return len(str(count))

def format_prepend(group:str,number:int,size:int):
    return "{:0{n}}_".format(number,n=size) + group

def get_file_name(event:str,round:str,attempt=None,group=None):
    filename = f'{event_name_map[event]} Round {round}'
    if group:
        filename += f" Scramble Set {group_num_to_letter[group]}"
    if attempt:
        filename += f" Attempt {attempt}"
    return filename+'.pdf'
    
def get_final_map(sortedRounds:list[tuple[str,str]], scrambleSetsPerRound:dict):
    finalmap = {}
    codes = parse_passcodes()
    codes_ordered = []
    o = get_prepend_size(sortedRounds,scrambleSetsPerRound)
    count = 0
    for _,e in sortedRounds:
        esplit = e.split('-')
        if len(esplit) == 2:
            groupSize = scrambleSetsPerRound[e]
            event,roundNum = esplit[0],esplit[1][1:]
            attempt = None
        else: # Assume only FM and MBLD possible
            groupSize = scrambleSetsPerRound["-".join(e.split('-')[:2])]
            event,roundNum,attempt = esplit[0],esplit[1][1:],esplit[2][1:]

        if groupSize > 1:
            for i in range(1,groupSize+1):
                filename = get_file_name(event,roundNum,attempt,str(i))
                finalmap[filename] = format_prepend(filename,count,o).replace(' ','_')
                code_dict_name = filename.split('.')[0]
                codes_ordered.append((code_dict_name,codes[code_dict_name]))
                count += 1
        else:
            filename = get_file_name(event,roundNum,attempt,None)
            code_dict_name = filename.split('.')[0]
            codes_ordered.append((code_dict_name,codes[code_dict_name]))
            finalmap[filename] = format_prepend(filename,count,o).replace(' ','_')
            count += 1
        
    return finalmap,codes_ordered

def parse_passcodes():
    c = 0
    codes = {}
    with open(passcodes) as f:
        
        for line in f:
            if c <= 8:
                c+=1 
                continue
            sett, code = tuple(line.strip().split(':'))
            codes[sett] = code
    return codes



passcodes = f'{dirr}/{comp_name} - Computer Display PDF Passcodes - SECRET.txt'
new_passcodes = f'{dirr}/{comp_name}PasscodesSorted.txt'
zip_file_name = f'{dirr}/{comp_name} - Computer Display PDFs.zip'
new_folder_name = f'{dirr}/{compid}SortedPdfs'

name_map,codes_ordered = get_final_map(sortedRounds,scrambleSetsPerRound)

with open(new_passcodes,'w') as f:
    for group,code in codes_ordered:
        f.write(f"{group}: {code}\n")

with zipfile.ZipFile(zip_file_name, "r") as zip_file:

    os.makedirs(new_folder_name, exist_ok=True)

    for zip_info in zip_file.infolist():
        old_file_name = zip_info.filename
        if old_file_name in name_map: # Dont accidentally lose a pdf
            new_file_name = name_map[old_file_name]
            file_contents = zip_file.read(old_file_name)

            with open(os.path.join(new_folder_name, new_file_name), "wb") as new_file:
                new_file.write(file_contents)

        else:
            print(f"Didnt find {old_file_name}")
            zip_file.extract(old_file_name, new_folder_name)
