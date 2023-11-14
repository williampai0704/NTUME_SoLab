import pygame
import math
from math import exp
import matplotlib.pyplot as plt
import random 

from bezier import Bezier
from bezier import RPoint
from velocityProfile import velocityProfile

class Car:
  w     = 1.6 #car width (m)
  l     = 3.2 #car length (m)
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
    self.vel = km_hr2pixel_s(vel) # from km/hr --> pixel/frame
    self.vel2 = vel
    self.vel_ideal = vel
    self.steerAngle = steerAngle/180*math.pi
    self.lane = lane   
    # self.acc = meter2pixel(acc)/10 #acceleration
    self.probList   = [[] for i in range(9)]
    self.timeList   = [[] for i in range(9)]
    self.timeList2  = [[] for i in range(9)]
    self.alpha1List = [[] for i in range(9)]
    self.alpha2List = [[] for i in range(9)]
    self.DList      = [[] for i in range(9)]
    self.RList      = [[] for i in range(9)]
    self.rList      = [[] for i in range(9)]
    self.vList      = [[] for i in range(9)]
    self.xList      = [[] for i in range(9)]
    self.yList      = [[] for i in range(9)]
    self.mode = 'stand_by'
    self.isFront = isFront
    self.acc = 0

  def drive(self,egoCar):
    global lane_changing
    global finish_lane_change
    global start_lane_change
    global at_last
    global at_front
    global at_middle
    # self.vel += self.acc
    if not self.isFront:
      if not start_lane_change:
        if at_last:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[0][-1],self.vel_ideal)) 
        elif at_front:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[3][-1],self.vel_ideal)) 
        else:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[6][-1],self.vel_ideal))
      if lane_changing: 
        if at_last:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[1][-1],self.vel_ideal)) 
        elif at_front:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[4][-1],self.vel_ideal))   
        else:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[7][-1],self.vel_ideal))
      if finish_lane_change:
        if at_last:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[2][-1],self.vel_ideal))
        elif at_front:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[5][-1],self.vel_ideal))
        else:
          self.vel = km_hr2pixel_s(velocityProfile(self.probList[8][-1],self.vel_ideal))
    # print("egoCar.vel ="+str(egoCar.vel))
    if self.mode == 'lane_change':
      self.i += int(self.vel/self.step)
      
      # print(self.i)  # 11
      if (self.i >= len(self.b_x)):
        self.i = len(self.b_x)-1
        self.mode = 'stand_by'
        print("back to stand by")
        finish_lane_change = True
        lane_changing = False
      self.x = self.b_x[self.i]
      self.y = self.b_y[self.i]
      self.steerAngle = self.b_alpha1[self.i]
      # print(self.steerAngle/math.pi*180)
    if self.mode == 'stand_by':
      self.steerAngle = 0
      self.x += self.vel*math.sin(self.steerAngle) # Real x(pixel)
      self.y -= self.vel*math.cos(self.steerAngle) # Real y(pixel)
    
    
    # self.y_ref -= self.vel*math.cos(self.steerAngle)-egoCar.vel*math.cos(egoCar.steerAngle) # For relative view on screen
    self.y_ref = self.y - egoCar.y + meter2pixel(20)
    self.x_tl = self.x-meter2pixel(carWidth)/2  #top left x
    self.y_tl = self.y_ref-meter2pixel(carLength)/2 #top left y
    for i in range(8):
      self.vList[i].append(pixel_s2km_hr(self.vel))
      self.xList[i].append(pixel2meter(self.x))
      self.yList[i].append(pixel2meter(self.y))
      self.timeList2[i].append(pygame.time.get_ticks()/1000)
    
  def predict_drive(self,f_egoCar): # for prediction
    # global predict_lane_changing
    global predict_finish_lane_change
    global predict_at_last
    global predict_at_front
    global predict_at_middle
    # global predict_start_lane_change
    if not self.isFront:
      if at_last:
        self.vel = km_hr2pixel_s(velocityProfile(self.probList[1][-1],self.vel_ideal)) 
      elif at_front:
        self.vel = km_hr2pixel_s(velocityProfile(self.probList[4][-1],self.vel_ideal))   
      else:
        self.vel = km_hr2pixel_s(velocityProfile(self.probList[7][-1],self.vel_ideal))
    # add gaussian distribution
    self.acc = random.gauss(0,g2pixel_frame_frame(0.1*9.81))
    self.vel += self.acc
    if self.mode == 'lane_change':
      self.i += int(self.vel/self.step)
      # print(self.i)
      if (self.i >= len(self.b_x)):
        self.i = len(self.b_x)-1
        self.mode = 'stand_by'
        print("predict back to stand by")
        predict_finish_lane_change = True
        # predcit_lane_changing = False
      self.x = self.b_x[self.i]
      self.y = self.b_y[self.i]
      self.steerAngle = self.b_alpha1[self.i]
    if self.mode == 'stand_by':
      self.steerAngle = 0
      self.x += self.vel*math.sin(self.steerAngle) # Real x(pixel)
      self.y -= self.vel*math.cos(self.steerAngle) # Real y(pixel)

    # self.y_ref -= self.vel*math.cos(self.steerAngle) - f_egoCar.vel*math.cos(f_egoCar.steerAngle) # For relative view on screen
    self.y_ref = self.y - f_egoCar.y+ meter2pixel(20)
    self.x_tl = self.x-meter2pixel(carWidth)/2  #top left x
    self.y_tl = self.y_ref-meter2pixel(carLength)/2 #top left y
    # for i in range(4):
    #   self.vList[i].append(pixel_s2km_hr(self.vel))
    #   self.xList[i].append(pixel2meter(self.x))
    #   self.yList[i].append(pixel2meter(self.y))
    #   self.timeList2[i].append(pygame.time.get_ticks()/1000)
      
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
    eCar.r = math.sqrt((TCar.gamma*TCar.l*math.cos(eCar.alpha2_h))**2+(1/2*TCar.w*math.sin(eCar.alpha2_h))**2)
  else:
    eCar.r = math.sqrt(((1-TCar.gamma)*TCar.l*math.cos(eCar.alpha2_h))**2+(1/2*TCar.w*math.sin(eCar.alpha2_h))**2) 
  
  eCar.lmda2 = 0.5 - ((eCar.vel-60)/60)
  #print(eCar.lmda2)
  #Calculate probability
  if eCar.D - eCar.R - eCar.r > 0:
    eCar.prob = eCar.lmda*exp(-eCar.lmda2*(eCar.D-eCar.R-eCar.r))
  else:
    eCar.prob = 1
  
  eCar.probList[i].append(eCar.prob)
  eCar.timeList[i].append(pygame.time.get_ticks()/1000)
  eCar.alpha1List[i].append(eCar.alpha1_h/math.pi*180)
  eCar.alpha2List[i].append(eCar.alpha2/math.pi*180)
  eCar.DList[i].append(eCar.D-eCar.R-eCar.r)
  eCar.RList[i].append(eCar.R)
  eCar.rList[i].append(eCar.r)
  



# =================================================================================

def plot_report(TCar):
  plt.subplot(131)
  plt.plot(TCar.timeList[0],TCar.probList[0])
  plt.xlabel('Risk to front car')
  plt.subplot(132)
  plt.plot(TCar.timeList[7],TCar.probList[7])
  plt.xlabel('Risk to left front car')
  plt.subplot(133)
  plt.plot(TCar.timeList[1],TCar.probList[1])
  plt.xlabel('Risk to left rear car')
  plt.show()
  
  plt.subplot(131)
  plt.plot(timeList0,probList0)
  plt.xlabel('Predict Risk 1')
  plt.subplot(132)
  plt.plot(timeList1,probList1)
  plt.xlabel('Predict Risk 2')
  plt.subplot(133)
  plt.plot(timeList2,probList2)
  plt.xlabel('Predict Risk 3')
  plt.show()
  
  # plt.subplot(221)
  # newlist = [x1 - x2 for (x1, x2) in zip(LFCar.yList[0], egoCar.yList[0])]
  # plt.plot(LFCar.timeList2[3],newlist)
  # # plt.xlim(5, 10)
  # # plt.ylim(-70,-100)
  # # ax = plt.gca()
  # # ax.set_aspect('equal', adjustable='box')
  # plt.subplot(222)
  # plt.plot(egoCar.timeList[0],egoCar.DList[0])
  # plt.subplot(223)
  # newlist2 = [x1 - x2 for (x1, x2) in zip(LRCar.yList[0], egoCar.yList[0])]
  # plt.plot(LRCar.timeList2[3],newlist2)
  # plt.subplot(224)
  # plt.plot(egoCar.timeList[3],egoCar.DList[3])
  # plt.show()
  
  
  
def meter2pixel(m):
  return m*20
def pixel2meter(p):
  return p/20
def km_hr2pixel_s(v):
  return meter2pixel(v*1000/(10*3600))
def pixel_s2km_hr(p):
  return pixel2meter(p/1000*3600*10)
def g2pixel_frame_frame(g):
  return meter2pixel(g/100)


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

def riskPredict():
  global predict_at_last
  global predict_at_front
  global predict_at_middle
  f_egoCar = Car(egoCar.lane,pixel2meter(egoCar.y),egoCar.vel2,egoCar.steerAngle,egoCar.isFront)
  f_LFCar  = Car(LFCar.lane,pixel2meter(LFCar.y),LFCar.vel2,LFCar.steerAngle,LFCar.isFront)
  f_FCar   = Car(FCar.lane,pixel2meter(FCar.y),FCar.vel2,FCar.steerAngle,FCar.isFront)
  f_LRCar  = Car(LRCar.lane,pixel2meter(LRCar.y),LRCar.vel2,LRCar.steerAngle,LRCar.isFront)
  f_RCar  = Car(RCar.lane,pixel2meter(RCar.y),RCar.vel2,RCar.steerAngle,RCar.isFront)
  
  f_p1 = RPoint(f_egoCar.x,f_egoCar.y)
  f_p2 = RPoint(f_egoCar.x,f_egoCar.y-meter2pixel(bezier_point[0]))
  f_p3 = RPoint(f_egoCar.x-meter2pixel(4),f_egoCar.y-meter2pixel(bezier_point[1]))
  f_p4 = RPoint(f_egoCar.x-meter2pixel(4),f_egoCar.y-meter2pixel(bezier_point[2]))
  f_egoCar.step , f_egoCar.b_x, f_egoCar.b_y ,f_egoCar.b_alpha1= Bezier(f_p1,f_p2,f_p3,f_p4)
  while(not predict_finish_lane_change):
    # global predict_start_lane_change
    # global predict_lane_changing
    # predict_start_lane_change = 1
    # predict_lane_changing = 1
    f_egoCar.mode = 'lane_change'
    cal_prob(f_egoCar,f_FCar,0) # 0 = egoCar will be at last before lane change
    cal_prob(f_LRCar,f_LFCar,0)
    cal_prob(f_RCar,f_egoCar,0)
    cal_prob(f_LRCar,f_LFCar,1) # 1 = egoCar will be at last when lane changing
    cal_prob(f_egoCar,f_LRCar,1)
    cal_prob(f_RCar,f_egoCar,1)
    cal_prob(f_LRCar,f_LFCar,2) # 2 = egoCar will be at last after lane change
    cal_prob(f_egoCar,f_LRCar,2)
    cal_prob(f_RCar,f_FCar,2)
    cal_prob(f_LRCar,f_LFCar,3) # 3 = egoCar will be at front before lane change
    cal_prob(f_egoCar,f_FCar,3)
    cal_prob(f_RCar,f_egoCar,3)
    cal_prob(f_LRCar,f_LFCar,4) # 4 = egoCar will be at front when lane changing
    cal_prob(f_egoCar,f_FCar,4)
    cal_prob(f_RCar,f_egoCar,4)
    cal_prob(f_LRCar,f_LFCar,5) # 5 = egoCar will be at front after lane change
    cal_prob(f_RCar,f_FCar,5)
    cal_prob(f_LRCar,f_LFCar,6) # 6 = egoCar will be at middle before lane change
    cal_prob(f_egoCar,f_FCar,6)
    cal_prob(f_RCar,f_egoCar,6)
    cal_prob(f_LRCar,f_egoCar,7) # 7 = egoCar will be at middle when lane changing
    cal_prob(f_egoCar,f_LFCar,7)
    cal_prob(f_RCar,f_egoCar,7)
    cal_prob(f_LRCar,f_egoCar,8) # 8 = egoCar will be at middle after lane change
    cal_prob(f_egoCar,f_LFCar,8)
    cal_prob(f_RCar,f_FCar,8)
     
    
    f_egoCar.predict_drive(f_egoCar) # Relative coordinate 
    f_LFCar.predict_drive(f_egoCar)
    f_FCar.predict_drive(f_egoCar)
    f_LRCar.predict_drive(f_egoCar)
    f_RCar.predict_drive(f_egoCar)
    f_center_point = pygame.draw.circle(screen,'red', (f_egoCar.x,f_egoCar.y_ref), 5)
    f_center_point = pygame.draw.circle(screen,'green', (f_LRCar.x,f_LRCar.y_ref), 5)
    f_center_point = pygame.draw.circle(screen,'green', (f_LFCar.x,f_LFCar.y_ref), 5)
    # f_center_point = pygame.draw.circle(screen,'green', (f_FCar.x,f_FCar.y_ref), 5)
    
  
  if at_last:
    avg_risk0 = sum(f_egoCar.probList[0])/len(f_egoCar.probList[0]) # FCar
    avg_risk1 = sum(f_egoCar.probList[1])/len(f_egoCar.probList[1]) # LRCar
    avg_risk2 = 0
    max_risk0 = max(f_egoCar.probList[0])
    max_risk1 = max(f_egoCar.probList[1])
    max_risk2 = 0
    probList0 = f_egoCar.probList[0]
    probList1 = f_egoCar.probList[1]
    probList2 = 0
    timeList0 = f_egoCar.timeList[0]
    timeList1 = f_egoCar.timeList[1]
    timeList2 = 0
    
    
  elif at_front:
    avg_risk0 = sum(f_egoCar.probList[3])/len(f_egoCar.probList[3]) # FCar
    avg_risk1 = sum(f_egoCar.probList[7])/len(f_egoCar.probList[7]) # LFCar
    avg_risk2 = 0
    max_risk0 = max(f_egoCar.probList[3])
    max_risk1 = max(f_egoCar.probList[7])
    max_risk2 = 0
    probList0 = f_egoCar.probList[3]
    probList1 = f_egoCar.probList[7]
    probList2 = 0
    timeList0 = f_egoCar.timeList[3]
    timeList1 = f_egoCar.timeList[7]
    timeList2 = 0
   
  else:
    avg_risk0 = sum(f_egoCar.probList[0])/len(f_egoCar.probList[0]) # FCar
    avg_risk1 = sum(f_egoCar.probList[8])/len(f_egoCar.probList[8]) # LFCar
    avg_risk2 = sum(f_egoCar.probList[1])/len(f_egoCar.probList[1]) # LRCar
    max_risk0 = max(f_egoCar.probList[0])
    max_risk1 = max(f_egoCar.probList[8])
    max_risk2 = max(f_egoCar.probList[1])
    probList0 = f_egoCar.probList[0]
    probList1 = f_egoCar.probList[8]
    probList2 = f_egoCar.probList[1]
    timeList0 = f_egoCar.timeList[0]
    timeList1 = f_egoCar.timeList[8]
    timeList2 = f_egoCar.timeList[1]
    
  return avg_risk0 , avg_risk1, avg_risk2, max_risk0, max_risk1, max_risk2 , probList0, probList1, probList2, timeList0, timeList1, timeList2
  
  
    
#=================================================================================== 

#Length Parameter 
windowWidth  = 300 #pixel
windowLength = 800
carWidth     = 1.6 #m
carLength    = 3.2
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

egoCar = Car('R',20,60,0,False)
LFCar  = Car('L',15,61,0,True)
FCar   = Car('R',12,57,0,True)
LRCar  = Car('L',25,57,0,False)
RCar   = Car('R',35,64,0,False)
start_lane_change = False
lane_changing = False
finish_lane_change = False
at_last = False
at_front = False
at_middle = True
predict_start_lane_change = False
predict_lane_changing = False
predict_finish_lane_change = False
predict_at_last = False
predict_at_front = False
pedict_at_middle = True
bezier_point = [10,20,30]


def refreshScreen():
  drawRoad()
  
  cal_prob(egoCar,FCar,0) # 0 = egoCar will be at last before lane change
  cal_prob(LRCar,LFCar,0)
  cal_prob(RCar,egoCar,0)
  cal_prob(LRCar,LFCar,1) # 1 = egoCar will be at last when lane changing
  cal_prob(egoCar,LRCar,1)
  cal_prob(RCar,egoCar,1)
  cal_prob(LRCar,LFCar,2) # 2 = egoCar will be at last after lane change
  cal_prob(egoCar,LRCar,2)
  cal_prob(RCar,FCar,2)
  cal_prob(LRCar,LFCar,3) # 3 = egoCar will be at front before lane change
  cal_prob(egoCar,FCar,3)
  cal_prob(RCar,egoCar,3)
  cal_prob(LRCar,LFCar,4) # 4 = egoCar will be at front when lane changing
  cal_prob(egoCar,FCar,4)
  cal_prob(RCar,egoCar,4)
  cal_prob(LRCar,LFCar,5) # 5 = egoCar will be at front after lane change
  cal_prob(RCar,FCar,5)
  cal_prob(LRCar,LFCar,6) # 6 = egoCar will be at middle before lane change
  cal_prob(egoCar,FCar,6)
  cal_prob(RCar,egoCar,6)
  cal_prob(LRCar,egoCar,7) # 7 = egoCar will be at middle when lane changing
  cal_prob(egoCar,LFCar,7)
  cal_prob(RCar,egoCar,7)
  cal_prob(LRCar,egoCar,8) # 8 = egoCar will be at middle after lane change
  cal_prob(egoCar,LFCar,8)
  cal_prob(RCar,FCar,8)
  
  
  car_move()
  if lane_changing:
    screen.blit(blueCar,(egoCar.x_tl,egoCar.y_tl))
  else:
    screen.blit(whiteCar,(egoCar.x_tl,egoCar.y_tl))
  screen.blit(redCar,(LFCar.x_tl,LFCar.y_tl))
  screen.blit(redCar,(FCar.x_tl,FCar.y_tl))
  screen.blit(redCar,(RCar.x_tl,RCar.y_tl))
  screen.blit(redCar,(LRCar.x_tl,LRCar.y_tl))
  '''
  center_point = pygame.draw.circle(screen,'yellow', (egoCar.x_tl,egoCar.y_tl), 5)
  center_point = pygame.draw.circle(screen,'yellow', (LRCar.x_tl,LRCar.y_tl), 5)
  center_point = pygame.draw.circle(screen,'yellow', (LFCar.x_tl,LFCar.y_tl), 5)
  center_point = pygame.draw.circle(screen,'yellow', (RCar.x_tl,RCar.y_tl), 5)
  center_point = pygame.draw.circle(screen,'yellow', (FCar.x_tl,FCar.y_tl), 5)
  TL_point = pygame.draw.circle(screen,'red', (egoCar.x,egoCar.y_ref), 5)
  TL_point = pygame.draw.circle(screen,'red', (LRCar.x,LRCar.y_ref), 5)
  TL_point = pygame.draw.circle(screen,'red', (LFCar.x,LFCar.y_ref), 5)
  TL_point = pygame.draw.circle(screen,'red', (RCar.x,RCar.y_ref), 5)
  TL_point = pygame.draw.circle(screen,'red', (FCar.x,FCar.y_ref), 5) '''

  pygame.display.update()

def car_move():
  global start_lane_change
  global lane_changing
  global predict_finish_lane_change
  global at_last
  global at_front
  global probList0
  global probList1
  global probList2
  global timeList0
  global timeList1
  global timeList2
  if(egoCar.probList[6][-1] >= 0.1 and egoCar.probList[7][-1] <= 0.5 and start_lane_change == 0):
    avg_risk0 , avg_risk1, avg_risk2, max_risk0, max_risk1, max_risk2 ,probList0, probList1, probList2, timeList0, timeList1, timeList2= riskPredict()
    print(avg_risk0)
    print(avg_risk1)
    print(avg_risk2)
    print(max_risk0)
    print(max_risk1)
    print(max_risk2)
    
    print("========================")
    if (avg_risk0 <= 0.4 and avg_risk1 <= 0.5 and avg_risk2 <= 0.3 and max(max_risk0,max_risk1,max_risk2) <= 0.5):
      
      print("predict success")
      print(avg_risk0)
      print(avg_risk1)
      print(avg_risk2)
      egoCar.mode = 'lane_change'
      p1 = RPoint(egoCar.x,egoCar.y)
      p2 = RPoint(egoCar.x,egoCar.y-meter2pixel(bezier_point[0]))
      p3 = RPoint(egoCar.x-meter2pixel(4),egoCar.y-meter2pixel(bezier_point[1]))
      p4 = RPoint(egoCar.x-meter2pixel(4),egoCar.y-meter2pixel(bezier_point[2]))
      egoCar.step , egoCar.b_x, egoCar.b_y ,egoCar.b_alpha1= Bezier(p1,p2,p3,p4)
      print("step = "+str(egoCar.step))
      start_lane_change = 1
      lane_changing = 1    
    else:
      predict_finish_lane_change = False
      
  if (LRCar.y < egoCar.y):
    at_last = True
    at_middle = False
    print("change to at last")
  elif (LFCar.y > egoCar.y):
    at_front = True 
    at_moddle = False
    egoCar.isFront = True  
    print("change to at front")
  else:
    print("still in middle")
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
    refreshScreen()
      
  # plot1(egoCar,0)
  # plot1(egoCar,1)
  # plotv(egoCar)
  # plot1(egoCar,3)
  plot_report(egoCar)
  pygame.quit()

if __name__ == '__main__':
    main()