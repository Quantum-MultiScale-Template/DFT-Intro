#!/usr/bin/env python3
import numpy as np
import ase
from edftpy.api.api4ase import eDFTpyCalculator
from edftpy.config import read_conf
from edftpy.interface import conf2init
from edftpy.mpi import sprint, pmi
from ase.constraints import FixAtoms


np.random.seed(8888)
############################## initial ##############################
conf = read_conf('./qmmm.ini')
graphtopo = conf2init(conf, pmi.size > 0)
#-----------------------------------------------------------------------
from ase.io.trajectory import Trajectory
from ase import units
from ase.optimize import BFGS, LBFGS, FIRE
from ase.optimize.sciopt import SciPyFminBFGS, SciPyFminCG
from ase.constraints import FixBondLength

#atoms = None
#atoms = eDFTpyCalculator(config = conf, graphtopo = graphtopo, atoms = atoms).atoms

atoms = ase.io.read("../../pert_4.xyz",format='extxyz')

calc = eDFTpyCalculator(config = conf, graphtopo = graphtopo, atoms=atoms)
atoms.set_calculator(calc)

idx_fx = list(range(24, len(atoms) ,1)) 

c = FixAtoms(indices=idx_fx)
atoms.set_constraint(c)


trajfile = 'opt.traj'
opt = BFGS(atoms,
        trajectory = trajfile, logfile = 'opt.log')
opt.run(fmax = 0.02,steps=100)

#if graphtopo.is_root :
#    traj = Trajectory(trajfile)
#    traj[-1].write('opt.xyz')
