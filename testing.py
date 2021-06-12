import os

'''
s ={'form count' : 1,
        1 : 'ddfdf',
        'ddfdf' : 
                { 
                'question count' : 3, 
                'question iterator' : 0, 
                 0 : "actual qn "
                 }
            }


form = 'ddfdf'
form_count = s[0]['form count']

s[0][s[0]['form count']][form]['question iterator'] = "question created"


for i in range(1,10):
        with open("userid.txt", "a") as f:
                f.write(str(i) + "\n")


out = os.popen("grep -o '11' userid.txt").read()

if out == "":
        print(out)

else:
        print("failed")
'''

import json
'''
with open("sample.json", "r") as f:
    data = json.load(f)

for i in range(data['576048895_1']['questions count']):
        print(data['576048895_1'][str(i)])
'''

with open("sample.json", "r") as f:
    data = json.load(f)
    data["1"]["2"].append(23)
    with open("sample.json", "w") as f1:
        json.dump(data, f1)

