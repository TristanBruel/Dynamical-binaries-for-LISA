import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib as mpl

import os
from glob import glob


def plot_nBBHs_rhocl():


    ### NBODY7 clusters ###
    nbody7_dir = '../NBODY7-Star-Cluster-Models/new_set_bin1a_compact_share'
    cluster_files = glob(os.path.join(nbody7_dir,'M*.h5'))
    print('Number of NBODY7 clusters:', len(cluster_files))
    nbody7_mass = np.zeros(len(cluster_files))
    nbody7_r = np.zeros(len(cluster_files))
    nbody7_nBBHs = np.zeros(len(cluster_files), dtype=int)
    for n in range(len(cluster_files)):
        f = cluster_files[n]
        nbody7_mass[n] = float(f.split('/M')[1].split('k_')[0]) *1e3
        nbody7_r[n] = float(f.split('rh')[1].split('_')[0])
        with h5py.File(f) as c:
            kw1 = c['compact']['kw1'][:]
            kw2 = c['compact']['kw2'][:]
            record = c['compact']['record_type'][:]
        nbody7_nBBHs[n] = np.sum((kw1==14)&(kw2==14)&(record==2))
    print('Total number of BBH mergers in NBODY7 clusters:', np.sum(nbody7_nBBHs),'\n')

    ### MOCCA clusters ###
    # Escapers #
    mocca_dir = '../MOCCA-Star-Cluster-Models/BBH/Escapers'
    ident, smt0, rh0, tmerge  = np.loadtxt(os.path.join(mocca_dir,'MOCCA_escapers_BBH.dat'), usecols=[0,25,26,58]).T
    unique_ident, indexes = np.unique(ident, return_index=True)
    print('Number of MOCCA clusters (with escaped BBHs):', len(unique_ident))
    mocca_mass = smt0[indexes]
    print('Total number of escaped BBH mergers in MOCCA clusters:', len(ident))
    mocca_nBBHs = np.array([np.sum(tmerge[ident==i]<14e3) for i in unique_ident])
    print('Escaped BBH mergers in MOCCA clusters with tmerge < 14 Gyr:', np.sum(mocca_nBBHs))
    mocca_mass = smt0[indexes]
    mocca_r = rh0[indexes]
    mocca_nBBHs = np.array([np.sum(tmerge[ident==i]<14e3) for i in unique_ident])
    # In-Cluster #
    mocca_dir = '../MOCCA-Star-Cluster-Models/BBH/In-Cluster-Binary-Evolution'
    ident, itype1, ik1i, ik2i = np.loadtxt(os.path.join(mocca_dir,'MOCCA-binevol-BBH.dat'), usecols=[0,4,13,14]).T
    print('Number of MOCCA clusters (with in-cluster BBHs):', len(np.unique(ident)))
    print('Additional number of in-cluster BBH mergers:', np.sum((ik1i==14)&(ik2i==14)&((np.abs(itype1-4)<=1)|(np.abs(itype1-15)<=2))),'\n')
    mocca_nBBHs += np.array([np.sum((ident==i)&(ik1i==14)&(ik2i==14)&((np.abs(itype1-4)<=1)|(np.abs(itype1-15)<=2))) for i in unique_ident])

    ### CMC clusters ###
    cmc_dir = '../CMC-Star-Cluster-Models'
    cluster_file = os.path.join(cmc_dir, 'gridClusters.hdf5')
    with h5py.File(cluster_file) as c:
        CMC_mass = c['Mass'][()]
        CMC_r = c['HalfMassRadius'][()]
        CMC_nBBHs = c['nBBHs'][()]
    print('Number of CMC clusters:', len(CMC_mass))
    print('Total number of BBH mergers in CMC clusters:', np.sum(CMC_nBBHs))


    #####################################
    # Plot your result
    fs = 12
    lw = 1.4
    plt.rcParams['font.size']=fs
    plt.rcParams['font.family']='serif'
    plt.rcParams['font.serif']='cmr10'
    plt.rcParams['mathtext.fontset']='cm'
    plt.rcParams['axes.unicode_minus']=False
    plt.rcParams['axes.formatter.use_mathtext']=True
    plt.rcParams['lines.linewidth']=lw
    plt.rcParams['xtick.labelsize']=fs
    plt.rcParams['ytick.labelsize']=fs
    plt.rcParams['legend.fontsize']=.9*fs
    plt.rcParams['axes.titlesize']=fs


    fig, ax = plt.subplots(figsize=(5,5))

    ### NBODY7 ###
    nbody7_rho = nbody7_mass /(4/3*np.pi*nbody7_r**3)
    ax.scatter(np.log10(nbody7_rho), nbody7_nBBHs,
               marker='o', c='darkorange', s=4**2, zorder=3,
               label='NBODY7 (%i)' %np.sum(nbody7_nBBHs),
               )

    ### MOCCA ###
    mocca_rho = mocca_mass /(4/3*np.pi*mocca_r**3)
    ax.scatter(np.log10(mocca_rho), mocca_nBBHs,
               marker='o', c='royalblue', s=3**2, zorder=2,
               label='MOCCA (%i)' %np.sum(mocca_nBBHs),
               )

    ### CMC ###
    CMC_rho = CMC_mass /(4/3*np.pi*CMC_r**3)
    ax.scatter(np.log10(CMC_rho), CMC_nBBHs,
               marker='o', c='forestgreen', s=2**2, zorder=1,
               label='CMC (%i)' %np.sum(CMC_nBBHs),
               )


    ax.set_xlabel('$\\rm{log}(\\rho_{\\rm{cl}}/\\rm{M}_\\odot\\rm{pc}^3)$')
    #ax.set_xlim(xmin=3., xmax=7.)
    #ax.set_xticks(np.linspace(3.,7.,5))
    ax.set_ylabel('Number of BBH mergers')
    ax.set_yscale('log')
    #ax.set_ylim(ymin=-2.5, ymax=2.5)
    #ax.set_yticks(np.linspace(-2,2,5))

    ax.legend(loc='best')
    ax.set_box_aspect(1)
    ax.set_title('BBH mergers in simulations of star clusters')

    # Save
    plot_dir = '../plots'
    plt.savefig(os.path.join(plot_dir,'nBBHs_rhocl_allsims.png'), dpi=1200, 
                bbox_inches='tight',
                )


##################################################################
### Run it!
###
##################################################################
if __name__ == "__main__":

    plot_nBBHs_rhocl()
    plt.show()
