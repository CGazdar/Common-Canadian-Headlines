"""Extra GDELT domains that belong to an outlet already in outlets.csv.
Format: "domain as GDELT spells it": "outlet_id".  Edit freely; unknown outlet ids are ignored."""
EXTRA_DOMAINS = {
    # CTV regional sites
    "toronto.ctvnews.ca": "ctv", 
    "montreal.ctvnews.ca": "ctv", "ottawa.ctvnews.ca": "ctv",
    "kitchener.ctvnews.ca": "ctv",
    "barrie.ctvnews.ca": "ctv", "windsor.ctvnews.ca": "ctv", "london.ctvnews.ca": "ctv",
    "vancouverisland.ctvnews.ca": "ctv",
    "northernontario.ctvnews.ca": "ctv",
    # CityNews regional sites
    "toronto.citynews.ca": "citynews", "calgary.citynews.ca": "citynews",
    "vancouver.citynews.ca": "citynews", "ottawa.citynews.ca": "citynews",
    "montreal.citynews.ca": "citynews", "kitchener.citynews.ca": "citynews",
    "winnipeg.citynews.ca": "citynews", "halifax.citynews.ca": "citynews", "edmonton.citynews.ca": "citynews",
}