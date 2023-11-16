import math
import numpy as np
from PIL import Image

#useful functions
def dist(p1,t1,p2,t2):
    return np.arccos((np.cos(t1)*np.cos(t2))+(np.sin(t1)*np.sin(t2)*np.cos(p1-p2)))
def s2c(p):
    return (np.array((np.sin(p[1])*np.cos(p[0]),np.sin(p[1])*np.sin(p[0]),np.cos(p[1]))))

#constants for the final image
n=714
c=88

#gives the stars positions on the sphere
stars=[]
def doStars():
    global stars
    stars=[]
    for i in range(n):
        #x,y,z
        pos=(np.random.rand(3)*2)-1
        r=np.linalg.norm(pos)
        theta=np.arccos(pos[2]/r)
        phi=np.arctan2(pos[1],pos[0])
        stars.append([phi,theta])
    stars=np.array(stars)
    

    '''
start to build out the constellations
check all stars in a constellation with all stars not in a constellation yet
the shortest path will be connected
repeat n-c times
'''
constellations=[]
unProcessedStars=[]
paths=[]
pathPerStars=[[] for i in range(n)]
def doConst():
    global constellations
    global unProcessedStars
    global paths
    global pathPerStars
    #initialize constellations. Using first c stars as that should already be randomized 
    #constellation seeds
    constellations=[[i] for i in range(c)]
    unProcessedStars=list(np.arange(c,n))
    paths=[]
    for i in range(n-c):
        d=99999999
        idj=-1
        idk=-1
        idm=-1
        for j in range(c):
            for k in constellations[j]:
                for m in unProcessedStars:
                    tdist=dist(stars[m][0],stars[m][1],stars[k][0],stars[k][1])
                    if(tdist<d):
                        d=tdist
                        idj=j
                        idk=k
                        idm=m
        constellations[idj].append(idm)
        paths.append((idk,idm))
        pathPerStars[idk].append(idm)
        pathPerStars[idm].append(idk)
        unProcessedStars.remove(idm)
    constellations=[np.array(constellations[i]) for i in range(c)]
    pathPerStars=[np.array(pathPerStars[i]) for i in range(n)]
'''
initial paths have been defined, almost ready to draw.
constellations have cycles in the graph though. and we have built them as a tree
need a way to define if more paths should be made.


compare each star within the constellation, if a path is shortest it will already be defined.
if it is close to the shortest path, we should probably still draw it.
'''
path2=[]
pathPerStars2=[]
def addPath():
    global path2
    global pathPerStars2
    pathPerStars2=[[] for i in range(n)]
    path2=[]
    for i in constellations:

        for j in i:
            l=[]
            for k in i:
                if(j!=k):
                    d=dist(stars[j][0],stars[j][1],stars[k][0],stars[k][1])
                    l.append([d,k])
            l=sorted(l,key=lambda x: x[0])
            if(len(l)>1):
                for co in l:
                    if(np.all(pathPerStars[j]!=co[1])):
                        if(np.all(np.array(pathPerStars2[j])!=co[1])):
                            if(co[0]<1.3*l[0][0]):
                                for m in pathPerStars[j]:
                                    di=dist(stars[m][0],stars[m][1],stars[co[1]][0],stars[co[1]][1])
                                    if(di<1.0*l[0][0]):
                                        break
                                else:
                                    for m in pathPerStars2[j]:
                                        di=dist(stars[m][0],stars[m][1],stars[co[1]][0],stars[co[1]][1])
                                        if(di<1.0*l[0][0]):
                                            break
                                    else:
                                        path2.append([j,co[1]])
                                        pathPerStars2[j].append(co[1])
                                        pathPerStars2[co[1]].append(j)

doStars()
doConst()
addPath()
scale=1300
out=Image.new("1",(math.floor(2*np.pi*scale),math.floor(np.pi*scale)))
pixels=out.load()
def slerp(p0,p1):
    pc0=s2c(p0)
    pc1=s2c(p1)
    omega=np.arccos(np.dot(pc0,pc1))
    t=np.arange(0,1,1/360)
    for i in t:
        point=((np.sin((1-i)*omega)/np.sin(omega))*pc0)+((np.sin(i*omega)/np.sin(omega))*pc1)
        r=np.linalg.norm(point)
        theta=np.arccos(point[2]/r)
        phi=np.arctan2(point[1],point[0])
        p=math.floor(phi*scale)
        t=math.floor(theta*scale)
        pixels[p,t]=1
for i in paths:
    slerp(stars[i[0]],stars[i[1]])
out.save("o.png")
for i in path2:
    slerp(stars[i[0]],stars[i[1]])
out.save("o3.png")

