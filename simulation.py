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
  
  def __init__(self, x,y,vel,steerAngle,lane):
    self.x = x
    self.y = y
    self.x_c = x+carWidth_p/2 #center x
    self.y_c = y+carLength_p/2 #center y
    self.vel = vel
    self.steerAngle = steerAngle
    self.lane = lane
    

  def drive(self):
    self.x += self.vel*math.sin(self.steerAngle)
    self.y -= self.vel*math.cos(self.steerAngle)
    self.x_c += self.vel*math.sin(self.steerAngle)
    self.y_c -= self.vel*math.cos(self.steerAngle)
      
  def cal_prob(self,TCar):
    self.D = pixel2meter(math.sqrt((self.x_c- TCar.x_c)**2+(self.y_c - TCar.y_c)**2))
    self.alpha1 = math.atan2(-(TCar.x_c-self.x_c),-(TCar.y_c-self.y_c)) #radius 

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

pygame.init()
screen = pygame.display.set_mode((800,1000))
pygame.display.set_caption("SoLab")
carWidth_p = 24*3
carLength_p = 48*3
whiteCar = pygame.image.load('pics/white_car.png')
whiteCar = pygame.transform.scale(whiteCar, (carLength_p, carWidth_p))
whiteCar = pygame.transform.rotate(whiteCar, 90)
redCar = pygame.image.load('pics/red_car.png')
redCar = pygame.transform.scale(redCar,(carLength_p, carWidth_p))
redCar = pygame.transform.rotate(redCar, 90)
clock = pygame.time.Clock()

egoCar = Car(400,300,0,0,'R')
LFCar = Car(328,800,5,0,'L')

def refreshScreen(egoCar,LFCar):
  screen.fill([0,0,0])
  egoCar.drive()
  LFCar.drive()
  screen.blit(whiteCar,(egoCar.x,egoCar.y))
  screen.blit(redCar,(LFCar.x,LFCar.y))
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

