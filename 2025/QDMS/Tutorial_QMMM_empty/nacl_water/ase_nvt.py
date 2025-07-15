#!/usr/bin/env python3
import os
from edftpy.api.api4ase import eDFTpyCalculator
from edftpy.config import read_conf
from edftpy.interface import conf2init
from edftpy.mpi import sprint, pmi
import numpy as np
np.random.seed(8888)
############################## initial ##############################
conf = read_conf('./qe.ini')
graphtopo = conf2init(conf, pmi.size > 0)
cell_file = conf["PATH"]["cell"] +os.sep+ conf['GSYSTEM']["cell"]["file"]
#-----------------------------------------------------------------------
import ase.io
import ase.md
from ase.io.trajectory import Trajectory
from ase import units
from ase.md.npt import NPT
from ase.md.langevin import Langevin
from ase.md.nvtberendsen import NVTBerendsen
from ase.md.andersen import Andersen
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution

#atoms = ase.io.read(cell_file)
atoms = ase.io.read('./md.traj')

T = 373.15  # Kelvin

calc = eDFTpyCalculator(config = conf, graphtopo = graphtopo)
atoms.set_calculator(calc)

# MaxwellBoltzmannDistribution(atoms, temperature_K = T, force_temp=True)

dyn = Andersen(atoms, 1.0 * units.fs, temperature_K = T, andersen_prob=0.02)

#step = 12826
step = 1
interval = 1

def printenergy(a=atoms):
    global step, interval
    epot = a.get_potential_energy() / len(a)
    ekin = a.get_kinetic_energy() / len(a)
    sprint("Step={:<8d} Epot={:.5f} Ekin={:.5f} T={:.3f} Etot={:.5f}".format(
            step, epot, ekin, ekin / (1.5 * units.kB), epot + ekin))
    step += interval


dyn.attach(printenergy, interval=1)

traj = Trajectory("md.traj", "a", atoms)
dyn.attach(traj.write, interval=1)

nsteps = 30000
dyn.run(nsteps)
