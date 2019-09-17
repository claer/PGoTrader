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

from multiprocessing import Pool

def create_console_handler(verbose_level):
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)

    if verbose_level == 0:
        clog.setLevel(logging.WARN)
    elif verbose_level == 1:
        clog.setLevel(logging.INFO)
    else:
        clog.setLevel(logging.DEBUG)

    return clog

def scrap_screencap(dev, location):
    img = Image.open(BytesIO(dev.screencap()))
    crop = img.crop(config[dev.name]['locations'][location])
    return tool.image_to_string(crop).replace("\n", " ")

def tap(dev,location):
    x, y = config[dev.name]['locations'][location]
    dev.shell("input tap " + str(x) + " " + str(y))
    logger.info(dev.name + ' | Tap location ' + str(location) + 'succeeded')

def check_known_errors(dev):
    errors= [
        ("error_box",["est trop loin", "expiration", "inconnue"])
    ]
    for err_set in errors:
        box, msgs = err_set
        text = scrap_screencap(dev, box)
        for msg in msgs:
            if text in msg:
                raise Exception('Trade Error!')
    return

def waiting(location):
    time.sleep(config['waits'][location])

def clic_trade(dev):
    retries=5
    retry_interval=5
    for retry in range(retries):
        logger.info("Check and clic on trade button device {}".format(dev.name))
        if 'ECHANGER' in scrap_screencap(dev,"trade_button_label"):
            logger.info(dev.name + ' | TRADE button found')
            tap(dev,'trade_button')
            waiting('trade_button')
            return
        logger.warning(dev.name + ' | TRADE button not found, retrying ... ' + str(retry+1) + '/' + str(retries))
        time.sleep(retry_interval)
    raise Exception('Error Clic Trade {}'.format(dev.name))

def select_pokemon(dev):
    search_string = config[dev.name]['search_string']
    retries=5
    retry_interval=2
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
        elif 'pas disponible' in scrap_screencap(dev,"waiting_box"):
            logger.warning(dev.name + ' | Waiting screen detected, please wait ... ' + str(retry+1) + '/' +str(retries))
        logger.warning(dev.name + ' | Waiting screen not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(retry_interval)
    raise Exception('Trade Error!')

def check_screen(dev):
    name_check = config[dev.name]['name_check']
    retries=5
    retry_interval=2
    for retry in range(retries):
        logger.info("Check device {} NEXT screen".format(dev.name))
        if 'SUIVANT' in scrap_screencap(dev,"next_button_box"):
            logger.info(dev.name + ' | Next screen found')
            #if name_check not in scrap_screencap(dev,"name_at_next_screen_box"):
            #    raise namecheckfail
            tap(dev,'next_button')
            return
        logger.warning(dev.name + ' | Next screen not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(retry_interval)
    raise Exception('Trade Error!')

def confirm_screen(dev):
    retries=5
    retry_interval=2
    for retry in range(retries):
        logger.info("Check device {} CONFIRM screen".format(dev.name))
        if 'CONFIRMER' in scrap_screencap(dev,"confirm_button_box"):
            logger.info(dev.name + ' | Confirm screen found')
            tap(dev,'confirm_button')
            return
        logger.warning(dev.name + ' | Confirm screen not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(retry_interval)
    raise Exception('Trade Error!')

def trade_end(dev):
    retries=5
    retry_interval=2
    for retry in range(retries):
        logger.info("Check device {} trade ended".format(dev.name))
        weight_text = str(scrap_screencap(dev,"weight_box"))
        logger.debug('scap_weight: {}'.format(weight_text))
        if 'POIDS' in weight_text:
            logger.info(dev.name + ' | traded pokemon screen found')
            tap(dev,'close_pokemon_button')
            return
        weight_text = str(scrap_screencap(dev,"weight_box_lucky"))
        logger.debug('lucky scap_weight: {}'.format(weight_text))
        if 'POIDS' in weight_text:
            logger.warning('LUCKY Pokemon !!')
            logger.info(dev.name + ' | traded pokemon screen found')
            tap(dev,'close_pokemon_button')
            return
        logger.warning(dev.name + ' | Traded pokemon not found, retrying ... ' + str(retry+1) + '/' +str(retries))
        time.sleep(retry_interval)
    raise Exception('Trade Error!')

def do_trade(num):
    try:
        p = Pool(2)
        p.map(clic_trade, [dev_id1,dev_id2])
        p.map(select_pokemon, [dev_id1,dev_id2])
        waiting('next_button')

        p.map(check_screen, [dev_id1,dev_id2])
        waiting('confirm_button')

        p.map(confirm_screen, [dev_id1,dev_id2])
        waiting('trade_anim')

        p.map(trade_end, [dev_id1,dev_id2])
        waiting('trade_ends')

    except Exception as e:
        logger.error("ERROR: Canceling trade:" + str(e))
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

    verbose_level=1
    logger = logging.getLogger()
    if verbose_level > 0:
        logger.addHandler(create_console_handler(verbose_level))


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
        logger.warning("Trade num {}/{} engaged".format(str(trade+1),str(args.stop_after)))
        do_trade(trade)
