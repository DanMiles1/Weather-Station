#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import time
import argparse
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
# from font_AmaticSC-Bold import AmaticSC-Bold
from datetime import date
import calendar

try:
    import requests
except ImportError:
    exit("This script requires the requests module\nInstall with: sudo pip install requests")

try:
    import geocoder
except ImportError:
    exit("This script requires the geocoder module\nInstall with: sudo pip install geocoder")

try:
    from bs4 import BeautifulSoup
except ImportError:
    exit("This script requires the bs4 module\nInstall with: sudo pip install beautifulsoup4")


#  print("""Inky pHAT: Weather
my_date = date.today()
# print calendar.day_name[my_date.weekday()]
tweekday = calendar.day_name[my_date.weekday()]
# Displays weather information for a given location. The default location is Sheffield-on-Sea.

# """)

# Command line arguments to set display colour

parser = argparse.ArgumentParser()
parser.add_argument('--colour', '-c', type=str, required=True, choices=["red", "black", "yellow"], help="ePaper display colour")
args = parser.parse_args()

# Set up the display

colour = args.colour
inky_display = InkyPHAT(colour)
inky_display.set_border(inky_display.BLACK)

# Details to customise your weather display

CITY = "Leighton Buzzard"
COUNTRYCODE = "GB"
WARNING_TEMP = 25.0

# Convert a city name and country code to latitude and longitude
def get_coords(address):
    g = geocoder.arcgis(address)
    coords = g.latlng
    return coords

# Query Dark Sky (https://darksky.net/) to scrape current weather data
def get_weather(address):
    coords = get_coords(address)
    weather = {}
    res = requests.get("https://darksky.net/forecast/{}/uk212/en".format(",".join([str(c) for c in coords])))
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "lxml")
        curr = soup.find_all("span", "currently")
        weather["summary"] = curr[0].img["alt"].split()[0]
        weather["temperature"] = int(curr[0].find("span", "summary").text.split()[0][:-1])
        press = soup.find_all("div", "pressure")
        weather["pressure"] = int(press[0].find("span", "num").text)
        humidity = soup.find_all("div", "humidity")
        weather["humidity"] = int(humidity[0].find("span", "num").text)
        wind = soup.find_all("div", "wind")
        weather["wind"] = int(wind[0].find("span", "num").text)
        uv = soup.find_all("div", "uv_index uv0")
        weather["uv"] = int(uv[0].find("span", "num").text)
        return weather
    else:
        return weather

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
location_string = "{city}, {countrycode}".format(city=CITY, countrycode=COUNTRYCODE)
weather = get_weather(location_string)

# This maps the weather summary from Dark Sky
# to the appropriate weather icons
icon_map = {
    "snow": ["snow", "sleet"],
    "rain": ["rain"],
    "cloud": ["fog", "cloudy", "partly-cloudy-day", "partly-cloudy-night"],
    "sun": ["clear-day", "clear-night"],
    "storm": [],
    "wind": ["wind"]
}

# Placeholder variables
pressure = 0
temperature = 0
weather_icon = None

if weather:
    temperature = weather["temperature"]
    pressure = weather["pressure"]
    summary = weather["summary"]
    humidity = weather["humidity"]
    wind = weather["wind"]
    uv = weather["uv"]

    for icon in icon_map:
        if summary in icon_map[icon]:
            weather_icon = icon
            break

else:
    print("Warning, no weather information found!")

# Create a new canvas to draw on
img = Image.open("/home/pi/cronjobs/resources/DMempty-backdrop.png")
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob("/home/pi/cronjobs/resources/icon-*.png"):
    icon_name = icon.split("icon-")[1].replace(".png", "")
    icon_image = Image.open(icon)
    icons[icon_name] = icon_image
    masks[icon_name] = create_mask(icon_image)

# Load the FredokaOne font
font = ImageFont.truetype("/home/pi/cronjobs/SquadaOne-Regular.ttf", 22)

# Draw lines to frame the weather data
draw.line((69, 36, 69, 81))       # Vertical line
draw.line((31, 35, 184, 35))      # Horizontal top line
draw.line((69, 58, 174, 58))      # Horizontal middle line
draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D


if time.strftime("%m") == "01":
   month = "January"
if time.strftime("%m") == "02":
   month = "February"
if time.strftime("%m") == "03":
   month = "March"
if time.strftime("%m") == "04":
   month = "April"
if time.strftime("%m") == "05":
   month = "May"
if time.strftime("%m") == "06":
   month = "June"
if time.strftime("%m") == "07":
   month = "July"
if time.strftime("%m") == "08":
   month = "August"
if time.strftime("%m") == "09":
   month = "September"
if time.strftime("%m") == "10":
   month = "October"
if time.strftime("%m") == "11":
   month = "November"
if time.strftime("%m") == "12":
   month = "December"
# else:
#     print("ffffh")
if time.strftime("%d") == "1":
   ord = "st"
if time.strftime("%d") == "2":
   ord = "nd"
if time.strftime("%d") == "3":
   ord = "rd"
if time.strftime("%d") == "21":
   ord = "st"
if time.strftime("%d") == "22":
   ord = "nd"
if time.strftime("%d") == "23":
   ord = "rd"
if time.strftime("%d") == "31":
   ord = "st"
else:
   ord = "th"

# Write text with weather values to the canvas
# datetime = time.strftime("%d/%m %H:%M")
datetime = time.strftime("%d") + ord + " " + month

draw.text((20, 5), tweekday + " " + datetime, inky_display.BLACK, font=font)

# draw.text((72, 27), "T", inky_display.BLACK, font=font)
draw.text((60, 32), u"{}°".format(temperature) + "c", inky_display.BLACK if temperature < WARNING_TEMP else inky_display.RED, font=font)

# draw.text((72, 58), "P", inky_display.BLACK, font=font)
draw.text((130, 32), "{}".format(pressure) + "mb", inky_display.BLACK, font=font)
# draw.text((72, 50), "H", inky_display.BLACK, font=font)
draw.text((60, 55), "{}".format(humidity) + "%", inky_display.BLACK, font=font)
# draw.text((10, 75), "W", inky_display.BLACK, font=font)
draw.text((60, 75), "{}".format(wind) + " mph", inky_display.BLACK, font=font)
# draw.text((120, 75), "UV", inky_display.BLACK, font=font)
draw.text((130, 55), "{}".format(uv), inky_display.BLACK, font=font)
# Draw the current weather icon over the backdrop
if weather_icon is not None:
    img.paste(icons[weather_icon], (5, 30), masks[weather_icon])

else:
    draw.text((28, 36), "?", inky_display.RED, font=font)

# Display the weather data on Inky pHAT
inky_display.set_image(img)
inky_display.show()

