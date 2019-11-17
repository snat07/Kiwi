from requests_html import HTMLSession
from datetime import datetime, timedelta
from redis import StrictRedis
from slugify import slugify
import requests
import pickle
import pprint

class connections():

    def __init__(self):
        self.default_ttl = 1800
        self.redis = StrictRedis(**{'host': '34.77.218.145','port': 80})
        self.cities = None

    def get_data(self, source, destination, date_departure):
        #TODO Add date validation
        cached_results = self.redis.get(self.trip_key_caching(source,destination,date_departure))
        if cached_results is not None:
            return pickle.loads(cached_results)

        source_id = self.find_city_id(source)
        destination_id = self.find_city_id(destination)
        if source_id == -1 or destination_id == -1:
            raise ValueError("Incorrect city")

        session = HTMLSession()
        response = session.get(f'https://shop.global.flixbus.com/search?departureCity={source_id}&arrivalCity={destination_id}rideDate={date_departure}')
        content = response.html.find('div.ride-available')
        
        result = []
        for element in content:
            result.append(self.parse_element(element,date_departure))

        self.redis.setex(self.trip_key_caching(source,destination,date_departure),self.default_ttl,pickle.dumps(result))
        return result
        
    def parse_element(self, element, date_departure):
        date = date_departure + ' ' + element.find('div.departure')[0].text + ':00'
        departure_date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
        duration = self.get_duration(element.find('span.duration')[0].text)
        arrival_date = departure_date + timedelta(hours=duration[0],minutes=duration[1])
         
        price = 'N/A'
        if len(element.find('span.num.currency-small-cents')) > 0:
            price = element.find('span.num.currency-small-cents')[0].text.split()
        #TODO Add price conversor logic in case it is not Euros
        #if price[1] != '€':
            
        return {
            'departure': str(departure_date),
            'return': str(arrival_date),
            'from': element.find('div.departure-station-name')[0].text,
            'to': element.find('div.arrival-station-name')[0].text,
            'price': float(price[0]) if type(price) == list else price
        }

    def get_duration(self, duration_str):
        duration_str = duration_str.replace('(','')
        duration_str = duration_str.replace(' Hrs.)','')
        hours_minutes = duration_str[0:5].split(':')
        return (int(hours_minutes[0]),int(hours_minutes[1]) if len(hours_minutes) > 1 else 0)


    def get_cities(self):
        r = requests.get('https://d11mb9zho2u7hy.cloudfront.net/api/v1/cities?locale=en')
        self.cities = r.json()['cities']
    
    def find_city_id(self, city):
        cached_city = self.redis.get(self.city_key_caching(city))
        if cached_city is not None:
            return pickle.loads(cached_city)

        if self.cities is None:
            self.get_cities()
        
        city_id = -1
        for key in self.cities:
            if self.cities[key]['name'] == city:
                city_id = key
                break
        self.redis.setex(self.city_key_caching(city),self.default_ttl, pickle.dumps(city_id))

        return city_id

    def city_key_caching(self, city):
        return f'bcn_SN_location:{slugify(city)}_flixbus'
    
    def trip_key_caching(self, departure_city, arrival_city, departure_date):
        return f'bcn_SN_journey:{slugify(departure_city)}_{slugify(arrival_city)}_{departure_city}_flixbus'


if __name__ == "__main__":
    connections = connections()
    print(10*'--')
    pprint.pprint(connections.get_data('Pa','Paris','2019-11-20'))
    print(10*'--')
    pprint.pprint(connections.get_data('Berlin','Brussels','2019-11-20'))
    print(10*'--')
    pprint.pprint(connections.get_data('Berlin','Munich','2019-11-20'))
