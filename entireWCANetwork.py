from collections import defaultdict, deque
# from multiprocessing import Process, Value, Array
import concurrent.futures
import pickle
from time import time

# results = pd.read_csv("data/WCA_export_Results.tsv",delimiter='\t')
s = time()

with open("../../export_okt1_22/WCA_export_Results.tsv") as f:
    # results = (line.strip().split('\t') for line in f.readlines())

    d = set()
    f.readline()
    for val in f:
        val = val.strip().split('\t')
        if val[0] not in {'FMC2019','FMCAmericas2019','FMCAmericas2018','FMCAmericas2017','FMCEurope2019','FMCEurope2018','FMCEurope2017','FMCEurope2015','FMCEurope2016','FMCAsia2016','FMCAsia2015','FMCAsia2017','FMCAsia2018','FMCAsia2019','FewestMovesSoutheastAsia2018','FMCUSA2016','FMCUSA2015','FMCUSA2014'}:
            d.add((val[0],val[7]))
    print('loaded',time()-s)


graph = defaultdict(list)

for idx,val in enumerate(d):
    graph[f"c{val[0]}"].append(val[1])
    graph[val[1]].append(f"c{val[0]}")

counting_overview = {}

def bfs(id):
    q = deque()
    used = {}
    added = set()
    comps = set()
    # q.append(('2019AZZO01',0))
    q.append((id,0))
    c = 0
    while q:
        c +=1
        val,dist = q.popleft()
        if val not in used:
            used[val] = dist
            for item in graph[val]:
                if item not in comps:
                    comps.add(item)
                    for person in graph[item]:
                        if person not in added:
                            q.append((person,dist+1))
                            added.add(person)
                
    counting = defaultdict(int)

    for key,item in used.items():
        counting[item] += 1
    # counting_overview[id] = counting
    return counting 
    # return counting

# print(counting)

all_ids = [keys for keys in graph.keys() if keys[0] != 'c']
# print(all_ids[:1000])

s = time()
with concurrent.futures.ProcessPoolExecutor() as executor: # This takes like 4hours
    results = executor.map(bfs,all_ids[:100])
    for result,id in zip(results,all_ids[:100]):
        counting_overview[id] = result

print('done with ids', time()-s)
s = time()
Ff = open('many.pickle','wb')
pickle.dump(counting_overview,Ff)
print('dumped',time()-s)

