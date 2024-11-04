import zmq
import pickle 


continents = {
    'North America': ["Alaska", "Alberta", "Central America", "Eastern United States", "Greenland", "Northwest Territory", "Ontario", "Quebec", "Western United States"],
    'South America': ['Argentina', 'Brazil', 'Peru', 'Venezuela'], 
    'Europe': ['Great Britain', 'Iceland', 'Northern Europe', 'Scandinavia', 'Southern Europe', 'Ukraine', 'Western Europe'],
    'Africa': ['Congo', 'East Africa', 'Egypt', 'Madagascar', 'North Africa', 'South Africa'], 
    'Asia': ['Afghanistan', 'China', 'India', 'Irkutsk', 'Japan', 'Kamchatka', 'Middle East', 'Mongolia', 'Siam', 'Siberia', 'Ural', 'Yakutsk'],
    'Australia': ['Eastern Australia', 'Indonesia', 'New Guinea', 'Western Australia']
    }


country_coords = {
    'Alaska': (49, 161), 
    'Alberta': (190, 237), 
    'Central America': (244, 439), 
    'Eastern United States': (297, 308), 
    'Greenland': (453, 111), 
    'Northwest Territory': (215, 149), 
    'Ontario': (266, 207), 
    'Quebec': (351, 253), 
    'Western United States': (185, 335), 
    'Argentina': (333, 770), 
    'Brazil': (415, 633), 
    'Peru': (250, 574), 
    'Venezuela': (321, 492), 
    'Great Britain': (557, 303), 
    'Iceland': (560, 190), 
    'Northern Europe': (674, 273), 
    'Scandinavia': (656, 181), 
    'Southern Europe': (699, 402), 
    'Ukraine': (777, 264), 
    'Western Europe': (572, 443), 
    'Congo': (735, 713), 
    'East Africa': (811, 675), 
    'Egypt': (760, 538), 
    'Madagascar': (850, 796), 
    'North Africa': (609, 544), 
    'South Africa': (727, 848), 
    'Afghanistan': (910, 363), 
    'China': (1106, 434), 
    'India': (996, 502), 
    'Irkutsk': (1077, 245), 
    'Japan': (1237, 349), 
    'Kamchatka': (1204, 129), 
    'Middle East': (820, 489), 
    'Mongolia': (1113, 336), 
    'Siam': (1123, 534), 
    'Siberia': (1014, 172), 
    'Ural': (927, 178), 
    'Yakutsk': (1100, 128), 
    'Eastern Australia': (1300, 810), 
    'Indonesia': (1123, 699), 
    'New Guinea': (1197, 610), 
    'Western Australia': (1170, 768)
    }

country_neighbors = {
    "Alaska": ["Northwest Territory", "Alberta", "Kamchatka"],
    "Alberta": ["Alaska", "Northwest Territory", "Ontario"],
    "Central America": ["Western United States", "Eastern United States", "Venezuela"],
    "Eastern United States": ["Central America", "Western United States", "Ontario", "Quebec"],
    "Greenland": ["Alaska", "Northwest Territory", "Ontario", "Iceland"],
    "Northwest Territory": ["Alaska", "Alberta", "Ontario", "Greenland", "Kamchatka"],
    "Ontario": ["Alberta", "Eastern United States", "Northwest Territory", "Quebec"],
    "Quebec": ["Ontario", "Eastern United States", "Greenland"],
    "Western United States": ["Alaska", "Central America", "Eastern United States"],
    
    "Argentina": ["Brazil", "Peru", "Venezuela"],
    "Brazil": ["Argentina", "Peru", "Venezuela", "North Africa"],
    "Peru": ["Argentina", "Brazil", "Venezuela", "North Africa"],
    "Venezuela": ["Argentina", "Brazil", "Central America", "North Africa"],
    
    "Great Britain": ["Iceland", "Northern Europe", "Western Europe"],
    "Iceland": ["Greenland", "Great Britain", "Northern Europe"],
    "Northern Europe": ["Great Britain", "Iceland", "Scandinavia", "Southern Europe", "Western Europe"],
    "Scandinavia": ["Northern Europe", "Southern Europe", "Ural"],
    "Southern Europe": ["Northern Europe", "Scandinavia", "Ukraine", "Western Europe", "Egypt"],
    "Ukraine": ["Northern Europe", "Southern Europe", "Ural", "Middle East"],
    "Western Europe": ["Great Britain", "Northern Europe", "Southern Europe", "North Africa"],
    
    "Congo": ["East Africa", "North Africa"],
    "East Africa": ["Congo", "North Africa", "Madagascar", "South Africa"],
    "Egypt": ["North Africa", "East Africa", "Southern Europe"],
    "Madagascar": ["East Africa", "South Africa"],
    "North Africa": ["Congo", "East Africa", "Egypt", "Brazil", "Western Europe"],
    "South Africa": ["East Africa", "Madagascar"],
    
    "Afghanistan": ["China", "India", "Middle East", "Ural"],
    "China": ["Mongolia", "India", "Siberia", "Kamchatka", "Afghanistan"],
    "India": ["China", "Afghanistan", "Middle East"],
    "Irkutsk": ["Siberia", "Kamchatka"],
    "Japan": ["Kamchatka"],
    "Kamchatka": ["Alaska", "Irkutsk", "China", "Mongolia"],
    "Middle East": ["Afghanistan", "India", "Ukraine", "Egypt"],
    "Mongolia": ["Siberia", "China", "Kamchatka"],
    "Siam": ["India", "China"],
    "Siberia": ["Irkutsk", "Ural", "China", "Mongolia"],
    "Ural": ["Scandinavia", "Northern Europe", "Ukraine", "Siberia", "Afghanistan"],
    "Yakutsk": ["Kamchatka", "Siberia"],
    
    "Eastern Australia": ["Western Australia", "Indonesia"],
    "Indonesia": ["Eastern Australia", "Western Australia"],
    "New Guinea": ["Eastern Australia"],
    "Western Australia": ["Eastern Australia", "Indonesia"],
    }

deck = {
    'Alaska': 'Infantry',
    'Northwest Territory': 'Cavalry',
    'Greenland': 'Artillery',
    'Alberta': 'Infantry',
    'Ontario': 'Cavalry',
    'Quebec': 'Artillery',
    'Western United States': 'Infantry',
    'Eastern United States': 'Cavalry',
    'Central America': 'Artillery',
    'Venezuela': 'Infantry',
    'Peru': 'Cavalry',
    'Brazil': 'Artillery',
    'Argentina': 'Infantry',
    'Iceland': 'Cavalry',
    'Scandinavia': 'Artillery',
    'Ukraine': 'Infantry',
    'Great Britain': 'Cavalry',
    'Northern Europe': 'Artillery',
    'Western Europe': 'Infantry',
    'Southern Europe': 'Cavalry',
    'North Africa': 'Artillery',
    'Egypt': 'Infantry',
    'East Africa': 'Cavalry',
    'Congo': 'Artillery',
    'South Africa': 'Infantry',
    'Madagascar': 'Cavalry',
    'Ural': 'Artillery',
    'Siberia': 'Infantry',
    'Yakutsk': 'Cavalry',
    'Kamchatka': 'Artillery',
    'Irkutsk': 'Infantry',
    'Mongolia': 'Cavalry',
    'Japan': 'Artillery',
    'Afghanistan': 'Infantry',
    'China': 'Cavalry',
    'India': 'Artillery',
    'Siam': 'Infantry',
    'Indonesia': 'Cavalry',
    'New Guinea': 'Artillery',
    'Western Australia': 'Infantry',
    'Eastern Australia': 'Cavalry'
}


context = zmq.Context()

socket = context.socket(zmq.REP)
socket.bind('tcp://*:5555')

def export_data(data):
    serialized_data = pickle.dumps(data)
    socket.send(serialized_data)

def recieve_request():
    request = socket.recv_string()
    return request

if __name__ == '__main__':
    while True:
        request = recieve_request()
        if request == 'country_coords':
            export_data(country_coords)
        if request == 'continents':
            export_data(continents)
        if request == 'country_neighbors':
            export_data(country_neighbors)
        if request == 'deck':
            export_data(deck)
        if request == 'stop':
            break
    socket.close()
    context.term()
        

