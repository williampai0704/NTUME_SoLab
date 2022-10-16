from cmath import exp
import pygame
import math
import matplotlib.pyplot as plt

class Car:
  probList = []
  timeList = []
  alpha1List = []
  alpha2List = []
  DList = []
  RList = []
  rList = []
  w = 2.4 #m
  l = 4.8
  gamma = 0.6
  lmda = 1
  
  def __init__(self,lane,y,vel,steerAngle):
    if lane == 'L':
      self.x = windowWidth/2 - meter2pixel(lineWidth/2+roadWidth/2)
    if lane == 'R':
      self.x = windowWidth/2 + meter2pixel(lineWidth/2+roadWidth/2)
      
    self.y = y
    self.x_tl = self.x-meter2pixel(carWidth)/2  #top left x
    self.y_tl = self.y-meter2pixel(carLength)/2 #top left y
    self.vel = vel
    self.steerAngle = steerAngle
    self.lane = lane
    

  def drive(self):
    self.x += self.vel*math.sin(self.steerAngle)
    self.y -= self.vel*math.cos(self.steerAngle)
    self.x_tl += self.vel*math.sin(self.steerAngle)
    self.y_tl -= self.vel*math.cos(self.steerAngle)
      
  def cal_prob(self,TCar):
    self.D = pixel2meter(math.sqrt((self.x- TCar.x)**2+(self.y - TCar.y)**2))
    self.alpha1 = math.atan2(-(TCar.x-self.x),-(TCar.y-self.y)) #radius 

    if (self.alpha1 <= math.pi/2) & (self.alpha1 >= -math.pi/2):
      self.R = math.sqrt((self.gamma*self.l*math.cos(self.alpha1))**2+(1/2*self.w*math.sin(self.alpha1))**2)
    else:
      self.R = math.sqrt(((1-self.gamma)*self.l*math.cos(self.alpha1))**2+(1/2*self.w*math.sin(self.alpha1))**2) 
    
    if TCar.lane == 'L':
      self.alpha2 = self.alpha1 - math.pi
    else: # 'R' or 0
      self.alpha2 = self.alpha1 + math.pi
    
    if (self.alpha2 <= math.pi/2) & (self.alpha2 >= -math.pi/2):
      self.r = math.sqrt((self.gamma*self.l*math.cos(self.alpha2))**2+(1/2*self.w*math.sin(self.alpha2))**2)
    else:
      self.r = math.sqrt(((1-self.gamma)*self.l*math.cos(self.alpha2))**2+(1/2*self.w*math.sin(self.alpha2))**2) 
    
    if self.D - self.R - self.r > 0:
      self.prob = self.lmda*exp(-self.lmda*(self.D-self.R-self.r))
    else:
      self.prob = 1
    
    self.probList.append(self.prob)
    self.timeList.append(pygame.time.get_ticks())
    self.alpha1List.append(self.alpha1/math.pi*180)
    self.alpha2List.append(self.alpha2/math.pi*180)
    self.DList.append(self.D)
    self.RList.append(self.R)
    self.rList.append(self.r)
  
  def plot_prob(self):
    plt.subplot(231)
    plt.plot(self.timeList,self.probList)
    plt.subplot(232)
    plt.plot(self.timeList,self.alpha1List)
    plt.subplot(233)
    plt.plot(self.timeList,self.alpha2List)
    plt.subplot(234)
    plt.plot(self.timeList,self.DList)
    plt.subplot(235)
    plt.plot(self.timeList,self.RList)
    plt.subplot(236)
    plt.plot(self.timeList,self.rList)
    print(self.RList)
    print(self.rList)
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
whiteCar = pygame.transform.scale(whiteCar, (meter2pixel(carLength), meter2pixel(carWidth)))
whiteCar = pygame.transform.rotate(whiteCar, 90)
redCar = pygame.image.load('pics/red_car.png')
redCar = pygame.transform.scale(redCar,(meter2pixel(carLength), meter2pixel(carWidth)))
redCar = pygame.transform.rotate(redCar, 90)
clock = pygame.time.Clock()

egoCar = Car('R',400,0,0)
LFCar = Car('L',800,5,0)

def refreshScreen(egoCar,LFCar):
  drawRoad()
  egoCar.drive()
  LFCar.drive()
  screen.blit(whiteCar,(egoCar.x_tl,egoCar.y_tl))
  screen.blit(redCar,(LFCar.x_tl,LFCar.y_tl))
  egoCar.cal_prob(LFCar)
  pygame.display.update()

running = True
while running:
  clock.tick(10)
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  keys = pygame.key.get_pressed()

  if keys[pygame.K_SPACE]:
    refreshScreen(egoCar,LFCar)
    
    
egoCar.plot_prob()

pygame.quit()

