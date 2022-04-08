from numpy import ndarray as matrix
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
        return

    def update_state(self, arena):
        arena = matrix(arena["dims"][0],arena["dims"][1],dtype=int).fill(0)
        for e in self.arena_state:
            if e != self.url:
            #Assign weights to the arena array to determine danger zones
               arena[e["x"],e["y"]] = 1
               if e["direction"] == "N":
                   arena = numpy.concatenate(arena[e["x"],e["y"]],[-1],arena[e["x"],e["y"]+3])
               elif e["direction"] == "S":
                   arena = numpy.concatenate(arena[e["x"],e["y"]],[-1],arena[e["x"],e["y"]-3])

               elif e["direction"] == "E":
                   arena = numpy.concatenate(arena[e["x"],e["y"]],[-1],arena[e["x"]+3,e["y"]])

               elif e["direction"] == "W":
                   arena = numpy.concatenate(arena[e["x"],e["y"]],[-1],arena[e["x"]-3,e["y"]])
            else:
                self.x_pos = e["x"]
                self.y_pos = e["y"]
                self.bearing = e["direction"]
        self.arena = arena
    def analyse_state(self):
        #first, check to see if current position is safe
        if self.arena[self.x_pos,self.y_pos] < 0:
            self.danger += 1
        if 1 in self.arena[self.x_pos:self.x_pos+(compassmap[self.bearing][0]*3), self.y_pos:self.y_pos+(compassmap[self.bearing][1]*3)] >= 0:
            #there is an enemy within range! fire!...if you're not encircled.
            self.danger -= 1
        if self.danger > 0:
            #need to move! check if we can just move forward to be safe
            if self.arena[self.x_pos+compassmap[self.bearing][0], self.y_pos+compassmap[self.bearing][1]] >= 0:
                #safe to move forward
                self.command = "MOVE"
                self.x_pos += compassmap[self.bearing][0]
                self.y_pos += compassmap[self.bearing][1]
            else:
                #not safe, turn to move toward centre of arena
                if self.x_pos > 2+(self.arena.ndim[0]/2):
                    #send turn message
                    #self.bearing = "W"
                    if self.bearing == "S":
                        self.command = "R"
                    else:
                        self.command = "L"
                elif self.x_pos < 2+(self.arena.ndim[0]/2):
                    #self.bearing = "E"
                    if self.bearing == "N":
                        self.command = "R"
                    else:
                        self.command ="L"
                elif self.y_pos > 2+(self.arena.ndim[1]/2):
                    #self.bearing = "S"
                    if self.bearing == "E":
                        self.command = "R"
                    else:
                        self.command = "L"
                else:
                    #self.bearing = "N"
                    if self.bearing == "W":
                        self.command = "R"
                    else:
                        self.command = "L"
                    
        else:
            self.command = "FIRE"
            #yolo, shoot your shot
            
        return
