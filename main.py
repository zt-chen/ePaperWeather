#!/usr/bin/python3
# -*- coding:utf-8 -*-
import time
from PIL import Image,ImageDraw,ImageFont, ImageOps
import traceback
import os
import WeatherConfig
import requests
import pyowm
from datetime import datetime
from datetime import timedelta
import pytz
from pytz import timezone

TEST = WeatherConfig.TEST

if TEST:
    import matplotlib.pyplot as plt  # test
    import epd2in13_test as epd2in13
else:
    import epd2in13


CITY = 'Beijing,CN'
lat = 39.91
lon = 116.4
current_tz=timezone('Asia/Shanghai')
owm = pyowm.OWM(WeatherConfig.OWM_API_KEY)


def drawWeatherForecast(draw, image, icon_night_wea, icon_day_wea, high, low, nextDay=0):
    print("Drawing Forecast")
    forecastX = 150 
    forecastY = 5

    # Draw the division line
    lineStart = (forecastX,0)
    lineEnd = (forecastX, epd2in13.EPD_WIDTH)
    draw.line([lineStart, lineEnd], fill=0x00, width=2)

    forecastX = forecastX + 3
    # Draw text today or tomorrow
    if nextDay == 0:
        draw.text((forecastX+21,forecastY), "Today", font=fontSmall, fill=0)
    else:
        draw.text((forecastX+6,forecastY), "Tomorrow", font=fontSmall, fill=0)

    # Draw the division line
    lineStart = (forecastX-3,forecastY+25)
    lineEnd = (epd2in13.EPD_HEIGHT, forecastY+25)
    draw.line([lineStart, lineEnd], fill=0x00, width=0)

    forecastY = forecastY + 28
    # Draw forecast weather icon
    if nextDay == 0:
        draw.text((forecastX+7,forecastY), 'Now', font=fontSmaller, fill=0)
    else:
        draw.text((forecastX+7,forecastY), 'Day', font=fontSmaller, fill=0)
    if(len(icon_day_wea) ==3):
        icon_image_day = Image.open(CURRENT_DIR + '/weatherIcons/'+icon_day_wea+'.bmp').resize((30,30))
        image.paste(icon_image_day, (forecastX+10,forecastY+25))    

    draw.text((forecastX+47,forecastY), 'Night', font=fontSmaller, fill=0)
    if(len(icon_night_wea) == 3):
        icon_image_night = Image.open(CURRENT_DIR + '/weatherIcons/'+icon_night_wea+'.bmp').resize((30,30))
        image.paste(icon_image_night, (forecastX+45+10,forecastY+25))    

    # Draw forecast temperature
    draw.text((forecastX+15,forecastY+30+32),  low + '\xb0 ~ ' + high + '\xb0', font=fontSmall, fill=0)

# Get AQI data 
def getAQI(station_code):
    # Request Get
    req = requests.get(
            "http://api.waqi.info/feed/@%d/" % (station_code),
            params={'token': WeatherConfig.AQI_TOKEN})

    if req.status_code == 200 and req.json()['status'] == "ok":
        json = req.json()["data"]
        iaqi = json['iaqi']
        result = {
                'idx': json['idx'],
                'city': json.get('city', ''),
                'aqi': json['aqi'],
                'dominentpol': json.get("dominentpol", ''),
                'time': json['time']['s'],
                'iaqi': [{'p': item, 'v': iaqi[item]['v']} for item in iaqi]
                }
        return result
    else:
        return {}

# Draw AQI Data, Default, Chaoyang Olympic Sports Center
def drawAQI(draw, X, Y, font, station_code=450):
    aqiData = getAQI(station_code)
    if len(aqiData) > 0:
        print ("Got AQI:"+str(aqiData.get('aqi')))
        draw.text((X, Y), "AQI: "+str(aqiData.get('aqi')), 
                font=font, fill = 0)
    else:
        print("Get AQI failed")

def drawWeatherCurrent(draw, image, icon, temperature, uv, humidity):
    print("Drawing Current")
    startX = 8
    startY = 5+25 + 5

    if(len(icon) == 3):
        icon_image = Image.open(CURRENT_DIR + '/weatherIcons/'+icon+'.bmp').resize((50,50))
        image.paste(icon_image, (startX,startY+5))    

    #draw.rectangle((startX, startY+8, startX+50, startY+8+50), fill = 0)

    draw.text((startX+ 50 + 5, startY + 1), temperature + '\xb0', font=font24, fill=0)
    draw.text((startX+ 50 + 5, startY + 1 + 27 + 1), "UV: " + uv, font=fontSmall, fill=0)
    drawAQI(draw, startX+50+5, startY+1+26+1+20, font=fontSmall, station_code=450)


def drawWeather(draw, image):
    print("Drawing Weather")
    ## 18~2: show weather of next day
    tm_hour = time.localtime().tm_hour
    if (tm_hour >= 18 or tm_hour <=3):
        index = 1
    else:
        index = 0

    # Get default weather

    # Draw Forecast
    nextDay = False
    if (tm_hour >= 18):
        nextDay = True
    else:
        nextDay = False

    observation = owm.weather_at_place(CITY)
    w = observation.get_weather()

    nextDay = True
    if (nextDay == False):
        date_night = datetime.now().replace(hour=19, minute=0, second=0, microsecond=0)
        forecast = owm.three_hours_forecast(CITY).get_weather_at(date_night)
        tprt = w.get_temperature('celsius')
        high = str(int(tprt['temp_max']))
        low  = str(int(tprt['temp_min']))
        day_wea = w.get_status()
        night_wea = forecast.get_status()
        icon_day_wea = w.get_weather_icon_name()
        icon_night_wea = forecast.get_weather_icon_name()
    else:
        tmr_morning = pyowm.timeutils.tomorrow().replace(hour=9)
        tmr_night = pyowm.timeutils.tomorrow().replace(hour=19)
        tmr = pyowm.timeutils.tomorrow().replace(hour=0, minute=0, second=0, microsecond=0)
        tmr = tmr.replace(tzinfo=current_tz)
        tmrtmr = tmr + timedelta(days=1)
        forecast_m = owm.three_hours_forecast(CITY).get_weather_at(tmr_morning)
        forecast_n = owm.three_hours_forecast(CITY).get_weather_at(tmr_night)
        forecast = owm.three_hours_forecast(CITY).get_forecast().get_weathers()

        # Get the temperature of tmr from 3h data
        high = -60.0
        low = 60.0
        for i in forecast:
            time_f = i.get_reference_time('date')
            
            #time = utc.localize(time)
            #tmr = utc.localize(tmr)
            #tmrtmr = utc.localize(tmrtmr)
            if time_f >= tmr and time_f < tmrtmr:
                tprt = i.get_temperature('celsius')
                tmp_max = tprt['temp_max']
                tmp_min = tprt['temp_min']
                if TEST:
                    print(str(tmp_min))

                if tmp_max > high:
                    high = tmp_max
                if tmp_min < low:
                    low = tmp_min

        high = str(int(high))
        low  = str(int(low))
        day_wea = forecast_m.get_status()
        night_wea = forecast_n.get_status()
        icon_day_wea = forecast_m.get_weather_icon_name()
        icon_night_wea = forecast_n.get_weather_icon_name()

        # forecast = forecasts[index]
        # high =      forecast.get('high')
        # low =       forecast.get('low')
        # icon_night_wea =    forecast.get('night').get('icon')
        # icon_day_wea =      forecast.get('day').get('icon')
        '''
        date =      forecast.get('date')
        day_week =  forecast.get('day_of_week')
        night_wea = forecast.get('night').get('brief_text')
        day_wea =   forecast.get('day').get('brief_text')
        draw.text((10,5),  date, font=font24, fill=0)
        '''

    drawWeatherForecast(draw, image, icon_night_wea, icon_day_wea, high, low, nextDay)


    # Draw Current Weather

    currentIcon = w.get_weather_icon_name()
    temperature = str(int(w.get_temperature('celsius')['temp']))
    humidity = str(int(w.get_humidity()))
    uvi = owm.uvindex_around_coords(lat, lon)
    uv = str(int(uvi.get_value()))

    drawWeatherCurrent(draw, image, currentIcon, temperature, uv, humidity)

    return 0


def drawDateTime(draw, drawData=True, drawTime=True):
    textX = 5
    textY = 5
    if drawData == True:
        draw.rectangle((textX, textY, textX+60, textY+25), fill = 255)
        draw.text((textX, textY), time.strftime('%b %d'), font = fontMid, fill = 0)
    if drawTime == True:
        draw.rectangle((textX+90, textY, textX+90+50, textY+20), fill = 255)
        draw.text((textX+90, textY), time.strftime('%H:%M'), font = fontMid, fill = 0)

def clearImage(draw):
    draw.rectangle((0, 0, epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), fill = 255)





try:
    # Beijing Time
    os.environ['TZ'] = 'Asia/Shanghai'
    if not TEST:
        epd = epd2in13.EPD()

    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    # read bmp file on window
    '''
    print("read bmp file on window")
    epd.Clear(0xFF)
    image1 = Image.new('1', (epd2in13.EPD_WIDTH, epd2in13.EPD_HEIGHT), 255)  # 255: clear the frame
    bmp = Image.open('100x100.bmp')
    image1.paste(bmp, (10,10))    
    epd.display(epd.getbuffer(image1))
    time.sleep(2)
    # Drawing on the image
    image2 = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
    # read bmp file 
    print("read bmp file")
    epd.Clear(0xFF)
    image2 = Image.open('2in13.bmp')
    epd.display(epd.getbuffer(image2.rotate(180)))    
    
    print("Drawing")  
    epd.Clear(0xFF)    
    image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)    
    draw.rectangle([(0,0),(50,50)],outline = 0)
    draw.rectangle([(55,0),(100,50)],fill = 0)
    draw.line([(0,0),(50,50)], fill = 0,width = 1)
    draw.line([(0,50),(50,0)], fill = 0,width = 1)
    draw.chord((10, 60, 50, 100), 0, 360, fill = 0)
    draw.ellipse((55, 60, 95, 100), outline = 0)
    draw.pieslice((55, 60, 95, 100), 90, 180, outline = 0)
    draw.pieslice((55, 60, 95, 100), 270, 360, fill = 0)
    draw.polygon([(110,0),(110,50),(150,25)],outline = 0)
    draw.polygon([(190,0),(190,50),(150,25)],fill = 0)
    font15 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 15)
    draw.text((120, 60), 'e-Paper demo', font = font15, fill = 0)
    # draw.text((110, 80), 'Hello world', font = font15, fill = 0)
    epd.display(epd.getbuffer(image.rotate(180)))
    time.sleep(2)
    '''

    image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    # partial update
    print("Show time")
    # epd.init(epd.lut_partial_update)
    font24 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 24)
    fontMid = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 20)
    fontSmall = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 18)
    fontSmaller = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 16)
    # time_image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)

    # Draw Date only
    drawDateTime(draw, True, False)
    drawWeather(draw, image)
    
    firstTime = True

    #epd.Clear(0xFF)

    while (True):
        # Always Draw the time
        drawDateTime(draw, False, True)

        time_hour = time.localtime().tm_hour
        time_min = time.localtime().tm_min
        time_sec = time.localtime().tm_sec
        print("Time:"+str(time_hour)+":"+str(time_min)+":"+str(time_sec))
        if TEST:
            drawDateTime(draw, True, True)
            res = drawWeather(draw, image)
            imgplot = plt.imshow(image)
            plt.show()
        else:
            if time_min == 0 :
                clearImage(draw) #clear the frame

                # Draw date and time
                drawDateTime(draw, True, True)
                res = drawWeather(draw, image)
                if(res == 0 ):
                    epd.init(epd.lut_full_update)
                    #epd.Clear(0xFF)
                    epd.display(epd.getbuffer(image.rotate(180)))
                    print('Full update')
                else:
                    print('Full update Fail')
                    pass
                    
            else:
                if(firstTime == True):
                    epd.init(epd.lut_full_update)
                    firstTime = False
                    print('First Paint')
                else:
                    epd.init(epd.lut_partial_update)
                    print('Partically update')
                epd.display(epd.getbuffer(image.rotate(180)))



        # newimage = time_image.crop([10, 10, 120, 50])
        # time_image.paste(newimage, (10,10))  

        if not TEST:
            epd.sleep()
        print('sleep')
        time.sleep(60)

        
    # epd.sleep()
        
except:
    print( 'traceback.format_exc():\n%s',traceback.format_exc())
    if not TEST:
        epd.sleep()
    print('sleep')
    exit()

