#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from dftpy.formats import io
import ase
import ase.io

from dftpy.grid import DirectGrid
from dftpy.field import DirectField
from dftpy.functional import Functional, TotalFunctional
from dftpy.td.propagator import Propagator
from dftpy.td.hamiltonian import Hamiltonian
from dftpy.utils.utils import calc_rho, calc_j
from dftpy.td.utils import initial_kick
from dftpy.ions import Ions
from dftpy.optimization import Optimization
from dftpy.functional.external_potential import ExternalPotential
from dftpy.optimize import Dynamics
from dftpy.mpi import MP, sprint

mp = MP(parallel=True)

inputfile = '../Ag20_rotate.vasp'
atoms = ase.io.read(inputfile, format='vasp')
nr = [100, 100, 100]

path = '../Challenge/OEPP/OEPP/UPF/'
PP_list = {'Ag':path+'Ag_OEPP_PZ.UPF'}
ions = Ions.from_ase(atoms)
grid = DirectGrid(ions.cell, nr, mp=mp, full=True)
pseudo = Functional(type='PSEUDO', grid=grid, ions=ions, PP_list=PP_list)
rho_ini = DirectField(grid=grid)
rho_ini[:] = ions.get_ncharges() / grid.volume

ke = Functional(type='KEDF',name='TFvW')
xc = Functional(type='XC',name='LDA')
hartree = Functional(type='HARTREE')
totalfunctional = TotalFunctional(KineticEnergyFunctional=ke,
                                XCFunctional=xc,
                                HARTREE=hartree,
                                PSEUDO=pseudo
                                 )
optimization_options = {'econv' : 1e-9,'maxiter' : 100}

opt = Optimization(EnergyEvaluator=totalfunctional, optimization_options = optimization_options,
        optimization_method = 'TN')

rho0 = opt.optimize_rho(guess_rho=rho_ini)

ke.options.update({'y':0})


direction = 0 # 0, 1, 2 means x, y, z-direction, respectively
k = 1.0e-3 # kick_strength in a.u.
psi = initial_kick(k, direction, np.sqrt(rho0))
j0 = calc_j(psi)
interval = 0.002

class Runner(Dynamics):

    def __init__(self, rho0, totalfunctional, k, direction, interval, max_steps):
        super(Runner, self).__init__()
        self.max_steps = max_steps
        self.totalfunctional = totalfunctional
        self.rho0 = rho0
        self.rho = rho0
        self.psi = initial_kick(k, direction, np.sqrt(self.rho0))
        self.j = calc_j(self.psi)
        potential = self.totalfunctional(self.rho0, current=self.j, calcType=['V']).potential
        hamiltonian = Hamiltonian(v=potential)
        self.prop = Propagator(hamiltonian, interval, name='crank-nicholson')
        self.dipole = []
        self.attach(self.calc_dipole)

    def step(self):
        sprint(self.psi.integral(), comm=self.rho.grid.mp)
        self.psi, info = self.prop(self.psi)
        self.rho = calc_rho(self.psi)
        self.j = calc_j(self.psi)
        potential = self.totalfunctional(self.rho, current=self.j, calcType=['V']).potential
        self.prop.hamiltonian.v = potential

    def calc_dipole(self):
        delta_rho = self.rho - self.rho0
        delta_mu = (delta_rho * delta_rho.grid.r).integral()
        sprint(len(self.dipole), delta_mu, comm=self.rho.grid.mp)
        self.dipole.append(delta_mu)


max_steps = 24175
runner = Runner(rho0, totalfunctional, k, direction, interval, max_steps)
for i, run in enumerate(runner.irun()):
    if i%200==0 and i>1:
        t = np.linspace(0, interval * i, i + 1)
        delta_mu = np.asarray([mu for mu in runner.dipole])
        if mp.is_root:
            np.save('./dipole/dipole_'+str(i)+'.npy', np.c_[t[:-1], delta_mu])
