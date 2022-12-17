# This script is from the MonoBehaviourFromAssembly example in the UnityPy repo.
# - https://github.com/K0lb3/UnityPy/tree/ba572869/examples/MonoBehaviourFromAssembly
# It has been modified to match this project's directories and updated libraries.
# 
# requirements:
# - pythonnet 3+ (already installed via requirements.txt)
#   - pip install git+https://github.com/pythonnet/pythonnet/
# - TypeTreeGenerator (already installed as the data_processing/input/net6.0 directory)
#   - https://github.com/K0lb3/TypeTreeGenerator/tree/12ed37d9
#   - requires .NET 6.0 SDK (this is the only extra thing you need to download)
#     - https://dotnet.microsoft.com/download/dotnet/6.0

import os
import json
import UnityPy
from typing import Dict

ROOT = os.path.join('data_processing', 'input')
TYPETREE_GENERATOR_PATH = os.path.join(ROOT, 'net6.0')

def main():
    # dump the trees for all classes in the assembly
    dll_folder = os.path.join(ROOT, 'DummyDll')
    tree_path = os.path.join(ROOT, 'typetrees.json')
    trees = dump_assembly_trees(dll_folder, tree_path)
    # by dumping it as json, it can be redistributed,
    # so that other people don't have to setup pythonnet3
    # People who don't like to share their decrypted dlls could also share the relevant structures this way.

def dump_assembly_trees(dll_folder: str, out_path: str):
    # init pythonnet, so that it uses the correct .net for the generator
    pythonnet_init()
    # create generator
    g = create_generator(dll_folder)

    # generate a typetree for all existing classes in the Assembly-CSharp
    # while this could also be done dynamically for each required class,
    # it's faster and easier overall to just fetch all at once
    trees = generate_tree(g, 'Assembly-CSharp.dll', '', '')

    if out_path:
        with open(out_path, 'wt', encoding='utf8') as f:
            json.dump(trees, f, ensure_ascii=False)
    return trees

def pythonnet_init():
    '''correctly sets-up pythonnet for the typetree generator'''
    # prepare correct runtime
    from clr_loader import get_coreclr
    from pythonnet import set_runtime

    rt = get_coreclr()
    set_runtime(rt)

def create_generator(dll_folder: str):
    '''Loads TypeTreeGenerator library and returns an instance of the Generator class.'''
    # temporarily add the typetree generator dir to paths,
    # so that pythonnet can find its files
    import sys
    sys.path.append(TYPETREE_GENERATOR_PATH)

    import clr
    clr.AddReference('TypeTreeGenerator')

    # import Generator class from the loaded library
    from Generator import Generator

    # create an instance of the Generator class
    g = Generator()
    # load the dll folder into the generator
    g.loadFolder(dll_folder)
    return g

class FakeNode:
    '''A fake/minimal Node class for use in UnityPy.'''
    def __init__(self, **kwargs):
        self.__dict__.update(**kwargs)

def generate_tree(
    g: 'Generator',
    assembly: str,
    class_name: str,
    namespace: str,
    unity_version=[2018, 4, 3, 1],
) -> Dict[str, Dict]:
    '''Generates the typetree structure / nodes for the specified class.'''
    # C# System
    from System import Array
    unity_version_cs = Array[int](unity_version)

    # fetch all type definitions
    def_iter = g.getTypeDefs(assembly, class_name, namespace)

    # create the nodes
    trees = {}
    for d in def_iter:
        try:
            nodes = g.convertToTypeTreeNodes(d, unity_version_cs)
        except Exception as e:
            # print(d.Name, e)
            continue
        trees[d.Name] = [
            {
                'level' : node.m_Level,
                'type' : node.m_Type,
                'name' : node.m_Name,
                'meta_flag' : node.m_MetaFlag,
            }
            for node in nodes
        ]
    return trees

if __name__ == '__main__':
    main()
