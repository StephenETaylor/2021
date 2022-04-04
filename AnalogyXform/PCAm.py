#!/usr/bin/env python3
"""
 this code also appears in plotting.py, which is a sensible place to need a PCA, but 
 do not fail to propagate edits between the two source files!
"""
import numpy as np
from scipy import linalg as LA

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


