import requests
import os
import time

# Finalized list for 2026 predictions
DRIVERS = {
  "g-russell": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-20230903-154941-1.jpg",
  "l-norris": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-6919200_HiRes.jpg",
  "m-verstappen": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-6952409_HiRes.jpg",
  "andrea-kimi-antonelli": "https://www.racefans.net/wp-content/uploads/2024/09/racefansdotnet-2024-09-02_142243.jpg",
  "charles-leclerc": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-6908033_HiRes.jpg",
  "lewis-hamilton": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-23-09-19-15-20-26-1-XPB_1236705_HiRes_33.jpg",
  "oliver-bearman": "https://www.racefans.net/wp-content/uploads/2024/11/racefansdotnet-21-11-17-21-13-02-1.jpg",
  "arvid-lindblad": "https://www.racefans.net/wp-content/uploads/2024/11/racefansdotnet-2024-11-02_002328.jpg",
  "gabriel-bortoleto": "https://www.racefans.net/wp-content/uploads/2024/11/racefansdotnet-2024-11-02_002328.jpg",
  "pierre-gasly": "https://www.racefans.net/wp-content/uploads/2024/02/racefansdotnet-7154321_HiRes.jpg",
  "esteban-ocon": "https://www.racefans.net/wp-content/uploads/2025/03/racefansdotnet-24-03-20-11-32-50-4-2205966739-340.jpg",
  "alexander-albon": "https://www.racefans.net/wp-content/uploads/2023/08/racefansdotnet-6891015_HiRes.jpg",
  "liam-lawson": "https://www.racefans.net/wp-content/uploads/2023/08/racefansdotnet-23-08-25-22-30-39-4-XPB_1223545_HiRes.jpg",
  "franco-colapinto": "https://www.racefans.net/wp-content/uploads/2024/08/XPB_1291418_HiRes-scaled.jpg",
  "carlos-sainz": "https://www.racefans.net/wp-content/uploads/2024/03/racefansdotnet-24-03-21-03-35-21-3-240022-scuderia-ferrari-australia-gp-thursday_23e3abab-a8e5-4059-b3b0-780093636aa7.jpg",
  "sergio-perez": "https://www.racefans.net/wp-content/uploads/2022/10/racefansdotnet-22-10-06-08-46-41-13.jpg",
  "lance-stroll": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-23-09-01-00-38-31-1-GP2314_133118_U1A9360.jpg",
  "fernando-alonso": "https://www.racefans.net/wp-content/uploads/2023/03/racefansdotnet-23-03-05-18-42-35-8.jpg",
  "valtteri-bottas": "https://www.racefans.net/wp-content/uploads/2024/07/racefansdotnet-24-07-31-22-23-41-6-XPB_1295453_HiRes.jpg",
  "isack-hadjar": "https://www.racefans.net/wp-content/uploads/2024/09/racefansdotnet-24-08-30-10-39-22-1-SI202408301293_hires_jpeg_24bit_rgb.jpg",
  "oscar-piastri": "https://www.racefans.net/wp-content/uploads/2023/09/racefansdotnet-23-09-20-11-28-24-1-XPB_1214390_HiRes.jpg",
  "nico-hulkenberg": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-2023-02-11_0542243.jpg"
}

TEAMS = {
  "mercedes-amg-petronas": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-44-6.jpg",
  "mclaren-f1-team": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-47-2.jpg",
  "oracle-red-bull-racing": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-50-4-470x314.jpg",
  "scuderia-ferrari": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-46-5.jpg",
  "aston-martin-aramco": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-25-16-42-35-8.jpg",
  "bwt-alpine-f1-team": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-49-3.jpg",
  "audi-f1-team": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-44-1.jpg",
  "williams-racing": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-44-7.jpg",
  "moneygram-haas-f1": "https://www.racefans.net/wp-content/uploads/2023/02/racefansdotnet-23-02-24-07-04-47-1.jpg",
  "racing-bulls": "https://www.racefans.net/wp-content/uploads/2024/02/racefansdotnet-24-02-09-08-46-41-13.jpg",
  "cadillac-f1": "https://www.racefans.net/wp-content/uploads/2024/11/racefansdotnet-2024-11-25-22-23-41-6.jpg"
}

# Simple circuit map URLs (Wikimedia Commons or similar)
CIRCUITS = {
  "albert_park": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Albert_Park_Circuit_2022.svg/330px-Albert_Park_Circuit_2022.svg.png",
  "shanghai": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Shanghai_International_Racing_Circuit_track_map.svg/330px-Shanghai_International_Racing_Circuit_track_map.svg.png",
  "suzuka": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Suzuka_circuit_map--2005.svg/300px-Suzuka_circuit_map--2005.svg.png",
  "bahrain": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Bahrain_International_Circuit--Main_Circuit.svg/330px-Bahrain_International_Circuit--Main_Circuit.svg.png"
}

def download_assets():
    headers = {"User-Agent": "Mozilla/5.0"}
    
    for category, mapping in [("drivers", DRIVERS), ("teams", TEAMS), ("circuits", CIRCUITS)]:
        folder = f"public/assets/{category}"
        os.makedirs(folder, exist_ok=True)
        for name, url in mapping.items():
            path = f"{folder}/{name}.png"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
                    print(f"✅ {path}")
                else:
                    print(f"❌ {path} ({r.status_code})")
            except:
                print(f"⚠️ {path}")

if __name__ == "__main__":
    download_assets()
