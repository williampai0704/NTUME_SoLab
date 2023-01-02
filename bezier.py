import math
import matplotlib.pyplot as plt

class RPoint:
    def __init__(self,x,y):
        self.x= x
        self.y = y
    
    
def Bezier(p1,p2,p3,p4):
    tList = list(range(0,101))
    tList = [i/100 for i in tList]
    b_x = []
    b_y = []
    b_alpha1 = [0]
    step = 0
    i = 0
    for tt in tList:
        b_x.append((1-tt)**3*(p1.x)+3*(1-tt)**2*tt*(p2.x)+3*(1-tt)*tt**2*(p3.x)+tt**3*(p4.x))
        b_y.append((1-tt)**3*(p1.y)+3*(1-tt)**2*tt*(p2.y)+3*(1-tt)*tt**2*(p3.y)+tt**3*(p4.y))
        if(i >= 1):
            step += (math.sqrt((b_x[-1]-b_x[-2])**2+(b_y[-1]-b_y[-2])**2))
            b_alpha1.append(math.atan2(-(b_x[-1]-b_x[-2]),-(b_y[-1]-b_y[-2]))) #radius
        i+=1
    
    step = step/len(tList)
    # print(len(tList))
    # print(step)
    # plt.plot(b_x,b_y)
    # plt.axis([0, 600, 0, 100])
    # plt.grid(True)
    # ax = plt.gca()
    # ax.set_aspect('equal', adjustable='box')
    # plt.show()
    return step, b_x, b_y, b_alpha1

# def main():
#     p1 = RPoint(0,0)
#     p2 = RPoint(200,0)
#     p3 = RPoint(400,80)
#     p4 = RPoint(600,80)
#     step, b_x,b_y,b_alpha_1 = Bezier(p1,p2,p3,p4)
#     print(b_x)
    
# if __name__ == '__main__':
#     main()