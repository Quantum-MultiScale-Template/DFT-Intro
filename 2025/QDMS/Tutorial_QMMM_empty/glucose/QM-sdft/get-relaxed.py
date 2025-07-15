from ase.io.trajectory import Trajectory

trajfile = 'opt.traj'
traj = Trajectory(trajfile)

i = 101
for struct in traj:
    struct.write(f'../../for_traj_p4/geometries/{i:03d}.xyz')
    i = i+1
