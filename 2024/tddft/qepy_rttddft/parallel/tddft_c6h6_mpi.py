#!/usr/bin/env python
# coding: utf-8

# In[1]:


import qepy
from qepy.driver import Driver
from qepy.io import QEInput

from scipy.optimize import minimize
try:
    from mpi4py import MPI
    comm=MPI.COMM_WORLD
except:
    comm=None


scf_options = {
    '&control': {'calculation': "'scf'",
                 'outdir': "'tmp'",
                 'prefix': "'c6h6'",
                 'pseudo_dir': "'../'",
                 'restart_mode': "'from_scratch'",
                 'tprnfor': True,
                 'tstress': False},
    '&electrons': {'conv_thr': 1e-10,
                   'diagonalization': "'david'"},
    '&system': {'celldm(1)': 24.45306579840016,
                'celldm(2)': 1.0,
                'celldm(3)': 0.8,
                'ecutwfc': 20,
                'ibrav': 8,
                'nat': 12,
                'nosym': True,
                'ntyp': 2},
    'atomic_positions angstrom': ['H   3.97999999999988   5.00000000000000   3.50000000000000',
                                  'C   5.07999999999987   5.00000000000000   3.50000000000000',
                                  'C   5.77500000000000   6.20377531126040   3.50000000000000',
                                  'H   5.22500000000007   7.15640325542330   3.50000000000000',
                                  'C   5.77500000000000   3.79622468873960   3.50000000000000',
                                  'H   5.22500000000007   2.84359674457670   3.50000000000000',
                                  'C   7.16500000000000   6.20377531126040   3.50000000000000',
                                  'H   7.71499999999993   7.15640325542330   3.50000000000000',
                                  'C   7.16500000000000   3.79622468873960   3.50000000000000',
                                  'H   7.71499999999993   2.84359674457670   3.50000000000000',
                                  'C   7.86000000000013   5.00000000000000   3.50000000000000',
                                  'H   8.96000000000012   5.00000000000000   3.50000000000000'],
    'atomic_species': ['C    12.00000  C.pz-vbc.UPF', 'H     1.00000  H.pz-vbc.UPF'],
    'k_points automatic': ['1 1 1    0 0 0'],
}


# In[3]:


tddft_options = {
    '&inputtddft': {'dt': 2.0,
                    'e_direction': 1,
                    'job': "'optical'",
                    'l_tddft_restart': False,
                    'nstep': 5000,
                    'prefix': "'c6h6'",
                    'tmp_dir': "'tmp/'"},
}


# In[4]:


# Write the options to input files for comparison with traditional command way
scf_in = 'C6H6.scf.in'
tddfpt_in= 'C6H6.tddft.in'
QEInput().write_qe_input(scf_in, qe_options=scf_options, prog='pw')
QEInput().write_qe_input(tddfpt_in, qe_options=tddft_options, prog='cetddft')


# In[5]:


additional_files = {
    'H.pz-vbc.UPF' : 'https://pseudopotentials.quantum-espresso.org/upf_files/H.pz-vbc.UPF',
    'C.pz-vbc.UPF' : 'https://pseudopotentials.quantum-espresso.org/upf_files/C.pz-vbc.UPF',
}
from dftpy.formats import download_files
download_files(additional_files)


driver = Driver(scf_in, task='scf', logfile='tmp.scf.out', comm=comm)
driver.scf()
driver.save()
driver = Driver(tddfpt_in, task='optical', logfile='tmp.tddft.out', iterative=True, comm=comm)
max_steps = 100
for istep in range(max_steps):
    driver.diagonalize() # driver.propagate()
    print("\r", end="")
    print(f"Progress: [{istep+1}/{max_steps}]", "|" * (istep*50 // max_steps), end="", flush=True)
