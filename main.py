
# Copyright 2020 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import math
import ast
import json
import random
#from "./player.py" import Player
from flask import Flask, request
from numpy import ndarray, zeros
from numpy import concatenate
compassmap = {
"N":(0,1),
"E":(1,0),
"S":(0,-1),
"W":(-1,0)
}

class Player:

    def __init__(self,url):
        self.url = url
        self.danger = 0
        self.x_pos = None
        self.y_pos = None
        self.command = None
        return

    def update_state(self, arena_in):
        self.danger = 0
        arena = zeros((arena_in["dims"][0]+3,arena_in["dims"][1]+3),dtype=int)
        for e in arena_in["state"]:
            if e != self.url:
            #Assign weights to the arena array to determine danger zones
                print(arena_in["state"][e])
                arena[arena_in["state"][e]["x"],arena_in["state"][e]["y"]] = 1
                
                if arena_in["state"][e]["direction"] == "N":
                    #arena = concatenate(arena[arena_in["state"][e]["x"],arena_in["state"][e]["y"]],arena[arena_in["state"][e]["x"],arena_in["state"][e]["y"]+3])
                    
                    arena[:,arena_in["state"][e]["y"]:(arena_in["state"][e]["y"]+3)] = -1
                elif arena_in["state"][e]["direction"] == "S":
                    arena[:,arena_in["state"][e]["y"]:(arena_in["state"][e]["y"]-3)] = -1
                

                elif arena_in["state"][e]["direction"] == "E":
                    arena[arena_in["state"][e]["x"]:(arena_in["state"][e]["x"]+3),:] = -1
                   

                elif arena_in["state"][e]["direction"] == "W":
                    arena[arena_in["state"][e]["x"]:(arena_in["state"][e]["x"]-3),:] = -1
                    
            else:
                self.x_pos = arena_in["state"][e]["x"]
                self.y_pos = arena_in["state"][e]["y"]
                self.bearing = arena_in["state"][e]["direction"]
        self.arena = arena

    def analyse_state(self):
        #first, check to see if current position is safe

        if self.arena[self.x_pos][self.y_pos] < 0:
            self.danger += 1
        if 1 in self.arena[self.x_pos:self.x_pos+(compassmap[self.bearing][0]*3)] [self.y_pos:self.y_pos+(compassmap[self.bearing][1]*3)] >= 0:
            #there is an enemy within range! fire!...if you're not encircled.
            self.danger -= 1
        if self.danger > 0:
            #need to move! check if we can just move forward to be safe
            if self.arena[self.x_pos+compassmap[self.bearing][0]] [self.y_pos+compassmap[self.bearing][1]] >= 0:
                #safe to move forward
                self.command = "F"
                self.x_pos += compassmap[self.bearing][0]
                self.y_pos += compassmap[self.bearing][1]
            else:
                logger.warn("Danger level:"+str(self.danger))
                #not safe, turn to move toward centre of arena
                if self.x_pos > 2+math.floor(self.arena.shape[0]/2):
                    logger.info("go west" +str(math.floor(self.arena.shape[0]/2)))
                    #send turn message
                    #self.bearing = "W"
                    if self.bearing == "W":
                        self.command = "F"
                    elif self.bearing == "S":
                        self.command = "R"
                    else:
                        self.command = "L"
                elif self.x_pos < 2+math.floor(self.arena.shape[0]/2):
                    logger.info("go east" +str(math.floor(self.arena.shape[0]/2)))
                    if self.bearing == "E":
                        self.command = "F"
                    elif self.bearing == "N":
                        self.command = "R"
                    else:
                        self.command ="L"
                elif self.y_pos < 2+math.floor(self.arena.shape[1]/2):
                    logger.info("go south" +str(math.floor(self.arena.shape[1]/2)))
                    if self.bearing == "S":
                        self.command = "F"
                    elif self.bearing == "E":
                        self.command = "R"
                    else:
                        self.command = "L"
                else:
                    logger.info("go north" +str(math.floor(self.arena.shape[1]/2)))
                    if self.bearing == "N":
                        self.command = "F"
                    elif self.bearing == "W":
                        self.command = "R"
                    else:
                        self.command = "L"
                    
        else:
            self.command = "T"
            #yolo, shoot your shot
            
        return self.command
    def get_command(self):
        return self.command



logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
logger = logging.getLogger(__name__)
player = Player("https://cloud-run-hackathon-python-scbpckg2va-uc.a.run.app")

app = Flask(__name__)
moves = ['F', 'T', 'L', 'R']




@app.route("/", methods=['GET'])
def index():
    return "Let the battle begin!"

@app.route("/", methods=['POST'])
def move():
    b = request.get_data()
    d = json.loads(b.decode('UTF-8'))
    player.update_state(d["arena"])
    player.analyse_state()
    logger.info("Action:"+player.get_command())
    return player.get_command()

if __name__ == "__main__":
   
    app.run(debug=False,host='0.0.0.0',port=int(os.environ.get('PORT', 8080)))
  
