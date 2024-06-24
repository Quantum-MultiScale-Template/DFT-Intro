#!/usr/bin/env python

import numpy as np
from qepy.driver import Driver


try:
  from mpi4py import MPI
  comm=MPI.COMM_WORLD
except:
  comm=None

qe_options = {
    '&control': {
        'calculation': "'scf'",
        'pseudo_dir': "'./'",
        'outdir': "tmp",
    },
    '&system': {
        'ibrav' : 0,
        'degauss': 0.005,
        'ecutwfc': 30,
        'nat': 1,
        'ntyp': 1,
        'occupations': "'smearing'"
    },
    'atomic_positions crystal': ['Al    0.0  0.0  0.0'],
    'atomic_species': ['Al  26.98 Al.pbe-nl-kjpaw_psl.1.0.0.UPF'],
    'k_points automatic': ['10 10 10 1 1 1'],
    'cell_parameters angstrom':[
        '0.     2.025  2.025',
        '2.025  0.     2.025',
        '2.025  2.025  0.   '],
}


additional_files = ['http://pseudopotentials.quantum-espresso.org/upf_files/Al.pbe-nl-kjpaw_psl.1.0.0.UPF']
from dftpy.formats import download_files
download_files(additional_files)


ecutwfcs = np.arange(10, 40, 5)
energies = []
for ecutwfc in ecutwfcs:
    qe_options['&system']['ecutwfc'] = ecutwfc
    driver = Driver(qe_options=qe_options, logfile=True, comm=comm)
    ene = driver.scf()
    energies.append(ene)
    print(ecutwfc, ene)
    driver.stop()

import matplotlib.pyplot as plt

energies=np.asarray(energies)
plt.plot(ecutwfcs, energies-energies[-1])
plt.xlabel('Kin. Energy Cutoff (Ry)')
plt.ylabel('Total Energy (Ry)')
plt.savefig('ecut_energies.pdf')




