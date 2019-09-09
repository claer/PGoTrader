#!/usr/bin/env python3.7
import argparse
import time 
import logging
from colorlog import ColoredFormatter

from adb.client import Client as AdbClient

from PIL import Image
from io import BytesIO
from pyocr import pyocr
from pyocr import builders
import yaml

logger = logging.getLogger('trading')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = ColoredFormatter("  %(log_color)s%(levelname)-8s%(reset)s | %(log_color)s%(message)s%(reset)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

def scrap_screencap(dev, location):
    img = Image.open(BytesIO(dev.screencap()))
    crop = img.crop(config[dev.name]['locations'][location])
    return tool.image_to_string(crop).replace("\n", " ")

def tap(dev,location):
    x, y = config[dev.name]['locations'][location]
    dev.shell("input tap " + str(x) + " " + str(y))
    logger.info(dev.name + ' | Tap location ' + str(location) + 'succeeded')
    

def waiting(location):
    time.sleep(config['waits'][location])

def clic_trade(dev):
    retries=5
    for retry in range(retries):
        logger.info("Check and clic on trade button device {}".format(dev.name))
        if 'ECHANGER' in scrap_screencap(dev,"trade_button_label"):
            logger.info(dev.name + ' | TRADE button found')
            tap(dev,'trade_button')
            waiting('trade_button')
            return
        else:
            logger.warning(dev.name + ' | TRADE button not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(5)
    raise trade_error

def wait_for_trade(dev):
    retries=2
    for retry in range(retries):
        logger.info("Check device {} is waiting".format(dev.name))
        if 'pas disponible' in scrap_screencap(dev,"waiting_box"):
            logger.info(dev.name + ' | Waitign screen found')
            return
        else:
            logger.warning(dev.name + ' | Waiting screen not found, retrying ... ' str(retry+1) + '/' +str(retries))
        time.sleep(2)
    # do not raise error on waiting screen not found
    #raise wait_for_trade_error

def select_pokemon(dev):
    search_string = config[dev.name]['search_string']
    retries=5
    for retry in range(retries):
        logger.info("Check device {} Pokemon selection screen".format(dev.name))
        if 'POKEMON' in scrap_screencap(dev,"pokemon_to_trade_box"):
            logger.info(dev.name + ' | Selection screen found')
            tap(dev,'search_button')
            waiting('location')
            dev.shell("input text " + search_string)
            # tap 2 times the pokemon, once to get of keyboard entry, 2nd to select pokemon
            tap(dev,'first_pokemon')
            waiting('first_pokemon')
            tap(dev,'first_pokemon')
            return
        else:
            logger.warning(dev.name + ' | Waiting screen not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(5)
    raise wait_for_trade_error

def check_screen(dev):
    name_check = config[dev.name]['name_check']
    retries=5
    for retry in range(retries):
        logger.info("Check device {} NEXT screen".format(dev.name))
        if 'SUIVANT' in scrap_screencap(dev,"next_button_box"):
            logger.info(dev.name + ' | Next screen found')
            #if name_check not in scrap_screencap(dev,"name_at_next_screen_box"):
            #    raise namecheckfail
            tap(dev,'next_button')
            waiting('confirm_button')
            return
        else:
            logger.warning(dev.name + ' | Next screen not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(5)
    raise check_screen_error

def confirm_screen(dev):
    retries=5
    for retry in range(retries):
        logger.info("Check device {} CONFIRM screen".format(dev.name))
        if 'CONFIRMER' in scrap_screencap(dev,"confirm_button_box"):
            logger.info(dev.name + ' | Confirm screen found')
            tap(dev,'confirm_button')
            waiting('trade_anim')
            return
        else:
            logger.warning(dev.name + ' | Confirm screen not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(5)
    raise confirm_screen_error

def trade_end(dev):
    retries=5
    for retry in range(retries):
        logger.info("Check device {} trade ended".format(dev.name))
        if 'POIDS' in scrap_screencap(dev,"weight_box"):
            logger.info(dev.name + ' | traded pokemon screen found')
            tap(dev,'close_pokemon_button')
            waiting('trade_ends')
            return
        else:
            logger.warning(dev.name + ' | Traded pokemon not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(5)

def error_cases(dev):
    pass

def do_trade(num):
    logger.info("Trade num {} engaged".format(num))

    try:
        clic_trade(dev_id1)
        clic_trade(dev_id2)

        wait_for_trade(dev_id1)
        wait_for_trade(dev_id2)

        select_pokemon(dev_id1)
        select_pokemon(dev_id2)

        check_screen(dev_id1)
        check_screen(dev_id2)

        confirm_screen(dev_id1)
        confirm_screen(dev_id2)

        trade_end(dev_id1)
        trade_end(dev_id2)

    except e:
        logger.error("ERROR: Canceling trade:" + e)
        return False

    return True
        

if __name__ == '__main__':
    # get params from command line
    parser = argparse.ArgumentParser(description='Pokemon GO trader')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help="Config file location.")
    parser.add_argument('--stop-after', default=1, type=int,
                        help='Stop after exchanging <number> pokemon')
    args = parser.parse_args()

    # load params from config file
    with open(args.config, "r") as f:
        config = yaml.load(f)
    tools = pyocr.get_available_tools()
    tool = tools[0]

    # magic number for randomizing crop 
    i = 2

    # Connecting on local adb server
    try:
        client = AdbClient(host="127.0.0.1", port=5037)
    except:
        logger.error("Unable to connect to adb server")
        logger.error("Please check your configuration and run ``adb start-server''")
         
    if len(client.devices()) < 2:
        logger.error("This program needs 2 phones connected with ADB")
        
    # instanciate 2 pogo games
    dev_id1 = client.device(config['app1']['device_id'])
    dev_id1.name = 'app1'
    dev_id2 = client.device(config['app2']['device_id'])
    dev_id2.name = 'app2'


    # trading
    for trade in range(args.stop_after):
        do_trade(trade)
