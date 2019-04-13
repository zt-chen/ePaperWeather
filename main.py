#!/usr/bin/python3
# -*- coding:utf-8 -*-

import epd2in13
import time
from PIL import Image,ImageDraw,ImageFont, ImageOps
import traceback
import pywapi
import os
def drawWeatherForecast(image, icon_night_wea, icon_day_wea, high, low, nextDay=0):
    print("Drawing Forecast")
    draw = ImageDraw.Draw(image)
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
    draw.text((forecastX+5,forecastY), 'Day', font=fontSmall, fill=0)
    if(len(icon_day_wea) ==2):
        icon_image_day = Image.open('./weatherIcons/'+icon_day_wea+'.bmp').resize((30,30))
        image.paste(icon_image_day, (forecastX+10,forecastY+25))    

    draw.text((forecastX+45,forecastY), 'Night', font=fontSmall, fill=0)
    if(len(icon_night_wea) == 2):
        icon_image_night = Image.open('./weatherIcons/'+icon_night_wea+'.bmp').resize((30,30))
        image.paste(icon_image_night, (forecastX+45+10,forecastY+25))    

    # Draw forecast temperature
    draw.text((forecastX+15,forecastY+30+32),  low + '\xb0 ~ ' + high + '\xb0', font=fontSmall, fill=0)

def drawWeatherCurrent(image, icon, temperature, uv, humidity):
    print("Drawing Current")
    startX = 5
    startY = 5+25 + 5

    draw = ImageDraw.Draw(image)

    if(len(icon) == 2):
        icon_image = Image.open('./weatherIcons/'+icon+'.bmp').resize((50,50))
        image.paste(icon_image, (startX,startY))    

    #draw.rectangle((startX, startY, startX+50, startY+50), fill = 0)

    draw.text((startX+ 50 + 5, startY + 2), temperature + '\xb0', font=font24, fill=0)
    draw.text((startX+ 50 + 5, startY + 2 + 30 + 2), "UV: " + uv, font=fontSmall, fill=0)


def drawWeather(image):
    print("Drawing Weather")
    ## 18~2: show weather of next day
    tm_hour = time.localtime().tm_hour
    if (tm_hour >= 18 or tm_hour <=2):
        index = 1
    else:
        index = 0

    draw = ImageDraw.Draw(image)
    # Get default weather
    #res = pywapi.get_weather_from_weather_com('UKXX8845', 'metric')
    res = pywapi.get_weather_from_weather_com('CHXX0008', 'metric')

    # Draw Forecast
    forecasts = res.get('forecasts')
    if forecasts != None and (len(forecasts) > (index + 1)):
        forecast = forecasts[index]
        high =      forecast.get('high')
        low =       forecast.get('low')
        icon_night_wea =    forecast.get('night').get('icon')
        icon_day_wea =      forecast.get('day').get('icon')
        '''
        date =      forecast.get('date')
        day_week =  forecast.get('day_of_week')
        night_wea = forecast.get('night').get('brief_text')
        day_wea =   forecast.get('day').get('brief_text')
        draw.text((10,5),  date, font=font24, fill=0)
        '''
        drawWeatherForecast(image, icon_night_wea, icon_day_wea, high, low, index)
    else:
        return 1

    # Draw Current Weather
    current = res.get('current_conditions')
    if current != None:
        currentIcon = current.get('icon')
        temperature = current.get('temperature')
        humidity    = current.get('humidity')
        uv          = current.get('uv').get('text')

        drawWeatherCurrent(image, currentIcon, temperature, uv, humidity)

    else:
        return 1

    return 0


def drawDateTime(image, drawData=True, drawTime=True):
    textX = 5
    textY = 5
    draw = ImageDraw.Draw(image)
    if drawData == True:
        draw.rectangle((textX, textY, textX+60, textY+25), fill = 255)
        draw.text((textX, textY), time.strftime('%b %d'), font = fontMid, fill = 0)
    if drawTime == True:
        draw.rectangle((textX+90, textY, textX+90+50, textY+20), fill = 255)
        draw.text((textX+90, textY), time.strftime('%H:%M'), font = fontMid, fill = 0)



try:
    # Beijing Time
    os.environ['TZ'] = 'Asia/Shanghai'
    epd = epd2in13.EPD()

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
    # partial update
    print("Show time")
    # epd.init(epd.lut_partial_update)
    font24 = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 24)
    fontMid = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 20)
    fontSmall = ImageFont.truetype('/usr/share/fonts/truetype/wqy/wqy-microhei.ttc', 18)
    # time_image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)

    # Draw Date only
    drawDateTime(image, True, False)
    drawWeather(image)


    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)

    while (True):
        # Always Draw the time
        drawDateTime(image, False, True)

        draw = ImageDraw.Draw(image)

        time_hour = time.localtime().tm_hour
        time_min = time.localtime().tm_min
        time_sec = time.localtime().tm_sec
        print("Time:"+str(time_hour)+":"+str(time_min)+":"+str(time_sec))
        
        if time_min == 0 :
            image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame

            # Draw date and time
            drawDateTime(image, False, True)
            res = drawWeather(image)
            if(res == 0 ):
                epd.init(epd.lut_full_update)
                epd.Clear(0xFF)
                epd.display(epd.getbuffer(image.rotate(180)))
                print('Full update')
            else:
                print('Full update Fail')
                pass
                
        else:
            epd.init(epd.lut_partial_update)
            epd.display(epd.getbuffer(image.rotate(180)))
            print('Partically update')


        # newimage = time_image.crop([10, 10, 120, 50])
        # time_image.paste(newimage, (10,10))  
        epd.sleep()
        print('sleep')
        time.sleep(60)

        
    # epd.sleep()
        
except:
    print( 'traceback.format_exc():\n%s',traceback.format_exc())
    epd.sleep()
    print('sleep')
    exit()

