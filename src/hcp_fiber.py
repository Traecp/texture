"""
Forked from var_gam_fiber.py to extend to more general BCC fibers.
- gamma, alpha, eta, and epsilon fibers.

## variable typical BCC rolling components

# (hkl) // ND, random vector // RD
# (uvw) // RD, random vector // ND
# (xyz) // TD, random vector // RD


## --------------------------------------------------------------- ##
# Addition of HCP ideal textures to study FLD of AZ31 (20151028)
## --------------------------------------------------------------- ##
** Casting leads to 'Basal' fiber
** Basal fiber -- [0,0,0,1] // ND fiber??
   (0,0,1) // ND
** Wrought magnesium (extrusion?)
- (1,0,-1,0) // ED fiber
  -> (1,0,0) // ED

** Doublets of (0002) tilted from ND
** Doughnuts of (0002) with varying tilting angle from ND

Ref #1 Superior light metals by texture engineering: Optimized aluminum and
        magnesium alloys for automotive applications
        J. Hirsch, T. Al-Samman, Acta Mat (2013)
Ref #2 Communication with Dr. Dirk Steglich Oct 30, 2015
"""

import numpy as np
import random, upf
from euler import euler
gauss = random.gauss
expov = random.expovariate
logno = random.lognormvariate
norma = random.normalvariate
from sym import __mmm__ as mmm
from bcc_rolling_fiber import gen_gr_fiber,\
    nd_rot, rd_rot, td_rot, rot_vectang
from text import miller2mat, miller2mat_RT

def basal_fib(iopt=0):
    """
    Basal fibers along ND (cast)
    Basal fibers along ED (extrusion)
    """
    if iopt==0:
        hkl = [0,0,1] ## major (basal) // ND
        uvw = [0,1,0] ## minor         // RD
        return hkl, uvw
    elif iopt==1:
        uvw = [0,0,1] ## major // ED
        xyz = [1,1,0] ## minor // TD
        return xyz, uvw

def gen_gr_fiber(th,sigma,mu,iopt,tilt):
    """
    Arguments
    =========
    th   =  7.
    sigma = 15.
    iopt  =  0 (basal//ND); 1 (basal//ED)
    """
    hkl, uvw = basal_fib(iopt)
    if iopt==0:
        g_casa = miller2mat(hkl,uvw)
        g_sasa = nd_rot(th)
    elif iopt==1:
        g_casa = miller2mat_RT(uvw=uvw,xyz=hkl)
        g_sasa = rd_rot(th)
    g = np.dot(g_casa,g_sasa)
    if tilt!=0:
        g_tilt = rd_rot(tilt)
        g = np.dot(g_tilt.T,g)

    dth = gauss(mu=mu, sigma=sigma)
    return rot_vectang(th=dth, r=g)

def main(ngrains=100,sigma=15.,c2a=1.6235,mu=0.,
         prc='cst',isc=False,tilt_1=0.,
         tilts_about_ax1=0.,tilts_about_ax2=0.):
    """
    Arguments
    =========
    ngrains = 100
    sigma   = 15.
    c2a     = 1.6235
    prc     = 'cst' or 'ext'
    tilts_about_ax1   = 0.   -- Systematic tilting abount axis 1
    tilts_about_ax2   = 0.   -- Systematic tilting abount axis 2
    tilt_1  = 0.   -- Tilt in the basis pole. (systematic tilting away from ND)
    """
    if isc:
        h  = mmm()
    else:
        h=np.array([np.identity(3)])
    gr = []
    for i in xrange(ngrains):
        dth = random.uniform(-180., 180.)
        if prc=='cst':   g = gen_gr_fiber(th=dth,sigma=sigma,mu=mu,tilt=tilt_1,iopt=0) # Basal//ND
        elif prc=='ext': g = gen_gr_fiber(th=dth,sigma=sigma,mu=mu,tilt=tilt_1,iopt=1)  # Basal//ED
        else:
            raise IOError, 'Unexpected option'
        for j in xrange(len(h)):
            temp = np.dot(g,h[j].T)

            ## tilts_about_ax1
            if abs(tilts_about_ax1)>0:
                g_tilt = rd_rot(tilts_about_ax1)
                temp = np.dot(temp,g_tilt.T)
            ## tilts_about_ax2?
            elif abs(tilts_about_ax2)>0:
                g_tilt = td_rot(tilts_about_ax2)
                temp = np.dot(temp,g_tilt.T)
            elif abs(tilts_about_ax2)>0 and abs(tilts_about_ax2)>0:
                raise IOError, 'One tilt at a time is allowed.'

            phi1,phi,phi2 = euler(a=temp, echo=False)
            gr.append([phi1,phi,phi2,1./ngrains])

    mypf=upf.polefigure(grains=gr,csym='hexag',cdim=[1,1,c2a])
    mypf.pf_new(poles=[[0,0,0,2],[1,0,-1,0],[1,0,-1,2]],cmap='jet')
    return np.array(gr)


def gen_file(lab='',ngr=None):
    fn='mg_textures_%5.5i_%s.cmb'%(ngr,lab)
    f = open(fn,'w')
    f.write('** Textures for Magensium alloys\n')
    f.write('** Generated by texture package:\n')
    f.write('** https://github.com/youngung/texture\n')
    return f

def write_gr(f,gr):
    f.write('B %i\n'%len(gr))
    for i in xrange(len(gr)):
        f.writelines('%9.3f %9.3f %9.3f %13.4e\n'%(
            gr[i][0],gr[i][1],gr[i][2],gr[i][3]))
    f.close()

def app(ngr=100,c2a=1.6235):
    """
    Application for FLD-Mg paper
    Create a set of polycrystals

    ## ZE10
    1) Small doughnut
    2) Big dougnut

    ## AZ31
    1) double let (tilt of 30 degree)
    1) double let (tilt of 50 degree)

    Arguments
    ---------
    ngr=100
    c2a=1.6235 c2a ratio for HCP structure
    """
    import matplotlib.pyplot as plt

    ## small donuts
    # plt.gcf().clf()
    grs = main(mu=0,ngrains=ngr,tilt_1=30.,sigma=15)
    plt.gcf().savefig('small_doughnut.pdf',bbox_inches='tight')
    plt.gcf().clf()
    f = gen_file(lab='sm_doughnut',ngr=ngr)
    write_gr(f,grs)

    ## Big donuts
    grs = main(mu=0,ngrains=ngr,tilt_1=50.,sigma=15)
    plt.gcf().savefig('big_doughnut.pdf',bbox_inches='tight')
    plt.gcf().clf()
    f = gen_file(lab='big_doughnut',ngr=ngr)
    write_gr(f,grs)

    ## twin tilts (30).
    gr1=main(mu=0,ngrains=ngr/2,tilts_about_ax1=30.,sigma=45)
    plt.gcf().clf()
    gr2=main(mu=0,ngrains=ngr/2,tilts_about_ax1=-30.,sigma=45)
    plt.gcf().clf()
    grs =[]
    for i in xrange(len(gr1)):
        grs.append(gr1[i])
        grs.append(gr2[i])
    grs=np.array(grs)
    mypf=upf.polefigure(grains=grs,csym='hexag',cdim=[1,1,c2a])
    mypf.pf_new(poles=[[0,0,0,1],[1,0,-1,0],[1,0,-1,2]],cmap='jet')
    plt.gcf().savefig('t30.pdf',bbox_inches='tight')
    f = gen_file(lab='dbl_lets_30',ngr=ngr)
    write_gr(f,grs)

    ## twin tilts (50).
    gr1=main(mu=0,ngrains=ngr/2,tilts_about_ax1=50.,sigma=45)
    plt.gcf().clf()
    gr2=main(mu=0,ngrains=ngr/2,tilts_about_ax1=-50.,sigma=45)
    plt.gcf().clf()
    gr =[]
    for i in xrange(len(gr1)):
        gr.append(gr1[i])
        gr.append(gr2[i])
    gr=np.array(gr)
    mypf=upf.polefigure(grains=gr,csym='hexag',cdim=[1,1,c2a])
    mypf.pf_new(poles=[[0,0,0,1],[1,0,-1,0],[1,0,-1,2]],cmap='jet')
    plt.gcf().savefig('t50.pdf',bbox_inches='tight')
    plt.gcf().clf()
    f = gen_file(lab='dbl_lets_50',ngr=ngr)
    write_gr(f,gr)

if __name__=='__main__':
    app(ngr=8000)
