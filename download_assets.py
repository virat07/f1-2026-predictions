import os
import requests
import time

WIKI_API_URL = "https://en.wikipedia.org/w/api.php"

def get_image_url(search_query, size=600):
    # Search for the page
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": search_query,
        "format": "json"
    }
    headers = {"User-Agent": "F1_App_Downloader/1.0"}
    try:
        res = requests.get(WIKI_API_URL, params=search_params, headers=headers).json()
        if not res['query']['search']: return None
        
        title = res['query']['search'][0]['title']
        
        # Get image for the specific page
        img_params = {
            "action": "query",
            "titles": title,
            "prop": "pageimages",
            "pithumbsize": size,
            "format": "json"
        }
        img_res = requests.get(WIKI_API_URL, params=img_params, headers=headers).json()
        pages = img_res['query']['pages']
        for _, pageinfo in pages.items():
            if 'thumbnail' in pageinfo:
                return pageinfo['thumbnail']['source']
    except Exception as e:
        print(f"Error fetching {search_query}: {e}")
    return None

def download_image(url, save_path):
    if not url: return False
    try:
        data = requests.get(url, headers={"User-Agent": "F1_App_Downloader/1.0"}).content
        with open(save_path, 'wb') as f:
            f.write(data)
        return True
    except Exception as e:
        print(e)
        return False

DRIVERS = [
    "Lewis Hamilton", "Max Verstappen", "Charles Leclerc", "Lando Norris", 
    "Oscar Piastri", "George Russell", "Andrea Kimi Antonelli", "Fernando Alonso",
    "Lance Stroll", "Isack Hadjar", "Pierre Gasly", "Franco Colapinto",
    "Nico Hülkenberg", "Gabriel Bortoleto", "Alex Albon", "Carlos Sainz",
    "Oliver Bearman", "Esteban Ocon", "Liam Lawson", "Arvid Lindblad",
    "Valtteri Bottas", "Sergio Pérez"
]

TEAMS = [
    "Scuderia Ferrari F1", "McLaren F1 Team", "Red Bull Racing F1", 
    "Mercedes-AMG Petronas F1", "Aston Martin Aramco F1", 
    "Alpine F1 Team", "Audi F1 Team", "Williams Racing F1", 
    "Haas F1 Team", "Racing Bulls F1", "Cadillac F1"
]

def format_filename(name):
    return name.lower().replace(" ", "-").replace("é", "e").replace("ü", "u") + ".png"

def main():
    os.makedirs("public/assets/drivers", exist_ok=True)
    os.makedirs("public/assets/teams", exist_ok=True)
    os.makedirs("public/assets/circuits", exist_ok=True)
    
    print("Downloading Driver Photos...")
    for driver in DRIVERS:
        filename = f"public/assets/drivers/{format_filename(driver)}"
        if os.path.exists(filename): continue
        url = get_image_url(driver + " F1 driver", size=500)
        if download_image(url, filename):
            print(f"✅ Downloaded {driver}")
        else:
            print(f"❌ Failed to find {driver}")
        time.sleep(0.5)
        
    print("\nDownloading Team Cars...")
    # Map back to exact names in JS file
    team_keys = [
        "Scuderia Ferrari", "McLaren F1 Team", "Oracle Red Bull Racing", 
        "Mercedes-AMG Petronas", "Aston Martin Aramco", "BWT Alpine F1 Team", 
        "Audi F1 Team", "Williams Racing", "MoneyGram Haas F1", 
        "Racing Bulls", "Cadillac F1 Team"
    ]
    for team, search in zip(team_keys, TEAMS):
        filename = f"public/assets/teams/{format_filename(team)}"
        if os.path.exists(filename): continue
        url = get_image_url(search + " Formula One car", size=800)
        if download_image(url, filename):
            print(f"✅ Downloaded {team}")
        else:
            print(f"❌ Failed to find {team}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
