#!/usr/bin/env python3
# -*- coding: utf-8 -*
# see examples below
# also read all the comments below.

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from operator import itemgetter

class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

class Spheres:
    def __init__(self, shade, center, radius):
        self.shade = shade
        self.center = center
        self.radius = radius

class Boxes:
    def __init__(self, shade, tPmin, tPmax):
        self.shade = shade
        self.tPmin = tPmin
        self.tPmax = tPmax

class Shading:
    def __init__(self, shade):
        self.shade = shade

class LambertianShading:
    def __init__(self, diffuse):
        self.diffuse = diffuse

class PhongShading:
    def __init__(self, diffuse, specular, exponent):
        self.diffuse = diffuse
        self.specular = specular
        self.exponent = exponent

class Lights:
    def __init__(self, point, intensity):
        self.point = point
        self.intensity = intensity

class Cameras:
    def __init__(self, viewPoint, viewDirection, viewUp, viewWidth, viewHeight, projNormal, projDistance):
        self.viewPoint = viewPoint
        self.viewDirection = viewDirection
        self.viewUp = viewUp
        self.viewWidth = viewWidth
        self.viewHeight = viewHeight
        self.projNormal = projNormal
        self.projDistance = projDistance
        
def RayTrace(position, direction, surfaces):
    t = sys.maxsize
    intersects = list()
    count = 0
    for i in range(len(surfaces)):
        s = surfaces[i]
        if s.__class__.__name__ == 'Spheres':
            center = s.center
            radius = s.radius
            
            tm = np.dot(center - position,direction)
            tdif = tm*tm - (np.dot(center-position,center-position) - radius*radius)*np.dot(direction,direction)

            if tdif>0:
                t0 = (tm - np.sqrt(tdif))/np.dot(direction,direction)
                t1 = (tm + np.sqrt(tdif))/np.dot(direction,direction)

                if t0>=0:
                    t = t0
                else:
                    if t1>=0:
                        t = t1

        elif s.__class__.__name__ == 'Boxes':
            tXmin = (s.tPmin[0]-position[0])/direction[0]
            tXmax = (s.tPmax[0]-position[0])/direction[0]
            if tXmax < tXmin:
                tXmin, tXmax = tXmax, tXmin

            tYmin = (s.tPmin[1]-position[1])/direction[1]
            tYmax = (s.tPmax[1]-position[1])/direction[1]
            if tYmax < tYmin:
                tYmin, tYmax = tYmax, tYmin

            tZmin = (s.tPmin[2]-position[2])/direction[2]
            tZmax = (s.tPmax[2]-position[2])/direction[2]
            if tZmax < tZmin:
                tZmin, tZmax = tZmax, tZmin

            if tXmax<0 or tYmax<0 or tZmax<0:
                if tXmax<tYmin or tXmax<tZmin or tYmax<tXmin or tYmax<tZmin or tZmax<tXmin or tZmax<tYmin:
                    continue
            else:
                t = max(tXmin,tYmin,tZmin)
        intersects.append((i,t))
        
    if len(intersects) == 0:
        intersects.append((-1,t))

    intersects.sort(key = itemgetter(1))
    return intersects[0]
    
def Shade(light, surfaces, idx, t, position, direction):
#Shade(tmp[0], ray, viewPoint, surfaceList, tmp[1], lightList)
    ray = position + t * direction

    normal = np.array([.0, .0, .0])
    normal_unit = np.array([.0, .0, .0])
    s = surfaces[idx]

    for s in surfaces:
        if s.__class__.__name__ == 'Spheres':
            normal = ray - s.center
            normal_unit = normal/np.sqrt(np.sum(normal*normal))
        elif s.__class__.__name__ == 'Boxes':
            if abs(ray[0] - s.tPmin[0])<0.00001:
                normal_unit = np.array([-1, 0, 0])
            elif abs(ray[0] - s.tPmax[0])<0.00001:
                normal_unit = np.array([1, 0, 0])
            elif abs(ray[1] - s.tPmin[1])<0.00001:
                normal_unit = np.array([0, -1, 0])
            elif abs(ray[1] - s.tPmax[1])<0.00001:
                normal_unit = np.array([0, 1, 0])
            elif abs(ray[2] - s.tPmin[2])<0.00001:
                normal_unit = np.array([0, 0, -1])
            elif abs(ray[2] - s.tPmin[2])<0.00001:
                normal_unit = np.array([0, 0, 1])

    kd = s.shade.diffuse

    for i in light:
        light = i.point-ray
        light_unit = light/np.sqrt(np.sum(light*light))

        check = RayTrace(i.point, -light_unit, surfaces)
        if check[0] == idx:
            if s.shade.__class__.__name__ == 'LambertianShading':
                X = kd[0]*i.intensity[0]*max(0,np.dot(normal_unit,light_unit))
                Y = kd[1]*i.intensity[1]*max(0,np.dot(normal_unit,light_unit))
                Z = kd[2]*i.intensity[2]*max(0,np.dot(normal_unit,light_unit))
            elif s.shade.__class__.__name__ == 'PhongShading':
                ks = s.shade.specular
                v = -direction
                h = v + light_unit
                h_unit = h/np.sqrt(np.sum(h*h))
                X = kd[0]*i.intensity[0]*max(0,np.dot(normal_unit,light_unit)) + ks[0]*i.intensity[0]*pow(max(0,np.dot(normal_unit,h_unit)),s.shade.exponent)
                Y = kd[1]*i.intensity[1]*max(0,np.dot(normal_unit,light_unit)) + ks[1]*i.intensity[1]*pow(max(0,np.dot(normal_unit,h_unit)),s.shade.exponent)
                Z = kd[2]*i.intensity[2]*max(0,np.dot(normal_unit,light_unit)) + ks[2]*i.intensity[2]*pow(max(0,np.dot(normal_unit,h_unit)),s.shade.exponent)

    res = Color(X,Y,Z)
    #if(X!=0 or Y!=0 or Z!=0): print(X, Y, Z)
    res.gammaCorrect(2.2)
    return res.toUINT8()
    

def main():


    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    viewDir=np.array([0,0,-1]).astype(np.float)
    viewUp=np.array([0,1,0]).astype(np.float)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=1.0
    intensity=np.array([1,1,1]).astype(np.float)  # how bright the light is.
    print(np.cross(viewDir, viewUp))

    imgSize=np.array(root.findtext('image').split()).astype(np.int)

    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float)
        if(c.findtext('viewDir')):
            viewDirection = np.array(c.findtext('viewDir').split()).astype(np.float)
        if(c.findtext('projNormal')):
            viewProjNormal = np.array(c.findtext('projNormal').split()).astype(np.float)
        if(c.findtext('viewUp')):
            viewUp = np.array(c.findtext('viewUp').split()).astype(np.float)
        if(c.findtext('projDistance')):
            projDistance = np.array(c.findtext('projDistance').split()).astype(np.float)
        if(c.findtext('viewWidth')):
            viewWidth=np.array(c.findtext('viewWidth').split()).astype(np.float)
        if(c.findtext('viewHeight')):
            viewHeight = np.array(c.findtext('viewHeight').split()).astype(np.float)

    shadeList = []
    for c in root.findall('shader'):
        diffuseColor_c=np.array(c.findtext('diffuseColor').split()).astype(np.float)
        if(c.get('type') == 'Lambertian'):
            diffuse = np.array(c.findtext('diffuseColor').split()).astype(np.float)
            shadeList.append((c.get('name'),LambertianShading(diffuse)))
        elif(c.get('type') == 'Phong'):
            diffuse = np.array(c.findtext('diffuseColor').split()).astype(np.float)
            specular = np.array(c.findtext('specularColor').split()).astype(np.float)
            exponent = float(c.findtext('exponent'))
            shadeList.append((c.get('name'),PhongShading(diffuse, specular, exponent)))

            
        print('name', c.get('name'))
        print('diffuseColor', diffuseColor_c)

    surfaceList = []
    for c in root.findall('surface'):
        ref = c.find('shader').get('ref')
        for s in shadeList:
            if(s[0]==ref):
                shade1 = s[1]

        if(c.get('type') == 'Sphere'):
            center = np.array(c.findtext('center').split()).astype(np.float)
            radius = float(c.findtext('radius'))
            surfaceList.append(Spheres(shade1, center, radius))

        elif(c.get('type') == 'Box'):
            tPmin = np.array(c.findtext('minPt').split()).astype(np.float)
            tPmax = np.array(c.findtext('maxPt').split()).astype(np.float)
            surfaceList.append(Boxes(shade1, tPmin, tPmax))
        
    lightList = []
    for c in root.findall('light'):
        point = np.array(c.findtext('position').split()).astype(np.float)
        intensity = np.array(c.findtext('intensity').split()).astype(np.float)
        lightList.append(Lights(point, intensity))
    #code.interact(local=dict(globals(), **locals()))  

    # Create an empty image
    channels=3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:,:]=0

    pixel_x = viewWidth / imgSize[0]
    pixel_y = viewHeight / imgSize[1]

    w = viewDirection
    u = np.cross(w, viewUp)
    v = np.cross(w, u)

    w_unit = w / np.sqrt(np.sum(w*w))
    u_unit = u / np.sqrt(np.sum(u*u))
    v_unit = v / np.sqrt(np.sum(v*v))

    start = w_unit * projDistance - u_unit * pixel_x * ((imgSize[0]/2) + 1/2) - v_unit * pixel_y * ((imgSize[1]/2) + 1/2)

    for x in np.arange(imgSize[0]):
        for y in np.arange(imgSize[1]):
            ray = start + u_unit*x*pixel_x + v_unit*y*pixel_y
            tmp = RayTrace(viewPoint,ray,surfaceList)
            
            if(tmp[1] != -1):
                img[y][x] = Shade(lightList, surfaceList, tmp[0], tmp[1], viewPoint, ray)
                #def Shade(light, surfaces, idx, t, position, direction):
            else:
                img[y][x] = np.array([0, 0, 0])
    
    rawimg = Image.fromarray(img, 'RGB')
    rawimg.save('out.png')
    #rawimg.save(sys.argv[1]+'.png')
    
if __name__=="__main__":
    main()
