from cmath import exp
import pygame
import math
import matplotlib.pyplot as plt

class Car:
  probList = []
  timeList = []
  alphaList = []
  def __init__(self, x,y,vel,steerAngle):
    self.x = x
    self.y = y
    self.vel = vel
    self.steerAngle = steerAngle

  def drive(self):
    self.x += self.vel*math.sin(self.steerAngle)
    self.y -= self.vel*math.cos(self.steerAngle)
      
  def cal_prob(self,TCar):
    w = 2.4
    l = 4.8
    r = 0.6
    lmda = 1
    self.D = pixel2meter(math.sqrt((self.x- TCar.x)**2+(self.y - TCar.y)**2))
    self.alpha = math.atan2(-(TCar.x-self.x),-(TCar.y-self.y)) #radius 

    if (self.alpha <= math.pi/2) & (self.alpha >= -math.pi/2):
      self.R = math.sqrt((r*l*math.cos(self.alpha))**2+(1/2*w*math.sin(self.alpha))**2)
    else:
      self.R =  math.sqrt(((1-r)*l*math.cos(self.alpha))**2+(1/2*w*math.sin(self.alpha))**2) 
    
    if self.D - self.R > 0:
      self.prob = lmda*exp(-lmda*(self.D-self.R))
    else:
      self.prob = 1
    
    self.probList.append(self.prob)
    self.timeList.append(pygame.time.get_ticks())
    self.alphaList.append(self.alpha/math.pi*180)
  
  def plot_prob(self):
    plt.subplot(121)
    plt.plot(self.timeList,self.probList)
    plt.subplot(122)
    plt.plot(self.timeList,self.alphaList)
    plt.show()

def meter2pixel(m):
  return m*30
def pixel2meter(p):
  return p/30

pygame.init()
screen = pygame.display.set_mode((600,800))
pygame.display.set_caption("SoLab")
whiteCar = pygame.image.load('pics/white_car.png')
whiteCar = pygame.transform.scale(whiteCar, (48*3, 24*3))
whiteCar = pygame.transform.rotate(whiteCar, 90)
redCar = pygame.image.load('pics/red_car.png')
redCar = pygame.transform.scale(redCar,(48*3,24*3))
redCar = pygame.transform.rotate(redCar, 90)
clock = pygame.time.Clock()

egoCar = Car(400,300,0,0)
LFCar = Car(300,600,5,0)

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

