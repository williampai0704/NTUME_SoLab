import pygame
import math
from math import exp
import matplotlib.pyplot as plt
from bezier import Bezier
from bezier import RPoint

class Car:
  w     = 2.4 #car width (m)
  l     = 4.8 #car length (m)
  gamma = 0.6
  lmda  = 1
  lmda2 = 1
  mode  = ['stand_by','lane_change']
  i = 0
  
  def __init__(self,lane,y,vel,acc,steerAngle):
    if lane == 'L':
      self.x = windowWidth/2 - meter2pixel(lineWidth/2+roadWidth/2) #pixel
    if lane == 'R':
      self.x = windowWidth/2 + meter2pixel(lineWidth/2+roadWidth/2)
      
    self.y = meter2pixel(y) #pixel
    self.y_ref = meter2pixel(y)
    self.x_tl = self.x-meter2pixel(carWidth)/2  # top left x
    self.y_tl = self.y-meter2pixel(carLength)/2 # top left y
    self.vel = meter2pixel(vel*1000/(10*3600)) # from km/hr --> pixel/fps
    self.steerAngle = steerAngle/180*math.pi
    self.lane = lane   
    self.acc = meter2pixel(acc)/10 #acceleration
    self.probList = [[] for i in range(4)]
    self.timeList = [[] for i in range(4)]
    self.timeList2 = [[] for i in range(4)]
    self.alpha1List = [[] for i in range(4)]
    self.alpha2List = [[] for i in range(4)]
    self.DList = [[] for i in range(4)]
    self.RList = [[] for i in range(4)]
    self.rList = [[] for i in range(4)]
    self.vList = [[] for i in range(4)]
    self.xList = [[] for i in range(4)]
    self.yList = [[] for i in range(4)]
    self.mode = 'stand_by'

  def drive(self,egoCar):
    self.vel += self.acc
    if self.mode == 'stand_by':
      self.x += self.vel*math.sin(self.steerAngle) # Real x(pixel)
      self.y -= self.vel*math.cos(self.steerAngle) # Real y(pixel)
    if self.mode == 'lane_change':
      self.i += int(self.vel/self.step)
      if (self.i >= len(self.b_x)):
        self.i = len(self.b_x)-1
        self.mode = 'stand_by'
      self.x = self.b_x[self.i]
      self.y = self.b_y[self.i]
    self.y_ref -= self.vel*math.cos(self.steerAngle)-egoCar.vel*math.cos(egoCar.steerAngle) # For relative view on screen
    self.x_tl = self.x-meter2pixel(carWidth)/2  #top left x
    self.y_tl = self.y_ref-meter2pixel(carLength)/2 #top left y
    for i in range(4):
      self.vList[i].append(self.vel)
      self.xList[i].append(pixel2meter(self.x))
      self.yList[i].append(pixel2meter(self.y))
      self.timeList2[i].append(pygame.time.get_ticks()/1000)
      
def cal_prob(eCar,TCar,i):
  eCar.D = pixel2meter(math.sqrt((eCar.x- TCar.x)**2+(eCar.y - TCar.y)**2))
  eCar.alpha1 = math.atan2(-(TCar.x-eCar.x),-(TCar.y-eCar.y)) #radius 
  eCar.alpha1_h = eCar.alpha1-eCar.steerAngle # angle between forward direction and target vehicle

  if (eCar.alpha1_h <= math.pi/2) & (eCar.alpha1_h >= -math.pi/2):
    eCar.R = math.sqrt((eCar.gamma*eCar.l*math.cos(eCar.alpha1_h))**2+(1/2*eCar.w*math.sin(eCar.alpha1_h))**2)
  else:
    eCar.R = math.sqrt(((1-eCar.gamma)*eCar.l*math.cos(eCar.alpha1_h))**2+(1/2*eCar.w*math.sin(eCar.alpha1_h))**2) 
  
  #Calculate alpha2 
  if TCar.lane == 'L':
    eCar.alpha2 = eCar.alpha1 - math.pi
  else: # 'R' or 0
    eCar.alpha2 = eCar.alpha1 + math.pi
  eCar.alpha2_h = eCar.alpha2-TCar.steerAngle # angle between forward direction and target vehicle
  
  if (eCar.alpha2_h <= math.pi/2) & (eCar.alpha2_h >= -math.pi/2):
    eCar.r = math.sqrt((eCar.gamma*eCar.l*math.cos(eCar.alpha2_h))**2+(1/2*eCar.w*math.sin(eCar.alpha2_h))**2)
  else:
    eCar.r = math.sqrt(((1-eCar.gamma)*eCar.l*math.cos(eCar.alpha2_h))**2+(1/2*eCar.w*math.sin(eCar.alpha2_h))**2) 
  
  #Calculate probability
  if eCar.D - eCar.R - eCar.r > 0:
    eCar.prob = eCar.lmda*exp(-eCar.lmda2*(eCar.D-eCar.R-eCar.r))
  else:
    eCar.prob = 1
  
  eCar.probList[i].append(eCar.prob)
  eCar.timeList[i].append(pygame.time.get_ticks()/1000)
  eCar.alpha1List[i].append(eCar.alpha1/math.pi*180)
  eCar.alpha2List[i].append(eCar.alpha2/math.pi*180)
  eCar.DList[i].append(eCar.D-eCar.R-eCar.r)
  eCar.RList[i].append(eCar.R)
  eCar.rList[i].append(eCar.r)
  
def plot_prob(TCar,i):
  # plt.subplot(331)
  # plt.plot(TCar.timeList[i],TCar.probList[i])
  # plt.subplot(332)
  # # plt.plot(TCar.timeList[i],TCar.alpha1List[i])
  # # plt.subplot(333)
  # # plt.plot(TCar.timeList[i],TCar.alpha2List[i])
  # # plt.subplot(334)
  # # plt.plot(TCar.timeList[i],TCar.DList[i])
  # # plt.subplot(335)
  # # plt.plot(TCar.timeList[i],TCar.RList[i])
  # plt.subplot(336)
  # plt.plot(TCar.timeList[i],TCar.rList[i])
  # plt.subplot(337)
  # plt.plot(TCar.timeList2[i],TCar.yList[i])
  # plt.subplot(338)
  plt.plot(TCar.xList[i],TCar.yList[i])
  plt.xlim(0, 10)
  ax = plt.gca()
  ax.set_aspect('equal', adjustable='box')
  plt.show()
  

def meter2pixel(m):
  return m*20
def pixel2meter(p):
  return p/20

def drawRoad():
  tW = meter2pixel(totalWidth)
  lW = meter2pixel(lineWidth)
  
  road = pygame.Rect(0,0,tW,windowLength)
  line = pygame.Rect(0,0,lW,windowLength)
  road.center = (windowWidth/2,windowLength/2)
  line.center = (windowWidth/2,windowLength/2)
  screen.fill([0,0,0])
  pygame.draw.rect(screen,'gray70',road)
  pygame.draw.rect(screen,'yellow',line)
 
#=================================================================================== 

#Length Parameter 
windowWidth  = 300 #pixel
windowLength = 800
carWidth     = 2.4 #m
carLength    = 4.8
totalWidth   = 8 #m
roadWidth    = 3.9 
lineWidth    = 0.2
lineLength   = 4
lineSpace    = 6

pygame.init()
screen = pygame.display.set_mode((windowWidth,windowLength))
pygame.display.set_caption("SoLab")
whiteCar = pygame.image.load('pics/white_car.png')
redCar = pygame.image.load('pics/red_car.png')
whiteCar = pygame.transform.scale(whiteCar, (meter2pixel(carLength), meter2pixel(carWidth)))
whiteCar = pygame.transform.rotate(whiteCar, 90)
redCar = pygame.transform.scale(redCar,(meter2pixel(carLength), meter2pixel(carWidth)))
redCar = pygame.transform.rotate(redCar, 90)
clock = pygame.time.Clock()

egoCar = Car('R',20,80,0,0)
LFCar  = Car('L',5,81,0,0)
FCar   = Car('R',10,75,0,0)
LRCar  = Car('L',35,80,0,0)
RCar   = Car('R',35,80,0,0)
start_lane_change = False


def refreshScreen():
  drawRoad()
  cal_prob(egoCar,LFCar,0)
  cal_prob(egoCar,FCar,1)
  car_move()
  screen.blit(whiteCar,(egoCar.x_tl,egoCar.y_tl))
  screen.blit(redCar,(LFCar.x_tl,LFCar.y_tl))
  screen.blit(redCar,(FCar.x_tl,FCar.y_tl))
  screen.blit(redCar,(RCar.x_tl,RCar.y_tl))
  screen.blit(redCar,(LRCar.x_tl,LRCar.y_tl))
  pygame.display.update()

def car_move():
  global start_lane_change
  if(egoCar.probList[1][-1] >= 0.2 and start_lane_change == 0):
    egoCar.mode = 'lane_change'
    p1 = RPoint(egoCar.x,egoCar.y)
    p2 = RPoint(egoCar.x,egoCar.y-meter2pixel(5))
    p3 = RPoint(egoCar.x-meter2pixel(4),egoCar.y-meter2pixel(10))
    p4 = RPoint(egoCar.x-meter2pixel(4),egoCar.y-meter2pixel(15))
    egoCar.step , egoCar.b_x, egoCar.b_y = Bezier(p1,p2,p3,p4)
    start_lane_change = 1
    
  egoCar.drive(egoCar) # Relative coordinate 
  LFCar.drive(egoCar)
  FCar.drive(egoCar)
  LRCar.drive(egoCar)
  RCar.drive(egoCar)
  

def main():
  running = True
  while running:
    clock.tick(10)
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        running = False
    # keys = pygame.key.get_pressed()
    refreshScreen()
      
  # plot_prob(egoCar,0)
  plot_prob(egoCar,1)
  
  pygame.quit()

if __name__ == '__main__':
    main()