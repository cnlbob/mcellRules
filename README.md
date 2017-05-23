# mcellRules

## Installation

- In build folder, run requirements.py. This file will download and compile,
  nfsim, nfsimCinterface, and mcell. (May need troubleshooting)
- Download a recent version of bionetgen.
- Update the paths in mcellr.yaml
  - Currently, paths are hard coded and the bngl and mdlr file should be in the
    mcellRules directory. 

## Testing

- Download the FCERI compartmental model example (files available here:
  https://drive.google.com/file/d/0B5fuCwEDXeVbZHBFQnBpT2JQSnM/view?usp=sharing)
- Move fceri.mdlr file and fceri.mdlr.bngl file to mcellRules directory and run
  the following command: `python mdlr2mdl.py -ni fceri.mdlr -o fceri_mdl` (use
  Python 2, not 3, for this part).
- This will create the following files:
  - fceri.mdlr.xml
  - fceri.mdlr_total.xml
  - fceri_mdl.seed.mdl
  - tfceri_mdl.reactions.mdl
  - fceri_mdl.output.mdl
  - fceri_mdl.molecules.mdl
  - fceri_mdl.main.mdl

Note: Currently, there is a small bug in the parser. Therefore, you need to
manually add “{“ and “}” to modify surface regions block in main.mdl file. In
other words, change this:

    MODIFY_SURFACE_REGIONS{
        EC[wall]
        SURFACE_CLASS = reflect
        EC[ALL]
        SURFACE_CLASS = reflect
        CP[PM]
        SURFACE_CLASS = reflect
        CP[ALL]
        SURFACE_CLASS = reflect
    }

To this:

    MODIFY_SURFACE_REGIONS{
        EC[wall] {
        SURFACE_CLASS = reflect
      }
        EC[ALL] {
        SURFACE_CLASS = reflect
      }
        CP[PM] {
        SURFACE_CLASS = reflect
      }
        CP[ALL] {
        SURFACE_CLASS = reflect
      }
    }


- Move the DEFINE_SURFACE_CLASSES block before the MODIFY_SURFACE_REGIONS
  block.
- Now use the following command to run newly created mdl file:
  `./build/mcell/build/mcell fceri_mdl.main.mdl -n fceri.mdlr_total.xml`
- This will create the following output files: 
  - fceri.mdlr_total.xml.gdat
  - fceri.mdlr_total.xml_reactions.gdat
