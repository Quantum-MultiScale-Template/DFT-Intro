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
conf = read_conf('./qeks.ini')
graphtopo = conf2init(conf, pmi.size > 0)
#-----------------------------------------------------------------------
from ase.io.trajectory import Trajectory
from ase import units
from ase.optimize import BFGS, LBFGS, FIRE
from ase.optimize.sciopt import SciPyFminBFGS, SciPyFminCG
from ase.constraints import FixBondLength

atoms = ase.io.read("./water_64_nacl_bond.xyz",format='extxyz')

calc = eDFTpyCalculator(config = conf, graphtopo = graphtopo)
atoms.set_calculator(calc)

trajfile = 'opt.traj'
opt = BFGS(atoms,
        trajectory = trajfile, logfile = 'opt.log')
opt.run(fmax = 0.02,steps=1000)
traj = Trajectory(trajfile)
ase.io.write('opt.xyz', traj[-1])
