from ase import Atoms
from ase.io import write
import numpy as np

def read_bestsqs(file):
    """
    Reads the bestsqs.out file and returns the basis vectors, lattice vectors, atomic positions, and element types.
    """
    basis_vectors = []
    lattice_vectors = []
    atomic_positions = []
    atomic_species = []
    
    with open(file, 'r') as f:
        # Read basis vectors (first 3 lines)
        for _ in range(3):
            basis_vectors.append([float(x) for x in f.readline().split()])
        
        # Read lattice vectors (next 3 lines)
        for _ in range(3):
            lattice_vectors.append([float(x) for x in f.readline().split()])
        
        # Read atomic positions and elements (remaining lines)
        for line in f:
            tokens = line.split()
            if len(tokens) < 4:
                continue
            x, y, z = [float(i) for i in tokens[:3]]
            element = tokens[3]
            atomic_positions.append([x, y, z])
            atomic_species.append(element)
    
    basis_vectors = np.array(basis_vectors)
    lattice_vectors = np.array(lattice_vectors)
    atomic_positions = np.array(atomic_positions)
    
    return basis_vectors, lattice_vectors, atomic_positions, atomic_species

def sqs2atoms(file,scale=1.0, write_POSCAR=True):
    basis_vectors, lattice_vectors, atomic_positions, atomic_species=read_bestsqs(file)
    lattice_vectors *=scale
    atomic_positions *=scale
    
    atoms = Atoms(symbols=atomic_species, positions=atomic_positions, cell=lattice_vectors, pbc=True)
    atoms=atoms[atoms.numbers.argsort()]

    if write_POSCAR:
        id=int(file.name.split(".")[0].split("-")[-1])
        write(f"{file}.POSCAR", atoms,direct=True, format='vasp')
    return atoms