import requests
import ast
import json

base_url = "https://developers.zomato.com/api/v2.1/"


def initialize_app(config):
    return Zomato(config)


class Zomato:
    def __init__(self, config):
        self.user_key = config["user_key"]

    def get_city_ID(self, city_name):
        """
        Takes City Name as input.
        Returns the ID for the city given as input.
        """
        # print("check1")
        if city_name.isalpha() == False:
            raise ValueError('InvalidCityName')
        # print("check2")
        city_name = city_name.split(' ')
        city_name = '%20'.join(city_name)
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "cities?q=" + city_name, headers=headers).content).decode("utf-8")
        # print(r)
        # print("check3")
        a = json.loads(r)
        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        if len(a['location_suggestions']) == 0:
            raise Exception('invalid_city_name')
        elif 'name' in a['location_suggestions'][0]:
            city_name = city_name.replace('%20', ' ')
            # print(city_name)
            return a['location_suggestions'][0]['id']

    def get_categories(self):
        """
        Takes no input.
        Returns a dictionary of IDs and their respective category names.
        """
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "categories", headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        categories = {}
        for category in a['categories']:
            categories.update({category['categories']['id'] : category['categories']['name']})

        return categories
    def get_cuisines(self, city_ID):
        """
        Takes City ID as input.
        Returns a sorted dictionary of all cuisine IDs and their respective cuisine names.
        """
        self.is_valid_city_id(city_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "cuisines?city_id=" + str(city_ID), headers=headers).content).decode("utf-8")
        a = ast.literal_eval(r)

        self.is_key_invalid(a)
        self.is_rate_exceeded(a)

        if len(a['cuisines']) == 0:
            raise ValueError('InvalidCityId')
        temp_cuisines = {}
        cuisines = {}
        for cuisine in a['cuisines']:
            temp_cuisines.update({cuisine['cuisine']['cuisine_id'] : cuisine['cuisine']['cuisine_name']})

        for cuisine in sorted(temp_cuisines):
            cuisines.update({cuisine : temp_cuisines[cuisine]})

        return cuisines


    def get_cuisines_ID(self,name,city_ID):

        cus=self.get_cuisines(city_ID)
        for id,cus_name in cus.items():
            if name.lower() == cus_name.lower() :
                    # print(id)
                    return id
        raise ValueError('InvalidCusineName')
    def restaurant_search(self, query="", latitude="", longitude="", cuisines="", limit=10):
        """
        Takes either query, latitude and longitude or cuisine as input.
        Returns a list of Restaurant IDs.
        """
        cuisines = "%2C".join(cuisines.split(","))
        if str(limit).isalpha() == True:
            raise ValueError('LimitNotInteger')
        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "search?q=" + str(query) + "&count=" + str(limit) + "&lat=" + str(latitude) + "&lon=" + str(longitude) + "&cuisines=" + str(cuisines), headers=headers).content).decode("utf-8")
        a = json.loads(r)

        restaurants = []

        if a['results_found'] == 0:
            return []
        else:
            for restaurant in a['restaurants']:
                restaurants.append(restaurant['restaurant']['id'])

        return restaurants
    def get_restaurant(self, restaurant_ID):
        """
        Takes Restaurant ID as input.
        Returns a dictionary of restaurant details.
        """
        self.is_valid_restaurant_id(restaurant_ID)

        headers = {'Accept': 'application/json', 'user-key': self.user_key}
        r = (requests.get(base_url + "restaurant?res_id=" + str(restaurant_ID), headers=headers).content).decode("utf-8")
        a = json.loads(r)

        if 'code' in a:
            if a['code'] == 404:
                raise('InvalidRestaurantId')

        restaurant_details = {}
        restaurant_details.update({"name" : a['name']})
        restaurant_details.update({"url" : a['url']})
        restaurant_details.update({"location" : a['location']['address']})
        restaurant_details.update({"city" : a['location']['city']})
        restaurant_details.update({"city_ID" : a['location']['city_id']})
        restaurant_details.update({"user_rating" : a['user_rating']['aggregate_rating']})

        restaurant_details = DotDict(restaurant_details)
        return restaurant_details




    def is_valid_restaurant_id(self, restaurant_ID):
        """
        Checks if the Restaurant ID is valid or invalid.
        If invalid, throws a InvalidRestaurantId Exception.
        """
        restaurant_ID = str(restaurant_ID)
        if restaurant_ID.isnumeric() == False:
            raise ValueError('InvalidRestaurantId')



    def is_valid_city_id(self, city_ID):
        """
        Checks if the City ID is valid or invalid.
        If invalid, throws a InvalidCityId Exception.
        """
        city_ID = str(city_ID)
        if city_ID.isnumeric() == False:
            raise ValueError('InvalidCityId')



    def is_key_invalid(self, a):
        """
        Checks if the API key provided is valid or invalid.
        If invalid, throws a InvalidKey Exception.
        """
        if 'code' in a:
            if a['code'] == 403:
                raise ValueError('InvalidKey')



    def is_rate_exceeded(self, a):
        """
        Checks if the request limit for the API key is exceeded or not.
        If exceeded, throws a ApiLimitExceeded Exception.
        """
        if 'code' in a:
            if a['code'] == 440:
                raise Exception('ApiLimitExceeded')
class DotDict(dict):
    """
    Dot notation access to dictionary attributes
    """

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
