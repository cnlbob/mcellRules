# mcellRules

## Installation

- In build folder, run `python requirements.py`. This file will download and
  compile, bionetgen, nfsim, nfsimCinterface, and MCell. (May need
  troubleshooting)
- Create a file called mcellr.yaml in the mcellRules directory.
  - Set the path to bionetgen, which should be
    ./mcellRules/build/bionetgen/bng2/BNG2.pl.
  - Set the "libpath" which should be in ./mcellRules/build/mcell/lib if you
    ran requirements.py.
  - Look at mcellr.yaml.template for a reference.

## Testing

- Download the FCERI compartmental model example (files available here:
  https://drive.google.com/file/d/0B5fuCwEDXeVbZHBFQnBpT2JQSnM/view?usp=sharing)
- Extract the zip to the mcellRules directory.
- Run the following command: `python mdlr2mdl.py -ni
  ./required_fceri_files/fceri.mdlr -o ./required_fceri_files/fceri_mdl`
  (use Python 2, not 3, for this part).
- This will create the following files within the required_fceri_files
  directory:
  - fceri.mdlr.xml
  - fceri.mdlr_total.xml
  - fceri_mdl.seed.mdl
  - tfceri_mdl.reactions.mdl
  - fceri_mdl.output.mdl
  - fceri_mdl.molecules.mdl
  - fceri_mdl.main.mdl
- Now use the following command to run newly created mdl file:
  `./build/mcell/build/mcell ./required_fceri_files/fceri_mdl.main.mdl -n
  ./required_fceri_files/fceri.mdlr_total.xml`
- This will create the following output files in the main mcellRules directory: 
  - fceri.mdlr_total.xml.gdat
  - fceri.mdlr_total.xml_reactions.gdat
