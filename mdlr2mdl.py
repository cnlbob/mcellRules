import argparse
import read_mdl
import write_mdl
from subprocess import call
import split_bngxml
import re
from nfsim_python import NFSim
import os
import read_bngxml
import write_bngxmle as writeBXe
import yaml
import sys


def define_console():
    parser = argparse.ArgumentParser(description='SBML to BNGL translator')
    parser.add_argument(
        '-i', '--input', type=str, help='input MDLr file', required=True)
    parser.add_argument(
        '-n', '--nfsim', action='store_true', help='mcell-nfsim mode')
    parser.add_argument('-o', '--output', type=str, help='output MDL file')
    parser.add_argument(
        '-b', '--bng-executable', type=str,
        help='file path pointing to the BNG2.pl file')
    return parser


def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))


class MDLR2MDL(object):
    '''
    given an mdlr definition this script will get a set of mdl files compatible
    with an nfsim bng-xml definition
    '''
    def __init__(self, configpath):
        with open(configpath, 'r') as f:
            self.config = yaml.load(f.read())
        try:
            self.nfsim = NFSim(
                os.path.join(self.config['libpath'], 'libnfsim_c.so'))
        except OSError:
            print("Cannot open libnfsim_c.so. Please check libpath in "
                  "mcellr.yaml")
            sys.exit(0)

    def process_mdlr(self, mdlrPath):
        '''
        main method. extracts species definition, creates bng-xml, creates mdl
        definitions
        '''
        try:
            nauty_dict = self.xml2hnauty_species_definitions(mdlrPath)
        except OSError:
            print("Cannot open BNG2.pl. Please check bionetgen in mcellr.yaml")
            sys.exit(0)

        # append extended bng-xml to the bng-xml definition (the one that
        # doesn't include seed information)
        bngxmlestr = writeBXe.mergeBXBXe(
            namespace.input + '_total.xml', namespace.input + '_extended.xml')
        with open(mdlrPath + '_total.xml', 'w') as f:
            f.write(bngxmlestr)

        xmlspec = read_bngxml.parseFullXML(namespace.input + '.xml')
        # write out the equivalent plain mdl stuffs
        mdlDict = write_mdl.construct_mcell(
            xmlspec, namespace.input, finalName.split(os.sep)[-1], nauty_dict)
        write_mdl.write_mdl(mdlDict, finalName)

    def tokenize_seed_elements(self, seed):
        # extract species names
        seedKeys = re.findall(
            'concentration="[0-9a-zA-Z_]+" name="[_0-9a-zA-Z@:(~!),.]+"', seed)
        seedKeys = [re.sub('concentration="([0-9a-zA-Z_]+)" name="([_0-9a-zA-Z@:(~!),.]+)"', '\g<2>;\g<1>', x) for x in seedKeys]

        seedList = seed.split('</Species>')
        seedList = [x.strip() for x in seedList if x != '']
        seedList = [x + '</Species>' for x in seedList]
        seedList = [re.sub('"S[0-9]+"', "S1", x) for x in seedList]
        seedList = [re.sub('concentration="[0-9a-zA-Z_]+"', 'concentration="1"', x) for x in seedList]

        seedList = ['<Model><ListOfSpecies>{0}</ListOfSpecies></Model>'.format(x) for x in seedList]

        # seedDict = {x:y for x, y in zip(seedKeys, seedList)}
        seedDict = {x.split(';')[0]: y for x, y in zip(seedKeys, seedList) if x.split(';')[1] != '0'}
        # print '---', seedDict.keys()
        return seedDict

    def get_names_from_definition_string(self, defStr):
        speciesNames = re.findall('[0-9a-zA-Z_]+\(', defStr)
        return [x[:-1] for x in speciesNames]

    def xml2hnauty_species_definitions(self, inputMDLRFile):
        """
        Temporary function for translating xml bng definitions to nautty
        species definition strings

        it call the nfsim library to get the list of possible complexes in the
        system, however the function right now returns the species in question
        + all molecule types (if we are sending a lone molecule tye as
        initialization it still returns all molecule types), which means the
        list requires filterinng. and the filtering is not pretty

        How to solve: make it so that nfsim returns a more sensible complex
        list (filtering out unrelated molecule types) or create a nauty label
        creation mechanism locally
        """

        # get a bng-xml file
        call([self.config['bionetgen'], '-xml', '-check', inputMDLRFile + '.bngl'])
        # extract seed species defition
        seed, rest = split_bngxml.extractSeedBNG(inputMDLRFile + '.xml')

        # store xml with non-seed sections and load up nfsim library
        with open(namespace.input + '_total.xml', 'w') as f:
            f.write(rest)
        # load up nfsim library
        self.nfsim.init_nfsim(namespace.input + '_total.xml', 0)

        # remove encapsulating tags
        seed = seed[30:-30]
        # get the seed species definitions as a list
        seedDict = self.tokenize_seed_elements(seed)

        nauty_dict = {}
        for seed in seedDict:
            # initialize nfsim with each species definition and get back a
            # dirty list where one of the entries is the one we want 
            #
            # XXX: i think i've solved it on the nfsim side, double check
            tmpList = self.get_nauty_string(seedDict[seed])
            # and now filter it out...
            # get species names from species definition string
            speciesNames = self.get_names_from_definition_string(seed)
            nauty_dict[seed] = [x for x in tmpList if all(y in x for y in speciesNames)][0]

        return nauty_dict

    def get_nauty_string(self, xmlSpeciesDefinition):
        self.nfsim.reset_system()
        self.nfsim.init_system_xml(xmlSpeciesDefinition)
        result = self.nfsim.querySystemStatus("complex")
        return result


if __name__ == "__main__":
    parser = define_console()
    namespace = parser.parse_args()
    bnglPath = namespace.input + '.bngl'
    finalName = namespace.output if namespace.output else namespace.input

    # mdl to bngl
    resultDict = read_mdl.constructBNGFromMDLR(namespace.input, namespace.nfsim)
    outputDir = os.sep.join(namespace.output.split(os.sep)[:-1])
    # create bngl file
    read_mdl.outputBNGL(resultDict['bnglstr'], bnglPath)

    # temporaryly store bng-xml information in a separate file for display
    # purposes
    with open(namespace.input + '_extended.xml', 'wb') as f:
        f.write(resultDict['bngxmlestr'])

    # get cannonical label -bngl label dictionary

    if not namespace.nfsim:
        # bngl 2 sbml 2 json

        read_mdl.bngl2json(namespace.input + '.bngl')
        # json 2 plain mdl
        mdlDict = write_mdl.constructMDL(
            namespace.input + '_sbml.xml.json', namespace.input, finalName)
        # create an mdl with nfsim-species and nfsim-reactions
        write_mdl.write_mdl(mdlDict, finalName)
    else:
        try:
            mdlr2mdl = MDLR2MDL(os.path.join(get_script_path(), 'mcellr.yaml'))
            mdlr2mdl.process_mdlr(namespace.input)
        except IOError:
            print("Please create mcellr.yaml in the mcellRules directory. Use "
                  "mcellr.yaml.template as a reference.")
        # get the species definitions
