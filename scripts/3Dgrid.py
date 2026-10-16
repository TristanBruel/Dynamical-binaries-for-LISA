import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib as mpl

import os
from glob import glob


def plot_clusterGrid(Zsun=0.014):


    ### NBODY7 clusters ###
    nbody7_dir = '../NBODY7-Star-Cluster-Models/new_set_bin1a_wdwd_share'
    cluster_files = glob(os.path.join(nbody7_dir,'M*.h5'))
    print('Number of NBODY7 clusters:', len(cluster_files))
    nbody7_mass = np.zeros(len(cluster_files))
    nbody7_r = np.zeros(len(cluster_files))
    nbody7_Z = np.zeros(len(cluster_files))
    for n in range(len(cluster_files)):
        f = cluster_files[n]
        nbody7_mass[n] = float(f.split('/M')[1].split('k_')[0]) *1e3
        nbody7_r[n] = float(f.split('rh')[1].split('_')[0])
        nbody7_Z[n] = float('0.'+f.split('Z')[1].split('_')[0])

    ### MOCCA clusters ###
    ### for now only the escapers, as the other file with in-cluster evolution is much bigger ###
    mocca_dir = '../MOCCA-Star-Cluster-Models/BBH/Escapers'
    ident, smt0, rh0, Z  = np.loadtxt(os.path.join(mocca_dir,'MOCCA_escapers_BBH.dat'), usecols=[0,25,26,56]).T
    print('Number of MOCCA clusters (with escaped BBHs):', len(np.unique(ident)))
    unique_indent, indexes = np.unique(ident, return_index=True)
    mocca_mass = smt0[indexes]
    mocca_r = rh0[indexes]
    mocca_Z = Z[indexes]

    ### CMC clusters ###
    cmc_dir = '../CMC-Star-Cluster-Models'
    cluster_file = os.path.join(cmc_dir, 'gridClusters.hdf5')
    with h5py.File(cluster_file) as c:
        CMC_mass = c['Mass'][()]
        CMC_r = c['HalfMassRadius'][()]
        CMC_Z = c['Metallicity'][()]
    print('Number of CMC clusters:', len(CMC_Z))


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


    fig = plt.figure(figsize=(6.,6.))
    ax = fig.add_subplot(111, projection='3d')

    ### NBODY7 ###
    ax.scatter(np.log10(nbody7_mass),
               np.log10(nbody7_r),
               np.log10(nbody7_Z /Zsun),
               marker='o', c='darkorange', s=4**2, 
               zorder=3, depthshade=False,
               label='NBODY7 (%i)' %len(nbody7_mass),
               )

    ### MOCCA ###
    ax.scatter(np.log10(mocca_mass),
               np.log10(mocca_r),
               np.log10(mocca_Z /Zsun),
               marker='o', c='royalblue', s=3**2,
               zorder=2, depthshade=False,
               label='MOCCA (%i)' %len(mocca_mass),
               )

    ### CMC ###
    ax.scatter(np.log10(CMC_mass),
               np.log10(CMC_r),
               np.log10(CMC_Z /Zsun),
               marker='o', c='forestgreen', s=1**2, 
               zorder=1, depthshade=False,
               label='CMC (%i)' %len(CMC_mass),
               )


    ax.set_xlabel('$\\rm{log}(M_{\\rm{cl}}/\\rm{M}_\\odot)$')
    ax.set_xlim(xmin=3., xmax=7.)
    ax.set_xticks(np.linspace(3.,7.,5))
    ax.set_ylabel('$\\rm{log}(r_{\\rm{hm}}/\\rm{pc})$')
    ax.set_ylim(ymin=-1.5, ymax=2.5)
    ax.set_yticks(np.linspace(-1,2,3))
    ax.set_zlabel('$\\rm{log}(Z_{\\rm{cl}}/\\rm{Z}_\\odot)$')
    ax.set_zlim(zmin=-2.5, zmax=1.)
    ax.set_zticks(np.linspace(-2.,0.,3))

    ax.legend(loc='best')
    #ax.view_init(azim=-60, elev=15)

    # Save
    plot_dir = '../plots'
    plt.savefig(os.path.join(plot_dir,'3Dgrid_allsims.png'), dpi=1200, 
                bbox_inches='tight',
                )


##################################################################
### Run it!
###
##################################################################
if __name__ == "__main__":


    plot_clusterGrid()
    plt.show()
