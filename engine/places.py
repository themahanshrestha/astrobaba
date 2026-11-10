"""Small built-in place list (offline fallback). The web app first tries Open-Meteo geocoding in
the browser; if that is unreachable, or the place is missing, users can type latitude/longitude."""
_RAW = """Kathmandu|Nepal|27.7172|85.3240|Asia/Kathmandu
Pokhara|Nepal|28.2096|83.9856|Asia/Kathmandu
Lalitpur|Nepal|27.6588|85.3247|Asia/Kathmandu
Biratnagar|Nepal|26.4525|87.2718|Asia/Kathmandu
Birgunj|Nepal|27.0104|84.8770|Asia/Kathmandu
Bhaktapur|Nepal|27.6710|85.4298|Asia/Kathmandu
Butwal|Nepal|27.7006|83.4484|Asia/Kathmandu
Dharan|Nepal|26.8065|87.2846|Asia/Kathmandu
New Delhi|India|28.6139|77.2090|Asia/Kolkata
Mumbai|India|19.0760|72.8777|Asia/Kolkata
Kolkata|India|22.5726|88.3639|Asia/Kolkata
Chennai|India|13.0827|80.2707|Asia/Kolkata
Bengaluru|India|12.9716|77.5946|Asia/Kolkata
Hyderabad|India|17.3850|78.4867|Asia/Kolkata
Ahmedabad|India|23.0225|72.5714|Asia/Kolkata
Pune|India|18.5204|73.8567|Asia/Kolkata
Jaipur|India|26.9124|75.7873|Asia/Kolkata
Lucknow|India|26.8467|80.9462|Asia/Kolkata
Varanasi|India|25.3176|82.9739|Asia/Kolkata
Patna|India|25.5941|85.1376|Asia/Kolkata
Darjeeling|India|27.0360|88.2627|Asia/Kolkata
Guwahati|India|26.1445|91.7362|Asia/Kolkata
Dhaka|Bangladesh|23.8103|90.4125|Asia/Dhaka
Colombo|Sri Lanka|6.9271|79.8612|Asia/Colombo
Karachi|Pakistan|24.8607|67.0011|Asia/Karachi
Lahore|Pakistan|31.5204|74.3587|Asia/Karachi
Islamabad|Pakistan|33.6844|73.0479|Asia/Karachi
Thimphu|Bhutan|27.4728|89.6390|Asia/Thimphu
Kabul|Afghanistan|34.5553|69.2075|Asia/Kabul
Dubai|United Arab Emirates|25.2048|55.2708|Asia/Dubai
Doha|Qatar|25.2854|51.5310|Asia/Qatar
Riyadh|Saudi Arabia|24.7136|46.6753|Asia/Riyadh
Kuwait City|Kuwait|29.3759|47.9774|Asia/Kuwait
Tehran|Iran|35.6892|51.3890|Asia/Tehran
Istanbul|Turkey|41.0082|28.9784|Europe/Istanbul
Tel Aviv|Israel|32.0853|34.7818|Asia/Jerusalem
Cairo|Egypt|30.0444|31.2357|Africa/Cairo
Lagos|Nigeria|6.5244|3.3792|Africa/Lagos
Nairobi|Kenya|-1.2921|36.8219|Africa/Nairobi
Johannesburg|South Africa|-26.2041|28.0473|Africa/Johannesburg
Cape Town|South Africa|-33.9249|18.4241|Africa/Johannesburg
Casablanca|Morocco|33.5731|-7.5898|Africa/Casablanca
Addis Ababa|Ethiopia|9.0320|38.7469|Africa/Addis_Ababa
London|United Kingdom|51.5072|-0.1276|Europe/London
Manchester|United Kingdom|53.4808|-2.2426|Europe/London
Edinburgh|United Kingdom|55.9533|-3.1883|Europe/London
Dublin|Ireland|53.3498|-6.2603|Europe/Dublin
Paris|France|48.8566|2.3522|Europe/Paris
Berlin|Germany|52.5200|13.4050|Europe/Berlin
Munich|Germany|48.1351|11.5820|Europe/Berlin
Madrid|Spain|40.4168|-3.7038|Europe/Madrid
Barcelona|Spain|41.3851|2.1734|Europe/Madrid
Lisbon|Portugal|38.7223|-9.1393|Europe/Lisbon
Rome|Italy|41.9028|12.4964|Europe/Rome
Milan|Italy|45.4642|9.1900|Europe/Rome
Amsterdam|Netherlands|52.3676|4.9041|Europe/Amsterdam
Brussels|Belgium|50.8503|4.3517|Europe/Brussels
Zurich|Switzerland|47.3769|8.5417|Europe/Zurich
Vienna|Austria|48.2082|16.3738|Europe/Vienna
Stockholm|Sweden|59.3293|18.0686|Europe/Stockholm
Oslo|Norway|59.9139|10.7522|Europe/Oslo
Copenhagen|Denmark|55.6761|12.5683|Europe/Copenhagen
Helsinki|Finland|60.1699|24.9384|Europe/Helsinki
Warsaw|Poland|52.2297|21.0122|Europe/Warsaw
Prague|Czechia|50.0755|14.4378|Europe/Prague
Athens|Greece|37.9838|23.7275|Europe/Athens
Moscow|Russia|55.7558|37.6173|Europe/Moscow
Kyiv|Ukraine|50.4501|30.5234|Europe/Kyiv
New York|United States|40.7128|-74.0060|America/New_York
Boston|United States|42.3601|-71.0589|America/New_York
Washington|United States|38.9072|-77.0369|America/New_York
Miami|United States|25.7617|-80.1918|America/New_York
Atlanta|United States|33.7490|-84.3880|America/New_York
Chicago|United States|41.8781|-87.6298|America/Chicago
Houston|United States|29.7604|-95.3698|America/Chicago
Dallas|United States|32.7767|-96.7970|America/Chicago
Denver|United States|39.7392|-104.9903|America/Denver
Phoenix|United States|33.4484|-112.0740|America/Phoenix
Los Angeles|United States|34.0522|-118.2437|America/Los_Angeles
San Francisco|United States|37.7749|-122.4194|America/Los_Angeles
Seattle|United States|47.6062|-122.3321|America/Los_Angeles
Anchorage|United States|61.2181|-149.9003|America/Anchorage
Honolulu|United States|21.3069|-157.8583|Pacific/Honolulu
Toronto|Canada|43.6532|-79.3832|America/Toronto
Vancouver|Canada|49.2827|-123.1207|America/Vancouver
Montreal|Canada|45.5019|-73.5674|America/Toronto
Mexico City|Mexico|19.4326|-99.1332|America/Mexico_City
Havana|Cuba|23.1136|-82.3666|America/Havana
Bogota|Colombia|4.7110|-74.0721|America/Bogota
Lima|Peru|-12.0464|-77.0428|America/Lima
Santiago|Chile|-33.4489|-70.6693|America/Santiago
Buenos Aires|Argentina|-34.6037|-58.3816|America/Argentina/Buenos_Aires
Sao Paulo|Brazil|-23.5505|-46.6333|America/Sao_Paulo
Rio de Janeiro|Brazil|-22.9068|-43.1729|America/Sao_Paulo
Beijing|China|39.9042|116.4074|Asia/Shanghai
Shanghai|China|31.2304|121.4737|Asia/Shanghai
Hong Kong|China|22.3193|114.1694|Asia/Hong_Kong
Taipei|Taiwan|25.0330|121.5654|Asia/Taipei
Tokyo|Japan|35.6762|139.6503|Asia/Tokyo
Osaka|Japan|34.6937|135.5023|Asia/Tokyo
Seoul|South Korea|37.5665|126.9780|Asia/Seoul
Singapore|Singapore|1.3521|103.8198|Asia/Singapore
Kuala Lumpur|Malaysia|3.1390|101.6869|Asia/Kuala_Lumpur
Bangkok|Thailand|13.7563|100.5018|Asia/Bangkok
Hanoi|Vietnam|21.0278|105.8342|Asia/Ho_Chi_Minh
Ho Chi Minh City|Vietnam|10.8231|106.6297|Asia/Ho_Chi_Minh
Jakarta|Indonesia|-6.2088|106.8456|Asia/Jakarta
Manila|Philippines|14.5995|120.9842|Asia/Manila
Yangon|Myanmar|16.8409|96.1735|Asia/Yangon
Sydney|Australia|-33.8688|151.2093|Australia/Sydney
Melbourne|Australia|-37.8136|144.9631|Australia/Melbourne
Perth|Australia|-31.9505|115.8605|Australia/Perth
Brisbane|Australia|-27.4698|153.0251|Australia/Brisbane
Auckland|New Zealand|-36.8485|174.7633|Pacific/Auckland"""
PLACES = []
for line in _RAW.splitlines():
    n, c, la, lo, tz = line.split("|")
    PLACES.append({"name": n, "country": c, "lat": float(la), "lon": float(lo), "tz": tz})


def search(q: str, limit: int = 8) -> list[dict]:
    q = q.strip().lower()
    if len(q) < 2:
        return []
    hits = [p for p in PLACES if p["name"].lower().startswith(q)] + \
           [p for p in PLACES if q in p["name"].lower() and not p["name"].lower().startswith(q)] + \
           [p for p in PLACES if q in p["country"].lower() and q not in p["name"].lower()]
    return hits[:limit]
