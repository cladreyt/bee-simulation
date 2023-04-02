from pylab import *
import random

from typing_extensions import TypeVarTuple
class Bee():
  def __init__(self, pos, beetype):
    self.pos = pos
    self.pollen = 0
    self.beetype = beetype  # 'Forager' or 'Scout'
    self.flower_loc = None
    self.reached_dest = False
    self.availiable = True
    
  def move_to_destination(self, dest):
    if(self.pos[1] > dest[1]):
      self.pos[1] += -1
    elif(self.pos[1] < dest[1]):
      self.pos[1] += 1
    
    if(self.pos[0] > dest[0]):
      self.pos[0] += -1
    elif(self.pos[0] < dest[0]):
      self.pos[0] += 1
       
  def random_walk(self, dims):
    self.pos[0] += randint(-1,2)
    self.pos[1] += randint(-1,2)
    self.pos[0] = self.boundary_behavior(self.pos[0], 0, dims - 1)
    self.pos[1] = self.boundary_behavior(self.pos[1], 0, dims - 1)
  
  def boundary_behavior(self, p, pmin, pmax):
    if p < pmin: return pmin
    elif p > pmax: return pmax
    else: return p

  # Called after every Scout random walk
  def pickup_pollen(self, enviro, hive):
    if enviro.grid[self.pos[0]][self.pos[1]] == 1 and self.pos != hive.pos:
      self.pollen += 1
      enviro.grid[self.pos[0]][self.pos[1]] = 0
      if self.beetype == "Scout":
        tempx = self.pos[0]
        tempy = self.pos[1]
        temploc = [tempx, tempy]
        self.flower_loc = temploc

class Hive():
  def __init__(self, dims):
    self.pos = [int(dims / 2), int(dims / 2)]
    self.pollen_count = []
    self.pollen_count_var = 0

  def return_bee(self, bee, agents):
    self.pollen_count_var += bee.pollen
    self.pollen_count.append(self.pollen_count_var)
    bee.pollen = 0
    if (bee.beetype == 'Forager'):
      # set foragers location to none
      bee.flower_loc = None
      bee.reached_dest = False
      bee.availiable = True
    if (bee.beetype == 'Scout'):
      temp_loc = bee.flower_loc
      # send a forager to go get that pollen!
      self.get_forager(temp_loc, agents)
      bee.flower_loc = None

  # takes destination and gives it to a forager
  def get_forager(self, dest, agents):
    for ag in agents:
      if ag.beetype == "Forager" and ag.availiable == True:
        ag.availiable = False
        ag.flower_loc = dest
        break
        
class Environment():
  def __init__(self, dims):
    self.grid = []  # grid is a 2-d list containing ints representing pollen levels
    self.dims = dims
    for row in range(dims): # initialize grid with zeros
      temp = []
      for col in range(dims):
        temp.append(0)
      self.grid.append(temp)
    cluster_positions = []  # holds location of top left corner of flower cluster
    while len(cluster_positions) < 3:
      x_pos = randint(0, dims - 6)
      y_pos = randint(0, dims - 6)
      # make sure we don't spawn on the hive
      if (x_pos < (dims / 2) - 3 or x_pos > (dims / 2) + 3) and (y_pos < (dims / 2) - 3 or y_pos > (dims / 2) + 3):
        cluster_positions.append((x_pos, y_pos))
    # go through the cluster positions and set the 0's to 1's
    for cluster in cluster_positions:
      for x in range(5):
        for y in range(5):
          self.grid[cluster[0]+x][cluster[1]+y] = 1
  
  def initialize():
  global enviro, agents, hive, time_history
  time_history = 0

  dims = 50
  
  num_scouts = 10
  num_foragers = 10
  
  hive = Hive(dims)
  enviro = Environment(dims)
  # holds all scout and forager bees
  agents = []
  for i in range(0, num_scouts):
    pos = [randint(dims), randint(dims)]
    agents.append(Bee(pos, 'Scout'))
  for i in range(0, num_foragers):
    pos = [25,25]
    agents.append(Bee(pos, 'Forager'))

def update():
  global enviro, agents, time_history
  time_history += 1
  for ag in agents:
    # Agent is Scout
    if ag.beetype == 'Scout':
      if ag.pollen > 0:
        # Agent is carrying
        if ag.pos == hive.pos:  # check if scount is back at the hive
          hive.return_bee(ag, agents)  # recruit foragers, if any there
        else:  # not at the hive
          ag.move_to_destination(hive.pos)
      else:  # scout doesn't have pollen, random walk
        ag.pickup_pollen(enviro,hive)
        ag.random_walk(enviro.dims)
    else:
      # Agent is Forager
      if ag.flower_loc is not None:  #  We are searching
        if ag.reached_dest == False:  # move to the destination
          ag.move_to_destination(ag.flower_loc)
          if(ag.pos == ag.flower_loc):  # we have made it to the flower cluster
            ag.reached_dest = True
        else: # We have reached the destination
          if ag.pollen == 2:  # 
            if ag.pos == hive.pos:  # we have made it back to hive, return bee
              hive.return_bee(ag, agents)
            else:
              ag.move_to_destination(hive.pos)
          else:  # we have less than 2 pollen
            ag.pickup_pollen(enviro,hive)
            ag.random_walk(enviro.dims)

def observe():
  cla()
  imshow(enviro.grid, cmap = 'Blues', vmin = -1, vmax = 1)
  axis('image')
  #scatter([bee.pos[0] for bee in agents], [bee.pos[1] for bee in agents], c = 'black')
  scatter([bee.pos[1] for bee in agents if bee.beetype == "Scout"], [bee.pos[0] for bee in agents if bee.beetype == "Scout"], c = 'black')
  scatter([bee.pos[1] for bee in agents if bee.beetype == "Forager"], [bee.pos[0] for bee in agents if bee.beetype == "Forager"], c = 'green')
  title('t = ' + str(time_history))
  show()

def observe_stats(pollen_history):
  plt.plot(pollen_history, label = 'Pollen Count')
  plt.legend()
  plt.show()
  
  
  
import IPython.display as display
import time

T = 500
pollen_history = []

initialize()

for t in range(T):
  update()
  pollen_history.append(hive.pollen_count_var)
  time.sleep(0.2)
  display.clear_output(wait=True)
  observe()
observe_stats(pollen_history)
