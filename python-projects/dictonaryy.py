'''
Create a dictionary that would ask for an input for any word and defines it
'''
import json
from difflib import get_close_matches

data = json.load(open('/Users/rohiththakur/Documents/projects/python-projects/data.json')) #load the data into python dictionary

dic_words = list(data.keys()) #sorted keys into a list 

def translate(w):
    w = w.lower() #make it case sensitive
    if w in data:
        return data[w]
    elif w.title() in data:
        return data[w.title()]
    elif w.upper() in data:
        return data[w.upper()]
    elif len(get_close_matches(w, dic_words))>0: #close match for a word entered
        yn = input("Did you mean %s ? Enter Y if Yes or N if No: " %get_close_matches(w, dic_words)[0])
        if yn == 'Y':
            return (get_close_matches(w, dic_words)[0])
        elif yn == 'N':
            return "Word doesn't exist. Please try again"
        else:
            return ('Sorry, please try again')
    else:
        return "Word doesn't exist. Please try again"

word = input("Enter a word: ")

output = translate(word)

if type(output) == list:
    for item in output:
        print(item)
else:
    print(output)