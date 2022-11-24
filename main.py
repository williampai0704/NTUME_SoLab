import pygame
import math
from math import exp
import matplotlib.pyplot as plt
from bezier import Bezier
from bezier import RPoint
from velocityProfile import velocityProfile

class Car:
  w     = 2.4 #car width (m)
  l     = 4.8 #car length (m)
  gamma = 0.6
  lmda  = 1
  lmda2 = 1
  mode  = ['stand_by','lane_change']
  i = 0
  
  def __init__(self,lane,y,vel,steerAngle,isFront):
    if lane == 'L':
      self.x = windowWidth/2 - meter2pixel(lineWidth/2+roadWidth/2) #pixel
    if lane == 'R':
      self.x = windowWidth/2 + meter2pixel(lineWidth/2+roadWidth/2)
      
    self.y = meter2pixel(y) #pixel
    self.y_ref = meter2pixel(y)
    self.x_tl = self.x-meter2pixel(carWidth)/2  # top left x
    self.y_tl = self.y-meter2pixel(carLength)/2 # top left y
    self.vel = km_hr2pixel_fps(vel) # from km/hr --> pixel/fps
    self.vel2 = vel
    self.vel_ideal = vel
    self.steerAngle = steerAngle/180*math.pi
    self.lane = lane   
    # self.acc = meter2pixel(acc)/10 #acceleration
    self.probList   = [[] for i in range(4)]
    self.timeList   = [[] for i in range(4)]
    self.timeList2  = [[] for i in range(4)]
    self.alpha1List = [[] for i in range(4)]
    self.alpha2List = [[] for i in range(4)]
    self.DList      = [[] for i in range(4)]
    self.RList      = [[] for i in range(4)]
    self.rList      = [[] for i in range(4)]
    self.vList      = [[] for i in range(4)]
    self.xList      = [[] for i in range(4)]
    self.yList      = [[] for i in range(4)]
    self.mode = 'stand_by'
    self.isFront = isFront

  def drive(self,egoCar):
    global lane_changing
    global finish_lane_change
    global start_lane_change
    # self.vel += self.acc
    if not self.isFront:
      if not start_lane_change:
        self.vel = km_hr2pixel_fps(velocityProfile(self.probList[1][-1],self.vel_ideal))
      if lane_changing:
        self.vel = km_hr2pixel_fps(velocityProfile(self.probList[2][-1],self.vel_ideal))
      if finish_lane_change:
        self.vel = km_hr2pixel_fps(velocityProfile(self.probList[0][-1],self.vel_ideal))
        
    if self.mode == 'stand_by':
      self.steerAngle = 0
      self.x += self.vel*math.sin(self.steerAngle) # Real x(pixel)
      self.y -= self.vel*math.cos(self.steerAngle) # Real y(pixel)
    if self.mode == 'lane_change':
      self.i += int(self.vel/self.step)
      if (self.i >= len(self.b_x)):
        self.i = len(self.b_x)-1
        self.mode = 'stand_by'
        print("back to stand by")
        finish_lane_change = True
        lane_changing = False
      self.x = self.b_x[self.i]
      self.y = self.b_y[self.i]
      self.steerAngle = self.b_alpha1[self.i]
    
    self.y_ref -= self.vel*math.cos(self.steerAngle)-egoCar.vel*math.cos(egoCar.steerAngle) # For relative view on screen
    self.x_tl = self.x-meter2pixel(carWidth)/2  #top left x
    self.y_tl = self.y_ref-meter2pixel(carLength)/2 #top left y
    for i in range(4):
      self.vList[i].append(pixel_fps2km_hr(self.vel))
      self.xList[i].append(pixel2meter(self.x))
      self.yList[i].append(pixel2meter(self.y))
      self.timeList2[i].append(pygame.time.get_ticks()/1000)
      
def cal_prob(eCar,TCar,i):
  eCar.D        = pixel2meter(math.sqrt((eCar.x- TCar.x)**2+(eCar.y - TCar.y)**2))
  eCar.alpha1   = math.atan2(-(TCar.x-eCar.x),-(TCar.y-eCar.y)) #radius 
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
  
  eCar.lmda2 = 0.5 - ((eCar.vel-80)/80)
  print(eCar.lmda2)
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
  
def plot1(TCar,i):
  plt.subplot(121)
  plt.plot(TCar.timeList[i],TCar.probList[i])
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
  plt.subplot(122)
  plt.plot(TCar.xList[i],TCar.yList[i])
  plt.xlim(0, 10)
  ax = plt.gca()
  ax.set_aspect('equal', adjustable='box')
  plt.show()

def plotv(TCar,i=1):
  plt.plot(TCar.timeList2[i],TCar.vList[i])
  # plt.subplot(338)
  plt.show()
  

def meter2pixel(m):
  return m*20
def pixel2meter(p):
  return p/20
def km_hr2pixel_fps(v):
  return meter2pixel(v*1000/(10*3600))
def pixel_fps2km_hr(p):
  return pixel2meter(p/1000*3600*10)

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
blueCar = pygame.image.load('pics/blue_car.png')
whiteCar = pygame.transform.scale(whiteCar, (meter2pixel(carLength), meter2pixel(carWidth)))
whiteCar = pygame.transform.rotate(whiteCar, 90)
redCar = pygame.transform.scale(redCar,(meter2pixel(carLength), meter2pixel(carWidth)))
redCar = pygame.transform.rotate(redCar, 90)
blueCar = pygame.transform.scale(blueCar,(meter2pixel(carWidth), meter2pixel(carLength)))
# blueCar = pygame.transform.rotate(blueCar, 90)
clock = pygame.time.Clock()

egoCar = Car('R',20,80,0,False)
LFCar  = Car('L',5,78,0,True)
FCar   = Car('R',10,77,0,True)
LRCar  = Car('L',35,82,0,False)
RCar   = Car('R',35,90,0,False)
start_lane_change = False
lane_changing = False
finish_lane_change = False


def refreshScreen():
  drawRoad()
  cal_prob(egoCar,LFCar,0) # 0 = track after lane change
  cal_prob(RCar,FCar,0)
  cal_prob(LRCar,egoCar,0)
  cal_prob(egoCar,FCar,1) # 1 = track before lane change 
  cal_prob(LRCar,LFCar,1)
  cal_prob(RCar,egoCar,1)
  cal_prob(egoCar,LFCar,2) # 2 = when lane changing
  cal_prob(LRCar,egoCar,2) 
  cal_prob(RCar,egoCar,2)
  
  car_move()
  if lane_changing:
    screen.blit(blueCar,(egoCar.x_tl,egoCar.y_tl))
  else:
    screen.blit(whiteCar,(egoCar.x_tl,egoCar.y_tl))
  screen.blit(redCar,(LFCar.x_tl,LFCar.y_tl))
  screen.blit(redCar,(FCar.x_tl,FCar.y_tl))
  screen.blit(redCar,(RCar.x_tl,RCar.y_tl))
  screen.blit(redCar,(LRCar.x_tl,LRCar.y_tl))
  pygame.display.update()

def car_move():
  global start_lane_change
  global lane_changing
  if(egoCar.probList[1][-1] >= 0.2 and start_lane_change == 0):
    egoCar.mode = 'lane_change'
    p1 = RPoint(egoCar.x,egoCar.y)
    p2 = RPoint(egoCar.x,egoCar.y-meter2pixel(5))
    p3 = RPoint(egoCar.x-meter2pixel(4),egoCar.y-meter2pixel(10))
    p4 = RPoint(egoCar.x-meter2pixel(4),egoCar.y-meter2pixel(15))
    egoCar.step , egoCar.b_x, egoCar.b_y ,egoCar.b_alpha1= Bezier(p1,p2,p3,p4)
    start_lane_change = 1
    lane_changing = 1
  if(lane_changing):
    egoCar.mode = 'lane_change'
  egoCar.drive(egoCar) # Relative coordinate 
  LFCar.drive(egoCar)
  FCar.drive(egoCar)
  LRCar.drive(egoCar)
  RCar.drive(egoCar)
  # print(str(egoCar.steerAngle) + "\n")
  

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
  plot1(egoCar,0)
  plotv(egoCar)
  pygame.quit()

if __name__ == '__main__':
    main()