import csv

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

with open("form_table.csv",mode= "w") as f:

        csv_writer = csv.writer(f, delimiter = ",")

        csv_writer.writerow([])

