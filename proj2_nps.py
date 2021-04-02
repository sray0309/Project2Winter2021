#################################
##### Name:    Rui Sun
##### Uniqname: rayss
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    BASE_URL = 'https://www.nps.gov'
    try:
        cache_file = open('index_cache.json', 'r')
        cache_file_contents = cache_file.read()
        state_dict = json.loads(cache_file_contents)
        cache_file.close()
        print('Using cache')
    except:
        response = requests.get(BASE_URL+'/index.htm')
        soup = BeautifulSoup(response.text, 'html.parser')
        drop_down_menu = soup.find('ul', class_='dropdown-menu SearchBar-keywordSearch')
        state_list_html = drop_down_menu.find_all('li')
        state_dict = {}
        for state in state_list_html:
            state_dict[state.text.lower()] = BASE_URL + state.find('a')['href']
        cache_file = open('index_cache.json', 'w')
        contents_to_write = json.dumps(state_dict)
        cache_file.write(contents_to_write)
        cache_file.close()
        print('Fetching')
    
    return state_dict
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    try:
        cache_file = open('site_cache.json', 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
    except:
        cache = {}
    if site_url in list(cache.keys()):
        print('Using cache')
        name = cache[site_url]['name']
        category = cache[site_url]['category']
        address = cache[site_url]['address']
        zipcode = cache[site_url]['zipcode']
        phone = cache[site_url]['phone']
    else:
        print('Fetching')
        response = requests.get(site_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        name = soup.find('a', class_='Hero-title').text.strip()
        category = soup.find('span', class_='Hero-designation').text.strip()
        address = soup.find('span', itemprop='addressLocality').text.strip() + ', ' + soup.find('span', itemprop='addressRegion').text.strip()
        zipcode = soup.find('span', itemprop='postalCode', class_='postal-code').text.strip()
        phone = soup.find('span', itemprop='telephone', class_='tel').text.strip()
        cache[site_url] = {
            'name': name,
            'category': category,
            'address': address,
            'zipcode': zipcode,
            'phone': phone
        }
        cache_file = open('site_cache.json', 'w')
        cache_file_contents = json.dumps(cache)
        cache_file.write(cache_file_contents)
        cache_file.close()
    site = NationalSite(category, name, address, zipcode, phone)

    return site


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    BASE_URL = 'https://www.nps.gov'
    try:
        cache_file = open('state_cache.json', 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
    except:
        cache = {}
    if (state_url in list(cache.keys())):
        print('Using cache')
        soup = BeautifulSoup(cache[state_url], 'html.parser')
    else:
        print('Fetching')
        response = requests.get(state_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cache[state_url] = response.text
        cache_file = open('state_cache.json', 'w')
        cache_file_contents = json.dumps(cache)
        cache_file.write(cache_file_contents)
        cache_file.close()
    site_url_list = soup.find('div', id='parkListResultsArea').find_all('h3')
    site_list = []
    for site_url in site_url_list:
        url = BASE_URL + site_url.find('a')['href']
        site_list.append(get_site_instance(url))

    return site_list
    


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    pass
    

if __name__ == "__main__":
    while(True):
        state_name = input('Enter a state name or exit:\n').lower()
        if (state_name == 'exit'):
            break
        else:
            state_list = build_state_url_dict()
            site_list = get_sites_for_state(state_list[state_name])
            print('-' * (30+len(state_name)))
            print(f'| list of national sites in {state_name} |')
            print('-' * (30+len(state_name)))
            for i in range(len(site_list)):
                print(f'[{i+1}] {site_list[i].info()}')
    