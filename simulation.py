from cmath import exp
import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("SoLab")
x = 50
y = 100
width = 40
height = 50
vel = 0.3


class Car:
  
  def __init__(self, x,y,vel,steerAngle):
    self.x = x
    self.y = y
    self.vel = vel
    self.steerAngle = steerAngle

  def drive(self):
    self.x += vel*math.sin(self.steerAngle)
    self.y -= vel*math.cos(self.steerAngle)
      
  def cal_prob(self,TCar):
    w = 1.6
    l = 3
    r = 0.6
    lmda = 1
    self.D = math.sqrt(abs(self.x- TCar.x)**2+abs(self.y - TCar.y)**2)
    self.alpha = math.atan2(-(TCar.x-self.x),-(TCar.y-self.y)) #radius 

    if self.alpha <= math.pi/2 & self.alpha >= -math.pi/2:
      self.R = math.sqrt((r*l*math.cos(self.alpha))**2+(1/2*w*math.sin(self.alpha))**2)
    else:
      self.R =  math.sqrt(((1-r)*l*math.cos(self.alpha))**2+(1/2*w*math.sin(self.alpha))**2) 
    
    if self.D - self.R > 0:
      self.prob = lmda*exp(-lmda*(self.D-self.R))
    else:
      self.prob = 1
    

whiteCar = pygame.image.load('pics/white_car.png')
whiteCar = pygame.transform.scale(whiteCar, (64, 32))
redCar = pygame.image.load('pics/red_car.png')
redCar = pygame.transform.scale(redCar,(64,32))
clock = pygame.time.Clock()

def refreshScreen():
  screen.fill([0,0,0])
  screen.blit(whiteCar,(x,y))
  pygame.display.update()

running = True

while running:
  clock.tick(100)
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
  keys = pygame.key.get_pressed()
  if keys[pygame.K_LEFT]:
    x -= vel
  if keys[pygame.K_RIGHT]:
    x += vel
  if keys[pygame.K_UP]:
    y -= vel
    # whiteCar = pygame.transform.rotate(whiteCar, 10)
  if keys[pygame.K_DOWN]:
    y += vel

  refreshScreen()


pygame.quit()