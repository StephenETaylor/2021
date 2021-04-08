#!/usr/bin/env python3
"""
    accepts a vector file and a pathname to a relation, and 
    produces a plot file.

"""

import math
import numpy as np
from scipy import linalg as LA
import os.path
from PIL import Image
#import rankPairs # removed, believed to be unused
import sys
import vectorstuff as vs


white,red,green,blue = [255,255,255],[255,0,0],[0,255,0],[0,0,255]
class p:
    """
        class to build, hold, and display a square image.
        imagearray = p(pixelwidth)
    """
    def __init__(self,wid=1024):
        self.iw, self.scale, self.pzx, self.pzy = 0,0,0,0
        self.imagemin, self.imagemax = None,None
        self.imagebot, self.imagetop = None,None
        self.vscale, self.hscale = None, None # just planning ahead...
        self.foreground = white
        # set up file to build image
        self.pixelwidth = wid
        self.image = None

        # set up image array, pixelwidth by pixelwidth array of rdb values
        self.imageArray = np.zeros(shape=(self.pixelwidth, self.pixelwidth, 3),
                            dtype=np.uint8)

    def rescale(self,p):
        """
            calls to rescale recompute scale factors for image, so that
                e.g.  a range of [-0.014 .. +0.28 ]
                can be displayed in a width of pixelwidth pixels
            rescale can be called multiple times, but data
            already in the array is not moved, so that data subsequently 
            added may have a different scale.
            intended to be used by looping over an array before displaying any 
            of it.

        """
        #global iw, scale, pzx, pzy, imagemin, imagemax, imagetop, imagebot
        x,y = p
        recompute = False
        if None == self.imagemin or x < self.imagemin:
            self.imagemin = x
            recompute = True
        if None == self.imagemax or x > self.imagemax:
            self.imagemax = x
            recompute = True
        if None == self.imagebot or y < self.imagebot:
            self.imagebot = y
            recompute = True
        if None == self.imagetop or y > self.imagetop:
            self.imagetop = y
            recompute = True

        if recompute:
            self.pzy = self.pixelwidth/2
            self.pzx = self.pixelwidth/2
            #hscale = min(pixelwidth/(-imagemin)/2, pixelwidth/imagemax/2)
            if self.imagemin == None and self.imagemax == None:
                self.hscale = self.pixelwidth
            elif self.imagemin == None:
                self.hscale = self.pixelwidth/self.imagemax/2
            elif self.imagemax == None:
                if self.imagemin > 0 :
                    #print('forgot to code case when least coordinate is > 0')
                    self.pzx = 0
                    self.hscale = self.pixelwidth/self.imagemax # this won't work, cant happen
                self.hscale = self.pixelwidth/2/(-self.imagemin)
            else:
                if self.imagemin >= 0 :
                    #print('forgot to code case when least coordinate is > 0')
                    self.pzx = 0
                    if self.imagemax !=0:
                        self.hscale = self.pixelwidth/self.imagemax # this won't work, cant happen
                    else:
                        self.hscale = 1
                elif self.imagemax < 0:
                    self.hscale = self.pixelwidth/(-self.imagemin)/2
                else:
                    self.hscale = min(self.pixelwidth/(-self.imagemin)/2, 
                                        self.pixelwidth/self.imagemax/2)

            #vscale = min(pixelwidth/(-imagebot)/2, pixelwidth/imagetop/2)
            if self.imagebot == None and self.imagetop == None: 
                self.hscale = self.pixelwidth
            elif self.imagebot == None:
                self.vscale = self.pixelwidth/self.imagetop/2
            #elif imagetop == None: #imagetop and imagebot: both None or neither
                #if imagebot > 0 :
                #    print('forgot to code case when least coordinate is > 0')
                #    sys.exit(1)
                #vscale = pixelwidth/2/(-imagebot)
            else:
                if self.imagebot >= 0 :
                    #print('forgot to code case when least coordinate is > 0')
                    self.pzy = 0
                    if self.imagetop !=0:
                        self.vscale = self.pixelwidth/self.imagetop
                    else:
                        self.vscale = 1
                elif self.imagetop < 0:
                    self.vscale = self.pixelwidth/(-self.imagebot)/2 
                else:
                    self.vscale = min(self.pixelwidth/(-self.imagebot)/2, 
                                        self.pixelwidth/self.imagetop/2)

            """
            # previously,  can fail if pz* value doesn't match chosen scale
            iw = imagemax-imagemin
            hscale = pixelwidth/iw
            pzx = pixelwidth*(-imagemin)/iw
            ih = imagetop - imagebot
            pzy = pixelwidth*(-imagebot)/ih
            vscale = pixelwidth/iw
            """
            self.scale = min(self.vscale*0.95,self.hscale*0.95)
            if self.scale < 0:
                print (' scale somehow negative!')
                sys.exit(1)
            #scale = min(vscale,hscale)


    def heightcoord(self,ic):
        pc = ic*self.scale + self.pzy
        if pc < 0: 
            pc = 0
        if pc >= self.pixelwidth: 
            pc = self.pixelwidth-1
        return int(pc)

    def widthcoord(self,ic):
        pc = ic*self.scale + self.pzx
        if pc < 0: pc = 0
        if pc >= self.pixelwidth: pc = self.pixelwidth-1
        return int(pc)

    def pixelpoint(self,ip):
        x,y = ip
        a = (self.widthcoord(x),self.heightcoord(y))
#        if a[1] == 1023:
#            exit() # pass
        return a

    def drawpoint(self,p):
        q = self.pixelpoint(p)
        self.drawpixel(q)

    def drawpixel(self,q):
        x,y = q
#        if y == 0 or x == 0 or y == pixelwidth-1 or x == pixelwidth-1:
#            imageArray[y][x] = foreground # pass
        self.imageArray[y][x] = self.foreground

    def drawline(self,p0,p1):
        #global foreground,white,red
        #nonlocal pixelpoint
        x0,y0 = p0
        x1,y1 = p1
        dx = x1-x0
        dy = y1-y0
        for d in range(self.pixelwidth):
            # this could be more efficient; we're almost guaranteed to 
            # rewrite each pixel several times
            nx = (d/self.pixelwidth) * dx + x0
            ny = (d/self.pixelwidth) * dy + y0
            self.drawpoint((nx,ny))
        self.foreground = red
        self.drawsquare(p1)  #drawpoint(p1)
        self.foreground = white

    def setForeground(color):
        self.foreground = color

    def drawsquare(self,p0,r=3):
        """
            draw a square centered at point p, in the foreground color,
            with side 2*r pixels
        """
        q = self.pixelpoint(p0)
        qx, qy = q
        for x in range(max(0,qx-r),min(qx+r,self.pixelwidth-1)):
            for y in range(max(0,qy-r),min(qy+r,self.pixelwidth-1)):
                self.drawpixel((x,y))

    def show(self):
        self.image = Image.fromarray(self.imageArray)
        self.image.show()



def PCA(data, dims_rescaled_data=2, mulout=False):
    """
        This code lifted from:
        https://stackoverflow.com/questions/13224362/principal-component-analysis-pca-in-python

        pass in: data as 2D NumPy array
                     that is data might have shape=(300000,300)
                 desired dimension 
                     defaults to 2 for drawing pictures
                 boolean flag whether to return first item or None
                 
        returns: Three items:
                data transformed into dims_rescaled_data dims/columns 
                    (or None if mulout parameter was True)
                eigenvalues
                transformation_matrix

            individual items of data can be projected into PCA space with 
                data[x] .dot (transformation_matrix)

    """
    m, n = data.shape
    # mean center the data
    data -= data.mean(axis=0)
    # calculate the covariance matrix
    R = np.cov(data, rowvar=False)
    # calculate eigenvectors & eigenvalues of the covariance matrix
    # use 'eigh' rather than 'eig' since R is symmetric, 
    # the performance gain is substantial
    evals, evecs = LA.eigh(R)
    # sort eigenvalue in decreasing order
    idx = np.argsort(evals)[::-1]
    evecs = evecs[:,idx]
    # sort eigenvectors according to same index
    evals = evals[idx]
    toteng = sum(evals)
    pcaeng = sum(evals[:dims_rescaled_data])
    print('pca energy',pcaeng/toteng)
    # select the first n eigenvectors (n is desired dimension
    # of rescaled data array, or dims_rescaled_data)
    evecs = evecs[:, :dims_rescaled_data]
    # carry out the transformation on the data using eigenvectors
    # and return the re-scaled data, eigenvalues, and eigenvectors
    if mulout:
        return np.dot(evecs.T, data.T).T, evals, evecs
    else:
        return None, evals, evecs



if __name__ == '__main__':
    ar = p(1024)
    ar.rescale((0,0)) # scale for the following range...
    ar.rescale((1023,1023))
    marg = 10
    leng = ar.pixelwidth - 2 * marg
    x,y = marg,marg
    for i in range (leng//(2*marg)):
        ar.drawline((x,y),((x+leng),y))
        ar.drawline(((x+leng),y),((x+leng),(y+leng)))
        x,y = x+leng,y+leng
        leng = leng - marg
        ar.drawline((x,y),(x-leng,(y)))
        ar.drawline((x-leng,(y)),((x-leng),(y-leng)))
        x,y = ((x-leng),(y-leng))
        leng = leng - marg
    ar.show()



