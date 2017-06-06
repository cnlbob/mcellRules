# mcellRules

## Overview

MCellR lets you leverage the power of bionetgen's rule based modeling within
the reaction-diffusion simulator MCell.

Using mdlr2mdl.py, you can convert MDLR files into MDL files. MDLR is similar
to MDL except it has bionetgen-style syntax for portions of the molecule
definitions, reactions, releases, and reaction data. After creating the MDL
files using mdlr2mdl.py, the simulation should be run using a special feature
branch of MCell (nfsim_diffusion). As the simulation runs, MCell will call the
NFsim library as needed in order to find reaction partners.

## Installation

- Clone this repository. By default, it will create a folder named "mcellRules".
- In the build folder (mcellRules/build), run `python requirements.py`. This will
  clone and build, bionetgen, nfsim, nfsimCInterface, and MCell. (May need
  troubleshooting)
- Create a file called mcellr.yaml in the mcellRules directory (or copy the file
  mcellr.yaml.template to mcellr.yaml). These are the default paths from running
  requirements.py:
  - bionetgen: './build/bionetgen/bng2/BNG2.pl'
  - libpath: './build/mcell/lib/'
  - mcell: './build/mcell/build/mcell'

## Testing

- Run the following command: `python mdlr2mdl.py -ni
  ./fceri_files/fceri.mdlr -o ./fceri_files/fceri_mdl`
  (use Python 2, not 3, for this part).
- This will create the following files within the fceri_files
  directory:
  - fceri.mdlr.xml
  - fceri.mdlr_total.xml
  - fceri_mdl.seed.mdl
  - tfceri_mdl.reactions.mdl
  - fceri_mdl.output.mdl
  - fceri_mdl.molecules.mdl
  - fceri_mdl.main.mdl
- Now use the following command to run newly created mdl file:
  `./build/mcell/build/mcell ./fceri_files/fceri_mdl.main.mdl -n
  ./fceri_files/fceri.mdlr_total.xml`
- This will create the following output files in the main mcellRules directory: 
  - fceri.mdlr_total.xml.gdat
  - fceri.mdlr_total.xml_reactions.gdat

## Syntax

For a general overview of MDL, please see the [quick reference
guide](http://mcell.org/documentation/qrg/index.html).

MDLR is an extension of MDL using bionetgen style syntax. All of the MDL blocks
(e.g. DEFINE_MOLECULE, DEFINE_REACTIONS, etc) are prefaced with a pound sign
like this:

    #DEFINE_MOLECULES {
      ..
    }

    #DEFINE_REACTIONS {
      ..
    }

### Molecules

For molecules, the names are treated like bionetgen molecules like
Syk(tSH2,l~Y~pY,a~Y~pY) in the following example:

    #DEFINE_MOLECULES
    {
      Syk(tSH2,l~Y~pY,a~Y~pY)
      {
          DIFFUSION_CONSTANT_3D = 8.51e-7 
      }
    }

This example shows a molecule named Syk with three different components (tSH2,
l, and a).  Two of the components (l and a) each have two different states (Y
and pY).
