from geopy.geocoders import Nominatim
geolocator = Nominatim()
location = geolocator.geocode("North America - Above The Wall")
print((location.latitude, location.longitude))