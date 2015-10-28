#! /usr/bin/env python3
# -*- coding: utf-8 -*-

'''
usage:
    ts17 [-v|--version] [-h|--help]
    ts17 run [-d] [-o <repfile>] [-t <timelimit>] <ai> ...
    ts17 replay <repfile>

options:
    -h, --help     show this message
    -v, --version  show current version

    -d             enable debug mode, allow programmatically pause the game
    -o <repfile>   log to file, if file name is not specified, current time
                   will be used
    -t <timelimit> set the time limit of the game in seconds
'''

import argparse
import docopt
import queue
import sys
import time
import threading

import ai_proxy
import action
import core
#import core.interface
#import logger

__version__='0.1-a'

action_queue = queue.PriorityQueue()
game_start_time = 0
game_paused = False
game_pause_time = 0

def push_queue_ai_proxy(obj: action.Action):
    global action_queue
    global game_start_time
    timestamp=time.time() - game_start_time
    if(game_paused):
        timestamp = game_pause_time - game_start_time
    action_queue.put((timestamp, obj))

def main():
    args = docopt.docopt(__doc__, version='ts17-platform '+__version__+' [ts17-core ver '+core.__version__+']')
    print(args)
    if(args['run']):
        run_main(args)
    elif(args['replay']):
        replay_main(args)
    else:
        docopt.docopt(__doc__, argv=['-h'])

def run_main(args: dict):
    global action_queue
    global game_start_time

    last_action_timestamp = 0

    # init logic
    main_logic = core.interface.Interface()

    # init ai_proxy
    ai_proxy.start(args['<ai>'], push_queue_ai_proxy)

    # init ui
    #TODO

    # init logger
    #TODO

    game_started = True
    game_start_time = time.time()

    time_limit=0
    if(args['-t']):
        time_limit=int(args['-t'])
    # main loop
    while(game_started):
        next_action=action_queue.get(block=True)
        if (next_action[1].action_name == '_pause'):
            if (args['-d']):
                if(game_paused):
                    game_start_time += time.time() - game_pause_time
                    game_paused = False
                else:
                    game_pause_time = time.time()
                    game_paused = True
            else:
                print('illegal action: pause')
            continue
        elif (next_action[1].action_name == '_end'):
            if(next_action[1].forced or (not game_paused and time.time() - game_start_time > time_limit)):
                break;
        if (next_action[0] > last_action_timestamp):
            last_action_timestamp = next_action[0]
        if(last_action_timestamp > time_limit):
            break
        next_action[1].timestamp = last_action_timestamp
        if (next_action[1].action_name != 'query'):
            #logger.log(next_action[1])
            pass
        next_action[1].run(main_logic)
    ai_proxy.stopAI()

def replay_main(args: dict):
    pass

if (__name__=='__main__'):
    main()