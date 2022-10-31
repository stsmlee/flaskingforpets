from app.pet_helper.sneaky import secret_dict
# from asyncore import write
import requests
import json

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

types_dict = update_types()
# update_all_types_breeds()
# json_obj = json.dumps(types_dict, indent = 4)
# with open('types.json', 'w') as outfile:
#     outfile.write(json_obj)
# pet_types_dict = get_types_dict()

base_url = 'https://api.petfinder.com'
animals_url = 'https://api.petfinder.com/v2/animals'


def get_request(payload):
    res = requests.get(animals_url, headers = header, params = payload)
    res_json = res.json()
    pagination = res_json['pagination']   
    total_hits = pagination['total_count']
    if total_hits <= 0:
        return None
    return res_json

null = None
false = False
true = True

def parse_res_animals(res_animals):
    parsed_list = []
    for pet in res_animals:
        current = {}
        current['ID'] = pet['id']
        current['Organization ID'] = pet['organization_id']
        current['Name'] = pet['name']
        current['Profile Link'] = pet['url']
        current['Species'] = pet['species']        
        breeds = []
        for attr,br in pet['breeds'].items():
            if attr == 'mixed' and br:
                breeds.append('Mixed Breed')
            elif br:
                breeds.append(br)
        current['Breed(s)'] = ', '.join(breeds)
        colors = []
        for color in pet['colors'].values():
            if color:
                colors.append(color)
        current['Colors'] = ', '.join(colors)
        current['Age'] = pet['age']
        current['Size'] = pet['size']
        current['Coat'] = pet['coat']
        additional_attr = []
        for attr, val in pet['attributes'].items():
            if val:
                additional_attr.append(' '.join(attr.split('_')).title())
        current['Attributes'] = ', '.join(additional_attr)
        enviro = []
        for attr, val in pet['environment'].items():
            if val:
                enviro.append(attr.title())
        current['Environment, Good with'] = ', '.join(enviro)
        current['Tags'] = ', '.join(pet['tags'])
        current['Description'] = pet['description']
        if pet['organization_animal_id']:
            current['Organization Animal ID'] = pet['organization_animal_id']
        photo_links = []
        for entry in pet['photos']:
            for key, val in entry.items():
                if key == 'medium':
                    photo_links.append(val)
        current['Photos'] = photo_links
        current['Status'] = pet['status'].title()
        current['Published at'] = pet['published_at'][:10]
        current['Distance'] = pet['distance']
        contact_info = {}
        for key, val in pet['contact'].items():
            if key != 'address' and val:
                contact_info[key.title()] = val
            elif val:
                # contact_info['Address'] = {}
                contact_info = ""
                for k,v in val.items():
                    if v:
                        if k == 'address1' or k == 'address2' or k == 'city':
                            contact_info += v + ', '
                        if k == 'state':
                            contact_info += v 
                        if k == 'postcode':
                            contact_info += ' ' + v                            
                        if k == 'country':
                            contact_info += ', ' + v                            
        current['Contact Info'] = contact_info
        clean_cur = {k: v for k, v in current.items() if v}
        parsed_list.append(clean_cur)
    return parsed_list

def parse_res_pag(res_pag):
    pag = {}
    pag['Results per page'] = res_pag['count_per_page']
    pag['Total number of results'] = res_pag['total_count']
    pag['Current page'] = res_pag['current_page']
    pag['Total pages'] = res_pag['total_pages']
    if '_links' in res_pag.keys():
        if 'previous' in res_pag['_links'].keys():
            pag['Previous'] = True
        else: 
            pag['Previous'] = False
        if 'next' in res_pag['_links'].keys():
            pag['Next'] = True
        else:
            pag['Next'] = False
    return pag

def build_params(my_data, type):
    payload = {'type':type, 'location' : my_data['zipcode'], 'distance' : my_data['distance'], 'limit':10}
    if my_data['breed1'] != 'N/A':
        payload['breed'] = my_data['breed1']
    if my_data['breed2'] != 'N/A':
        payload['breed'] += ',' + my_data['breed2']
    if my_data['color'] != 'N/A':
        payload['color'] = my_data['color']
    if my_data['coat'] != 'N/A':
        payload['coat'] = my_data['coat']
    if my_data['gender'] != 'N/A':
        payload['gender'] = my_data['gender']
    # if my_data['age']:
    #     payload['age'] = ','.join(my_data['age'])
    age = []
    if my_data['baby']:
        age.append('baby')
    if my_data['young']:
        age.append('young')
    if my_data['adult']:
        age.append('adult')
    if my_data['senior']:
        age.append('senior')
    if age:
        payload['age'] = ','.join(age)
    # if my_data['size']:
    #     payload['size'] = ','.join(my_data['size'])
    size = []
    if my_data['small']:
        size.append('small')
    if my_data['medium']:
        size.append('medium')
    if my_data['large']:
        size.append('large')
    if my_data['xlarge']:
        size.append('xlarge')
    if size:
        payload['size'] = ','.join(size)
    if my_data['children']:
        payload['good_with_children'] = 1
    if my_data['dogs']:
        payload['good_with_dogs'] = 1
    if my_data['cats']:
        payload['good_with_cats'] = 1
    return payload