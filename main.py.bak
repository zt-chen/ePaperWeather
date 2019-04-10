#!/usr/bin/python
# -*- coding:utf-8 -*-

import epd2in13
import time
from PIL import Image,ImageDraw,ImageFont, ImageOps
import traceback
import pywapi

try:
    epd = epd2in13.EPD()
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)

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
    # time_image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
    draw = ImageDraw.Draw(image)

    # Get default weather
    res = pywapi.get_weather_from_weather_com('UKXX8845', 'metric')
    high = res.get('forecasts')[0].get('high')
    low = res.get('forecasts')[0].get('low')
    night_wea = res.get('forecasts')[0].get('night').get('brief_text')
    day_wea = res.get('forecasts')[0].get('day').get('brief_text')
    icon_night_wea = res.get('forecasts')[0].get('night').get('icon')
    icon_day_wea = res.get('forecasts')[0].get('day').get('icon')
    date = res.get('forecasts')[0].get('date')
    day_week = res.get('forecasts')[0].get('day_of_week')

    draw.text((10,5),  date, font=font24, fill=0)
    draw.text((10,35),  'Low: '+low + ' High: ' + high, font=font24, fill=0)
    draw.text((10,65), "Day: " + day_wea , font=font24, fill=0)
    draw.text((120,65), 'Night: ' + night_wea, font=font24, fill=0)
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)

    icon_image_day = Image.open('./weatherIcons/00.bmp').resize((40,40))
    image.paste(icon_image_day, (70,75))    
    image.paste(icon_image_day, (200,75))    
    '''
    if(len(icon_day_wea)!=0):
        icon_image_day = Image.open('./weatherIcons/'+icon_day_wea+'.bmp').resize((40,40))
        image.paste(icon_image_day, (10,65))    

    if(len(icon_night_wea)!= 0):
        icon_image_night = Image.open('./weatherIcons/'+icon_night_wea+'.bmp').resize((40,40))
        image.paste(icon_image_night, (70,65))    
'''
    while (True):

        # Always Draw the time
        draw.rectangle((180, 5, 250, 35), fill = 255)
        draw.text((180, 5), time.strftime('%H:%M'), font = font24, fill = 0)
        time_hour = time.localtime().tm_hour
        time_min = time.localtime().tm_min
        time_sec = time.localtime().tm_sec
        print("Time:"+str(time_min)+str(time_sec))
        
        if time_min == 0 :
            epd.init(epd.lut_full_update)
            epd.Clear(0xFF)

            image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)  # 255: clear the frame
            draw = ImageDraw.Draw(image)
            # Get weather from weather api
            res = pywapi.get_weather_from_weather_com('UKXX8845', 'metric')
            if len(res) > 0:
                high = res.get('forecasts')[0].get('high')
                low = res.get('forecasts')[0].get('low')
                night_wea = res.get('forecasts')[0].get('night').get('brief_text')
                day_wea = res.get('forecasts')[0].get('day').get('brief_text')
                icon_night_wea = res.get('forecasts')[0].get('night').get('icon')
                icon_day_wea = res.get('forecasts')[0].get('day').get('icon')
                date = res.get('forecasts')[0].get('date')
                day_week = res.get('forecasts')[0].get('day_of_week')
                # Draw Weather
            draw.text((10,5),  date , font=font24, fill=0)
            draw.text((10,35),  'Low: '+low + ' High: ' + high, font=font24, fill=0)
            draw.text((10,66), "Day: " + day_wea , font=font24, fill=0)
            draw.text((10,95), 'Night: ' + night_wea, font=font24, fill=0)
            print('Full update')
        else:
            epd.init(epd.lut_partial_update)
            print('Partically update')



        # newimage = time_image.crop([10, 10, 120, 50])
        # time_image.paste(newimage, (10,10))  
        epd.display(epd.getbuffer(image.rotate(180)))
        epd.sleep()
        print('sleep')
        time.sleep(60)

        
    # epd.sleep()
        
except:
    print( 'traceback.format_exc():\n%s',traceback.format_exc())
    epd.sleep()
    print('sleep')
    exit()

