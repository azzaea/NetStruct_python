# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 10:49:02 2016

@author: Omer Tzuk <omertz@post.bgu.ac.il>
"""
import numpy as np
from scipy import stats
import igraph
#import h5py as h5

class NetStruct(object):
    def __init__(self,data,area=None,ind=None):
        self.data = data
        self.npop , num_columns = data.shape
        self.nloci = int(num_columns/2)
        if area is not None:
            self.area=area
        if ind is not None:
            self.ind=ind
        self.calc_allele_freq()
        self.createMatrix()

    def calc_allele_freq(self):
        max_l = np.max(self.data)
        freq  = np.zeros((self.nloci,max_l+1))
        for l in range(self.nloci):
            locus=np.concatenate((self.data[:,l*2],self.data[:,l*2+1]))
            count=np.bincount(np.append(locus,max_l))
            count[max_l]-=1
            zeros=count[0]
            count[0]=0
            freq[l]= count/float((2*self.npop)-zeros)
        self.freq_allele = freq

    def buildGDmatrix(self):
        A = np.zeros((self.npop,self.npop))
        for i in np.arange(self.npop):
            for j in np.arange(i+1,self.npop):
                A[i,j]=self.calc_edge(i,j)
        self.A = A + A.T
        self.A_graph = igraph.Graph.Adjacency(self.A.tolist())
        
    def Athreshold(self,threshold):
        return stats.threshold(self.A, threshmin=threshold,newval=0)

    def calc_edge(self,i,j):
        Sij = np.empty(self.nloci)
        nzeros=0
        for l in range(self.nloci):
            a=self.data[i,l*2]
            b=self.data[i,l*2+1]
            c=self.data[j,l*2]
            d=self.data[j,l*2+1]
            if any([a,b,c,d])==0: nzeros+=1
            Iac = int(a==c)
            Iad = int(a==d)
            Ibc = int(b==c)
            Ibd = int(b==d)
            fa=self.freq_allele[l][self.data[i,l*2]]
            fb=self.freq_allele[l][self.data[i,l*2+1]]
            Sij[l]=(1.0/4)*((1.0-fa)*(Iac+Iad)+(1.0-fb)*(Ibc+Ibd))
        if nzeros==self.nloci:
            Sijtot=0
        else:
            Sijtot=(1.0/(self.nloci-nzeros))*np.sum(Sij)
        return Sijtot


def readfile(fname):
    with open(fname) as f:
       ncols = len(f.readline().split(','))
    area = np.loadtxt(fname, delimiter=',', usecols=[0],dtype=str)
    ind  = np.loadtxt(fname, delimiter=',', usecols=[1],dtype=int)
    data = np.loadtxt(fname, delimiter=',', usecols=range(2,ncols),dtype=int)
    return data,area,ind

def main(args):
    print args.fname
    global test
    data,area,ind=readfile(args.fname)
    test = NetStruct(data,area,ind)

def add_parser_arguments(parser):
    parser.add_argument('--csvfile', type=str, nargs='?',
                        default='wildass4pops.csv',
                        dest='fname',
                        help='input file')
    parser.add_argument('--outputfile', type=str, nargs='?',
                        default='test',
                        dest='outfname',
                        help='output file')
    return parser


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(prog='PROG', usage='%(prog)s [options]')
    parser = add_parser_arguments(parser)
    args = parser.parse_args()
    main(args)