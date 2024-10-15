import requests
from bs4 import BeautifulSoup
import pandas as pd

# Function to get Craigslist locations and state name
def get_craigslist_locations(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Safely get the state name from the breadcrumb
    state_name_element = soup.find('li', class_='crumb')
    if state_name_element is None or state_name_element.p is None:
        print(f"State name not found for URL: {url}")
        return None, None

    state_name = state_name_element.p.text.strip()

    # Find all city locations under the relevant section
    locations_section = soup.find('ul', class_='geo-site-list')
    if locations_section is None:
        print(f"Locations section not found for state: {state_name}")
        return state_name, []

    # Extract all location names from <a> tags
    location_links = locations_section.find_all('a')
    locations = [link.text.strip() for link in location_links] if location_links else []
    
    return state_name, locations

# Dictionary to store scraped Craigslist data
craigslist_data = {}

# List of Craigslist links for all 50 states
state_links = {
    "Alabama": "https://geo.craigslist.org/iso/us/al",
    "Alaska": "https://geo.craigslist.org/iso/us/ak",
    "Arizona": "https://geo.craigslist.org/iso/us/az",
    "Arkansas": "https://geo.craigslist.org/iso/us/ar",
    "California": "https://geo.craigslist.org/iso/us/ca",
    "Colorado": "https://geo.craigslist.org/iso/us/co",
    "Connecticut": "https://geo.craigslist.org/iso/us/ct",
    "Delaware": "https://geo.craigslist.org/iso/us/de",
    "Florida": "https://geo.craigslist.org/iso/us/fl",
    "Georgia": "https://geo.craigslist.org/iso/us/ga",
    "Hawaii": "https://geo.craigslist.org/iso/us/hi",
    "Idaho": "https://geo.craigslist.org/iso/us/id",
    "Illinois": "https://geo.craigslist.org/iso/us/il",
    "Indiana": "https://geo.craigslist.org/iso/us/in",
    "Iowa": "https://geo.craigslist.org/iso/us/ia",
    "Kansas": "https://geo.craigslist.org/iso/us/ks",
    "Kentucky": "https://geo.craigslist.org/iso/us/ky",
    "Louisiana": "https://geo.craigslist.org/iso/us/la",
    "Maine": "https://geo.craigslist.org/iso/us/me",
    "Maryland": "https://geo.craigslist.org/iso/us/md",
    "Massachusetts": "https://geo.craigslist.org/iso/us/ma",
    "Michigan": "https://geo.craigslist.org/iso/us/mi",
    "Minnesota": "https://geo.craigslist.org/iso/us/mn",
    "Mississippi": "https://geo.craigslist.org/iso/us/ms",
    "Missouri": "https://geo.craigslist.org/iso/us/mo",
    "Montana": "https://geo.craigslist.org/iso/us/mt",
    "Nebraska": "https://geo.craigslist.org/iso/us/ne",
    "Nevada": "https://geo.craigslist.org/iso/us/nv",
    "New Hampshire": "https://geo.craigslist.org/iso/us/nh",
    "New Jersey": "https://geo.craigslist.org/iso/us/nj",
    "New Mexico": "https://geo.craigslist.org/iso/us/nm",
    "New York": "https://geo.craigslist.org/iso/us/ny",
    "North Carolina": "https://geo.craigslist.org/iso/us/nc",
    "North Dakota": "https://geo.craigslist.org/iso/us/nd",
    "Ohio": "https://geo.craigslist.org/iso/us/oh",
    "Oklahoma": "https://geo.craigslist.org/iso/us/ok",
    "Oregon": "https://geo.craigslist.org/iso/us/or",
    "Pennsylvania": "https://geo.craigslist.org/iso/us/pa",
    "Rhode Island": "https://geo.craigslist.org/iso/us/ri",
    "South Carolina": "https://geo.craigslist.org/iso/us/sc",
    "South Dakota": "https://geo.craigslist.org/iso/us/sd",
    "Tennessee": "https://geo.craigslist.org/iso/us/tn",
    "Texas": "https://geo.craigslist.org/iso/us/tx",
    "Utah": "https://geo.craigslist.org/iso/us/ut",
    "Vermont": "https://geo.craigslist.org/iso/us/vt",
    "Virginia": "https://geo.craigslist.org/iso/us/va",
    "Washington": "https://geo.craigslist.org/iso/us/wa",
    "West Virginia": "https://geo.craigslist.org/iso/us/wv",
    "Wisconsin": "https://geo.craigslist.org/iso/us/wi",
    "Wyoming": "https://geo.craigslist.org/iso/us/wy"
}
# Loop through all state links and scrape data
for state, url in state_links.items():
    try:
        state_name, locations = get_craigslist_locations(url)

        # Replace "United States" with "Alaska" if needed
        if state_name == "United States" and state == "Alaska":
            state_name = "Alaska"

        # Handle empty location lists by adding the state name as a location
        if not locations:
            locations = [state]

        # Store results in the dictionary
        craigslist_data[state_name] = locations

    except Exception as e:
        print(f"Error scraping {state}: {e}")

# Reverse the dictionary to map location -> state
location_to_state = {
    location: state
    for state, locations in craigslist_data.items()
    for location in locations
}

# Load the dataset from the Excel file
df = pd.read_excel(r'data\carbitrage-data.xlsx')

# Add a 'State' column based on the 'location' column using the reversed dictionary
df['state'] = df['location'].map(location_to_state)

print("Data scraping and transformation completed successfully.")

# Manual corrections for known abbreviations and unusual naming patterns
manual_location_to_state = {
    'eastnc': 'North Carolina', 'rapidcity': 'South Dakota', 
    'akroncanton': 'Ohio', 'corvallis': 'Oregon', 
    'hiltonhead': 'South Carolina', 'westernmass': 'Massachusetts',
    'allentown': 'Pennsylvania', 'columbusga': 'Georgia',
    'santafe': 'New Mexico', 'monterey': 'California', 
    'siskiyou': 'California', 'limaohio': 'Ohio', 
    'kpr': 'Washington', 'desmoines': 'Iowa',
    'losangeles': 'California', 'cnj': 'New Jersey',
    'lascruces': 'New Mexico', 'kansascity': 'Missouri',
    'longisland': 'New York', 'sfbay': 'California', 
    'sarasota': 'Florida', 'dallas': 'Texas', 'sd': 'South Dakota',
    'inlandempire': 'California', 'sierravista': 'Arizona',
    'newyork': 'New York', 'seattle': 'Washington', 
    'charlestonwv': 'West Virginia', 'mohave': 'Arizona', 
    'goldcountry': 'California', 'orangecounty': 'California', 
    'slo': 'California', 'lasvegas': 'Nevada',
    'glensfalls': 'New York', 'vermont': 'Vermont',
    'mcallen': 'Texas', 'stlouis': 'Missouri',
    'twinfalls': 'Idaho', 'miami': 'Florida', 
    'greenville': 'South Carolina', 'lasalle': 'Illinois', 
    'ventura': 'California', 'fresno': 'California',
    'tampa': 'Florida', 'lakecity': 'Florida', 
    'flagstaff': 'Arizona', 'southjersey': 'New Jersey', 
    'treasure': 'Florida', 'oklahomacity': 'Oklahoma', 
    'spokane': 'Washington', 'cosprings': 'Colorado',
    'sanantonio': 'Texas', 'plattsburgh': 'New York', 
    'worcester': 'Massachusetts', 'newjersey': 'New Jersey',
    'anchorage': 'Alaska', 'washingtondc': 'District of Columbia',
    'sandiego': 'California', 'norfolk': 'Virginia',
    'hartford': 'Connecticut', 'salem': 'Oregon', 'gainesville': 'Florida',
    'charleston': 'South Carolina', 'yakima': 'Washington', 'springfield': 'Illinois',
    'ocala': 'Florida', 'bakersfield': 'California', 'albany': 'New York',
    'lakeland': 'Florida', 'tallahassee': 'Florida', 'chattanooga': 'Tennessee',
    'brainerd': 'Minnesota', 'rockford': 'Illinois', 'memphis': 'Tennessee',
    'asheville': 'North Carolina', 'eugene': 'Oregon', 'phoenix': 'Arizona',
    'sacramento': 'California', 'chicago': 'Illinois', 'portland': 'Oregon',
    'houston': 'Texas', 'charlotte': 'North Carolina', 'boston': 'Massachusetts',
    'yuma': 'Arizona', 'orlando': 'Florida', 'cleveland': 'Ohio',
    'bend': 'Oregon', 'austin': 'Texas', 'bemidji': 'Minnesota',
    'milwaukee': 'Wisconsin', 'tucson': 'Arizona', 'albuquerque': 'New Mexico',
    'jacksonville': 'Florida', 'atlanta': 'Georgia', 'denver': 'Colorado',
    'pittsburgh': 'Pennsylvania', 'knoxville': 'Tennessee', 'flint': 'Michigan',
    'syracuse': 'New York', 'redding': 'California', 'binghamton': 'New York',
    'rochester': 'New York', 'kalispell': 'Montana', 'modesto': 'California',
    'baltimore': 'Maryland', 'indianapolis': 'Indiana', 'madison': 'Wisconsin',
    'honolulu': 'Hawaii', 'nashville': 'Tennessee', 'saltlakecity': 'Utah',
    'rockies': 'Colorado', 'fortcollins': 'Colorado', 'lexington': 'Kentucky',
    'batonrouge': 'Louisiana', 'chico': 'California', 'lancaster': 'Pennsylvania',
    'boise': 'Idaho', 'mankato': 'Minnesota', 'detroit': 'Michigan',
    'augusta': 'Maine', 'richmond': 'Virginia', 'maine': 'Maine',
    'lansing': 'Michigan', 'bellingham': 'Washington', 'toledo': 'Ohio',
    'minneapolis': 'Minnesota', 'buffalo': 'New York', 'dayton': 'Ohio',
    'seks': 'Kansas', 'palmsprings': 'California', 'medford': 'Oregon',
    'youngstown': 'Ohio', 'annarbor': 'Michigan', 'omaha': 'Nebraska',
    'reno': 'Nevada', 'columbia': 'South Carolina', 'philadelphia': 'Pennsylvania',
    'stockton': 'California', 'helena': 'Montana', 'newlondon': 'Connecticut',
    'cincinnati': 'Ohio', 'easttexas': 'Texas', 'littlerock': 'Arkansas',
    'huntsville': 'Alabama', 'newhaven': 'Connecticut', 'grandrapids': 'Michigan',
    'bham': 'Alabama', 'peoria': 'Illinois', 'macon': 'Georgia',
    'raleigh': 'North Carolina', 'myrtlebeach': 'South Carolina', 
    'victoriatx': 'Texas', 'charlottesville': 'Virginia', 'skagit': 'Washington',
    'nh': 'New Hampshire', 'santabarbara': 'California', 'bozeman': 'Montana',
    'wilmington': 'North Carolina', 'greensboro': 'North Carolina',
    'fortmyers': 'Florida', 'tippecanoe': 'Indiana', 'montgomery': 'Alabama',
    'spacecoast': 'Florida', 'greenbay': 'Wisconsin', 'hudsonvalley': 'New York',
    'saginaw': 'Michigan', 'centralmich': 'Michigan', 'jerseyshore': 'New Jersey',
    'scranton': 'Pennsylvania', 'appleton': 'Wisconsin', 'texoma': 'Texas',
    'hickory': 'North Carolina', 'pensacola': 'Florida', 'humboldt': 'California',
    'farmington': 'New Mexico', 'providence': 'Rhode Island', 'muskegon': 'Michigan',
    'springfieldil': 'Illinois', 'easternshore': 'Maryland', 'martinsburg': 'West Virginia',
    'lewiston': 'Idaho', 'annapolis': 'Maryland', 'eauclaire': 'Wisconsin',
    'erie': 'Pennsylvania', 'oregoncoast': 'Oregon', 'elpaso': 'Texas',
    'up': 'Michigan', 'merced': 'California', 'tulsa': 'Oklahoma',
    'daytona': 'Florida', 'greatfalls': 'Montana', 'westslope': 'Colorado',
    'wenatchee': 'Washington', 'klamath': 'Oregon', 'swva': 'Virginia',
    'showlow': 'Arizona', 'okaloosa': 'Florida', 'quadcities': 'Illinois',
    'roseburg': 'Oregon', 'york': 'Pennsylvania', 'savannah': 'Georgia',
    'bgky': 'Kentucky', 'fayar': 'Arkansas', 'swmi': 'Michigan',
    'yubasutter': 'California', 'eastky': 'Kentucky', 'gadsden': 'Alabama',
    'rmn': 'Minnesota', 'stillwater': 'Minnesota', 'stgeorge': 'Utah',
    'billings': 'Montana', 'delaware': 'Delaware', 'winstonsalem': 'North Carolina',
    'panamacity': 'Florida', 'missoula': 'Montana', 'ames': 'Iowa',
    'olympic': 'Washington', 'columbiamo': 'Missouri', 'fortsmith': 'Arkansas',
    'collegestation': 'Texas', 'lubbock': 'Texas', 'fargo': 'North Dakota',
    'nwga': 'Georgia', 'athensga': 'Georgia', 'jonesboro': 'Arkansas',
    'fredericksburg': 'Virginia', 'brownsville': 'Texas', 'montana': 'Montana',
    'fairbanks': 'Alaska', 'pennstate': 'Pennsylvania', 'duluth': 'Minnesota',
    'columbus': 'Ohio', 'fayetteville': 'North Carolina', 'abilene': 'Texas',
    'wyoming': 'Wyoming', 'prescott': 'Arizona', 'topeka': 'Kansas',
    'jackson': 'Mississippi', 'northmiss': 'Mississippi', 'juneau': 'Alaska',
    'ithaca': 'New York', 'wichita': 'Kansas', 'neworleans': 'Louisiana',
    'mobile': 'Alabama', 'boulder': 'Colorado', 'killeen': 'Texas',
    'lynchburg': 'Virginia', 'dothan': 'Alabama', 'wausau': 'Wisconsin',
    'louisville': 'Kentucky', 'pullman': 'Washington', 'hattiesburg': 'Mississippi',
    'fortwayne': 'Indiana', 'kalamazoo': 'Michigan', 'racine': 'Wisconsin',
    'nmi': 'Michigan', 'loz': 'Missouri', 'eastidaho': 'Idaho', 
    'ashtabula': 'Ohio', 'nwct': 'Connecticut', 'southcoast': 'Massachusetts', 
    'elmira': 'New York', 'altoona': 'Pennsylvania', 'carbondale': 'Illinois', 
    'utica': 'New York', 'smd': 'Maryland', 'cedarrapids': 'Iowa', 
    'iowacity': 'Iowa', 'mendocino': 'California', 'harrisonburg': 'Virginia', 
    'frederick': 'Maryland', 'lincoln': 'Nebraska', 'amarillo': 'Texas', 
    'staugustine': 'Florida', 'potsdam': 'New York', 'moseslake': 'Washington', 
    'dubuque': 'Iowa', 'lacrosse': 'Wisconsin', 'tricities': 'Washington', 
    'catskills': 'New York', 'chautauqua': 'New York', 'pueblo': 'Colorado', 
    'southbend': 'Indiana', 'williamsport': 'Pennsylvania', 'waco': 'Texas', 
    'winchester': 'Virginia', 'capecod': 'Massachusetts', 'roanoke': 'Virginia', 
    'gulfport': 'Mississippi', 'danville': 'Virginia', 'harrisburg': 'Pennsylvania', 
    'corpuschristi': 'Texas', 'poconos': 'Pennsylvania', 'jxn': 'Mississippi', 
    'stcloud': 'Minnesota', 'santamaria': 'California', 'kenai': 'Alaska', 
    'visalia': 'California', 'butte': 'Montana', 'fortdodge': 'Iowa', 
    'evansville': 'Indiana', 'siouxcity': 'Iowa', 'siouxfalls': 'South Dakota', 
    'sheboygan': 'Wisconsin', 'clarksville': 'Tennessee', 'thumb': 'Michigan', 
    'reading': 'Pennsylvania', 'lafayette': 'Louisiana', 'bn': 'Illinois', 
    'odessa': 'Texas', 'lakecharles': 'Louisiana', 'joplin': 'Missouri', 
    'shreveport': 'Louisiana', 'hanford': 'California', 'brunswick': 'Georgia', 
    'stjoseph': 'Missouri', 'northernwi': 'Wisconsin', 'northplatte': 'Nebraska', 
    'holland': 'Michigan', 'zanesville': 'Ohio', 'chambana': 'Illinois', 
    'roswell': 'New Mexico', 'bloomington': 'Indiana', 'boone': 'North Carolina', 
    'cenla': 'Louisiana', 'wheeling': 'West Virginia', 'valdosta': 'Georgia', 
    'chambersburg': 'Pennsylvania', 'muncie': 'Indiana', 'battlecreek': 'Michigan', 
    'monroemi': 'Michigan', 'semo': 'Missouri', 'blacksburg': 'Virginia', 
    'westky': 'Kentucky', 'beaumont': 'Texas', 'morgantown': 'West Virginia', 
    'shoals': 'Alabama', 'galveston': 'Texas', 'watertown': 'New York', 
    'mansfield': 'Ohio', 'sanmarcos': 'Texas', 'delrio': 'Texas', 
    'statesboro': 'Georgia', 'twintiers': 'New York', 'chillicothe': 'Ohio', 
    'monroe': 'Louisiana', 'athensohio': 'Ohio', 'waterloo': 'Iowa', 
    'huntington': 'West Virginia', 'kokomo': 'Indiana', 'bismarck': 'North Dakota', 
    'lawrence': 'Kansas', 'natchez': 'Mississippi', 'parkersburg': 'West Virginia', 
    'nacogdoches': 'Texas', 'kirksville': 'Missouri', 'lawton': 'Oklahoma', 
    'grandisland': 'Nebraska', 'ottumwa': 'Iowa', 'grandforks': 'North Dakota', 
    'florencesc': 'South Carolina', 'masoncity': 'Iowa', 'fingerlakes': 'New York', 
    'eastoregon': 'Oregon', 'onslow': 'North Carolina', 'westmd': 'Maryland', 
    'terrehaute': 'Indiana', 'provo': 'Utah', 'owensboro': 'Kentucky', 
    'imperial': 'California', 'outerbanks': 'North Carolina', 'sanangelo': 'Texas', 
    'quincy': 'Illinois', 'swv': 'Virginia', 'oneonta': 'New York', 
    'tuscaloosa': 'Alabama', 'nd': 'North Dakota', 'texarkana': 'Texas', 
    'marshall': 'Texas', 'ksu': 'Kansas', 'auburn': 'Alabama', 
    'porthuron': 'Michigan', 'clovis': 'New Mexico', 'decatur': 'Illinois', 
    'janesville': 'Wisconsin', 'wichitafalls': 'Texas', 'nesd': 'South Dakota', 
    'cookeville': 'Tennessee', 'cfl': 'Florida', 'albanyga': 'Georgia', 
    'scottsbluff': 'Nebraska', 'tuscarawas': 'Ohio', 'meridian': 'Mississippi', 
    'ogden': 'Utah', 'jacksontn': 'Tennessee', 'nwks': 'Kansas', 
    'meadville': 'Pennsylvania', 'keys': 'Florida', 'laredo': 'Texas', 
    'sandusky': 'Ohio', 'mattoon': 'Illinois', 'eastco': 'South Carolina', 
    'enid': 'Oklahoma', 'salina': 'Kansas', 'susanville': 'California', 
    'wv': 'West Virginia', 'houma': 'Louisiana', 'richmondin': 'Indiana', 
    'swks': 'Kansas', 'elko': 'Nevada', 'logan': 'Utah', 'bigbend': 'Texas', 
    'csd': 'South Dakota'
}

# Re-apply the mapping with the extended dictionary
df['state'] = df['location'].str.lower().map(manual_location_to_state)

# Save the updated DataFrame with resolved state mappings
df.to_excel(r'data\carbitrage-data-updated.xlsx', index=False)

print("State mapping updated successfully with extended manual corrections.")

# Display remaining missing state mappings
remaining_missing_states = df[df['state'].isna()]
print(f"Remaining missing locations:\n{remaining_missing_states['location'].unique()}")

# Save the updated DataFrame
df.to_excel(r'data\carbitrage-data-updated.xlsx', index=False)

print("Manual correction and data update completed.")
