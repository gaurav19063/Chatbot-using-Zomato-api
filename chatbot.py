import zomapi
import urllib.parse
import requests

config={
  "user_key":"09b1203d9eb13e52fca606b0ce1d48a8"
}

zomato = zomapi.initialize_app(config)
ndots=30
print(ndots*'+'+"Welcome"+(ndots*'+'))
print('Enter yes if you want to find good food.')
user_input=input()
user_input='yes'
if(user_input.lower()!='yes'):
    print("Thank you for your time. Please reach out to us again.")
    exit()
# print("yes")
print('Now you are in the Search of best food, Please tell us your city.')
city_name=input()
# city_name='Bengaluru'
city_ID=zomato.get_city_ID(city_name)
# print(city_ID)
print("Enter your favourite cuisine:")
cuisine=input()
# cuisine='Biryani'

cuisine_id=zomato.get_cuisines_ID(cuisine,city_ID)
# print(cuisine_id)


address =city_name
url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) +'?format=json'

response = requests.get(url).json()
# print(response[0]["lat"])
# print(response[0]["lon"])
res_list=zomato.restaurant_search(cuisine,response[0]["lat"],response[0]["lon"])
# (self, query="", latitude="", longitude="", cuisines="", limit=5)
# print(res_list)
print("Here are some restaurants of you choice:\n")
for id in res_list:
    print(zomato.get_restaurant(id)['name'],)



print(ndots*'+'+"Thank you for your visit."+(ndots*'+'))
