from cmath import exp
import pygame
import math
import matplotlib.pyplot as plt

class Car:
  probList = []
  timeList = []
  timeList2 = []
  alpha1List = []
  alpha2List = []
  DList = []
  RList = []
  rList = []
  vList = []
  w = 2.4 #car width
  l = 4.8 #car length
  gamma = 0.6
  lmda = 1
  
  def __init__(self,lane,y,vel,acc,steerAngle):
    if lane == 'L':
      self.x = windowWidth/2 - meter2pixel(lineWidth/2+roadWidth/2)
    if lane == 'R':
      self.x = windowWidth/2 + meter2pixel(lineWidth/2+roadWidth/2)
      
    self.y = y
    self.x_tl = self.x-meter2pixel(carWidth)/2  #top left x
    self.y_tl = self.y-meter2pixel(carLength)/2 #top left y
    self.vel = vel
    self.steerAngle = steerAngle/180*math.pi
    self.lane = lane   
    self.acc = acc #acceleration

  def drive(self):
    self.vel += self.acc
    self.vList.append(self.vel)
    self.timeList2.append(pygame.time.get_ticks())
    self.x += self.vel*math.sin(self.steerAngle)
    self.y -= self.vel*math.cos(self.steerAngle)
    self.x_tl += self.vel*math.sin(self.steerAngle)
    self.y_tl -= self.vel*math.cos(self.steerAngle)
      
  def cal_prob(self,TCar):
    self.D = pixel2meter(math.sqrt((self.x- TCar.x)**2+(self.y - TCar.y)**2))
    self.alpha1 = math.atan2(-(TCar.x-self.x),-(TCar.y-self.y)) #radius 
    self.alpha1_h = self.alpha1-self.steerAngle # angle between forward direction and target vehicle

    if (self.alpha1_h <= math.pi/2) & (self.alpha1_h >= -math.pi/2):
      self.R = math.sqrt((self.gamma*self.l*math.cos(self.alpha1_h))**2+(1/2*self.w*math.sin(self.alpha1_h))**2)
    else:
      self.R = math.sqrt(((1-self.gamma)*self.l*math.cos(self.alpha1_h))**2+(1/2*self.w*math.sin(self.alpha1_h))**2) 
    
    #Calculate alpha2 
    if TCar.lane == 'L':
      self.alpha2 = self.alpha1 - math.pi
    else: # 'R' or 0
      self.alpha2 = self.alpha1 + math.pi
    self.alpha2_h = self.alpha2-TCar.steerAngle # angle between forward direction and target vehicle
    
    if (self.alpha2_h <= math.pi/2) & (self.alpha2_h >= -math.pi/2):
      self.r = math.sqrt((self.gamma*self.l*math.cos(self.alpha2_h))**2+(1/2*self.w*math.sin(self.alpha2_h))**2)
    else:
      self.r = math.sqrt(((1-self.gamma)*self.l*math.cos(self.alpha2_h))**2+(1/2*self.w*math.sin(self.alpha2_h))**2) 
    
    #Calculate probability
    if self.D - self.R - self.r > 0:
      self.prob = self.lmda*exp(-self.lmda*(self.D-self.R-self.r))
    else:
      self.prob = 1
    
    self.probList.append(self.prob)
    self.timeList.append(pygame.time.get_ticks())
    self.alpha1List.append(self.alpha1/math.pi*180)
    self.alpha2List.append(self.alpha2/math.pi*180)
    self.DList.append(self.D-self.R-self.r)
    self.RList.append(self.R)
    self.rList.append(self.r)
  
  def plot_prob(self):
    plt.subplot(331)
    plt.plot(self.timeList,self.probList)
    plt.subplot(332)
    plt.plot(self.timeList,self.alpha1List)
    plt.subplot(333)
    plt.plot(self.timeList,self.alpha2List)
    plt.subplot(334)
    plt.plot(self.timeList,self.DList)
    plt.subplot(335)
    plt.plot(self.timeList,self.RList)
    plt.subplot(336)
    plt.plot(self.timeList,self.rList)
    plt.subplot(337)
    plt.plot(self.timeList2,self.vList)
    plt.show()

def meter2pixel(m):
  return m*30
def pixel2meter(p):
  return p/30

def drawRoad():
  tW = meter2pixel(totalWidth)
  rW = meter2pixel(roadWidth)
  lW = meter2pixel(lineWidth)
  lL = meter2pixel(lineLength)
  lS = meter2pixel(lineSpace)
  road = pygame.Rect(0,0,tW,windowLength)
  line = pygame.Rect(0,0,lW,windowLength)
  road.center = (windowWidth/2,windowLength/2)
  line.center = (windowWidth/2,windowLength/2)
  screen.fill([0,0,0])
  pygame.draw.rect(screen,'gray70',road)
  pygame.draw.rect(screen,'yellow',line)
  
#Length 
windowWidth = 600 #pixel
windowLength = 800
carWidth = 2.4 #m
carLength = 4.8
totalWidth = 8 #m
roadWidth = 3.9
lineWidth = 0.2
lineLength = 4
lineSpace = 6

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

egoCar = Car('R',500,0,0,0)
LFCar = Car('L',800,5,0.03,0)
FCar = Car('R',300,-3,0,0)

def refreshScreen(egoCar,LFCar):
  drawRoad()
  egoCar.drive()
  LFCar.drive()
  FCar.drive()
  screen.blit(whiteCar,(egoCar.x_tl,egoCar.y_tl))
  screen.blit(redCar,(LFCar.x_tl,LFCar.y_tl))
  screen.blit(redCar,(FCar.x_tl,FCar.y_tl))
  egoCar.cal_prob(LFCar)
  # egoCar.cal_prob(FCar)
  pygame.display.update()

running = True
while running:
  clock.tick(10)
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  keys = pygame.key.get_pressed()

  refreshScreen(egoCar,LFCar)
    
egoCar.plot_prob()
pygame.quit()