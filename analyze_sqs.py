import os
from pathlib import Path
from datetime import datetime
import re
from sqs2atom import sqs2atoms
from atom2sro import SRO
from collections import defaultdict
import json

class SQS_Analyzer:
    def __init__(self,
                 folder,
                 unit_cell_lattice_constant,
                 cutoffs,
                 weights,
                 write_poscar=True
                 ):
        self.folder=folder
        self.scale=unit_cell_lattice_constant
        self.cutoffs=cutoffs
        self.weights=weights
        self.write_poscar=write_poscar
        self.all_data=[]
    
    
    def calculate_all_sros(self):
        
        pattern = re.compile(r"^bestsqs-\d+\.out$")
        files = Path(self.folder).iterdir()
        
        for file in files:
            file_dict = {}
            if file.is_file() and pattern.match(file.name):  # Check if the filename matches the pattern
                creation_time = os.path.getmtime(file)
                creation_time_human = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d %H:%M:%S')
                # Add filename and its timestamp to the dictionary
                file_dict["name"]=file.name
                file_dict["sqs_id"]=int(file.name.split(".")[0].split("-")[-1])
                file_dict["time"] = creation_time
                file_dict["time_human"]=creation_time_human
                atoms_dict,sro_data=self.calculate_sros(file)
                #file_dict["atoms"]=atoms_dict
                file_dict["sros"]=sro_data
                self.all_data.append(file_dict)
                print(file.name)
                print(creation_time_human)

    def calculate_sros(self, file_name):
        atoms=sqs2atoms(file_name,scale=self.scale,write_POSCAR=self.write_poscar)
        sro=SRO(atoms,self.cutoffs, self.weights)
        sro_data=sro.get_all_sro()
        
        return atoms.todict(), sro_data



if __name__=="__main__":

    folder="./"
    scale=3.13275
    cutoffs = [
        2.9229,
        3.7816,
    ]
    weights=[8,6]
    sqs_analysis=SQS_Analyzer(folder,scale,cutoffs,weights)
    sqs_analysis.calculate_all_sros()
    
    with open("results.json", 'w') as fp:
        json.dump(sqs_analysis.all_data, fp, indent=4)
    
