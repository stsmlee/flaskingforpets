from app.pet_helper.sneaky import secret_dict
from asyncore import write
import requests
import json
# import copy

def get_types_dict():
    with open('types.json', 'r') as openfile:
        json_obj = json.load(openfile)
    return json_obj

def get_token():
    client_id = secret_dict['client_id']
    client_secret = secret_dict['client_secret']

    url = 'https://api.petfinder.com/v2/oauth2/token'
    params = {
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "client_id": client_id
    }
    response = requests.post(url, data=params)
    # print(response)
    # print(response.text)
    return response.json()['access_token']

token = get_token()
# print(token)
auth = "Bearer " + token
header = {"Authorization": auth}

def update_types():
    type_url = 'https://api.petfinder.com/v2/types'
    res = requests.get(type_url, headers=header)
    # print(res)
    # return res.json()
    types_json= res.json()
    types_dict = {}
    for i in range(len(types_json['types'])):
        cur = types_json['types'][i]
        types_dict[cur['name']] = {'Colors' : types_json['types'][i]['colors']}
        types_dict[cur['name']]['Coats'] = types_json['types'][i]['coats']
    return types_dict

def get_breeds(type):
    breeds_url = 'https://api.petfinder.com/v2/types/'+ type + '/breeds'
    res = requests.get(breeds_url, headers=header)
    breeds_json = res.json()
    breeds = []
    for i in range(len(breeds_json['breeds'])):
        breeds.append(breeds_json['breeds'][i]['name'])
    types_dict[type]['Breeds'] = breeds

def update_all_types_breeds():
    for key in types_dict.keys():
        get_breeds(key)        

types_dict = get_types_dict()

# types_dict = update_types()
# update_all_types_breeds()
# json_obj = json.dumps(types_dict, indent = 4)
# with open('types.json', 'w') as outfile:
#     outfile.write(json_obj)

