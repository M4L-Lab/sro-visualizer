from itertools import combinations_with_replacement
import numpy as np
from ase.io import read, write
from ase.data import atomic_numbers, atomic_masses
from ase.visualize import view
from ase.neighborlist import neighbor_list
from collections import Counter
from collections import defaultdict
from pathlib import Path


class SRO:
    def __init__(self, atoms, cutoffs, shell_weights) -> None:
        cutoffs.sort(reverse=True)
        self.atoms = atoms
        self.cutoffs = cutoffs
        self.shell_weights=shell_weights
        self.elements = list(self.atoms.symbols)
        self.atom_dict = {k: v for k, v in enumerate(self.elements)}
        self.atom_ratio = {
            key: Counter(self.elements)[key] / sum(Counter(self.elements).values())
            for key in Counter(self.elements).keys()
        }
        self._total_bond = []
        self.ndatas = self.get_neighbor_count()

    def get_neighbor_count(self):
        nth_shell_counts = []
        for cutoff in self.cutoffs:
            i, j = neighbor_list("ij", self.atoms, cutoff)
            self._total_bond.append(len(i))
            data = defaultdict(list)
            for p, q in zip(i, j):
                data[self.atom_dict[p]].append(self.atom_dict[q])
            nth_shell_counts.append({key: Counter(data[key]) for key in data.keys()})
        
        # print(len(nth_shell_counts))

        # for idx in range(len(nth_shell_counts) - 1):
        #     for key in nth_shell_counts[idx].keys():
        #         nth_shell_counts[idx][key].subtract(nth_shell_counts[idx + 1][key])
        return nth_shell_counts

    def sro_AB(self, A, B):
        sros = []
        for shell_number in range(len(self.cutoffs)):
            avg_sro=0
            k=len(self.cutoffs)-shell_number-1
            R_AB_random = self.atom_ratio[A] * self.atom_ratio[B] * self._total_bond[k]
            R_AB_mc = self.ndatas[k][A][B]
            sros.append(np.round((1 - R_AB_mc / R_AB_random),3))
        
        avg_sro=(sros[0]*self.shell_weights[0]+sros[1]*self.shell_weights[1])/(self.shell_weights[0]+self.shell_weights[1])
        sros.append(np.round(avg_sro,3))
        return sros
    
    def sort_by_atomic_weight(self, element1, element2):
        # Get the atomic numbers of the elements
        atomic_weight1 = atomic_masses[atomic_numbers[element1]]
        atomic_weight2 = atomic_masses[atomic_numbers[element2]]
        
        # Sort the elements by their atomic weight
        if atomic_weight1 < atomic_weight2:
            return element1, element2
        else:
            return element2, element1

    def get_all_sro(self, elements_list=None):
        sro_data = {}
        if elements_list is None:
            elements_pair = combinations_with_replacement(self.elements, 2)
        else:
            elements_pair = combinations_with_replacement(elements_list,2)
        
        for A, B in elements_pair:
            A,B=self.sort_by_atomic_weight(A, B)
            sro1 = self.sro_AB(A, B)
            sro_data[f"{A}{B}"] = sro1
    
        return sro_data

    def write_sro(self,sro_data,filename):
        with open(filename, "w") as f:
            for key, value in sro_data.items():
                value = list(np.around(np.array(value), 4))
                f.write(f"{key} {' '.join(map(str,value))}\n")
