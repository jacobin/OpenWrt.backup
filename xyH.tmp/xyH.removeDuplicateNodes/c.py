





#############################################################################{{
#############################################################################{{
#############################################################################{{
#https://github.com/yaml/pyyaml/issues/656
#### Use case: I want to load a yaml file, inject something in a mapping in a well-known place and dump back to the file.
#### 
#### I want to do this with arbitrary files outside of my control, which contain arbitrary tags.
#### 
#### safe_load[_all] and load[_all] will both error out at the tags.
#### 
#### There are workarounds on stackoverflow to discard the tags but I need to preserve them, just not evaluate them.
#### 
#### The best I came up with is this:
#
#"""
#Work-around to allow loading and dumping yaml with tags in a way that the tags do not get lost.
#"""
#
#from __future__ import annotations
#from enum import Enum, auto
#from typing import Any
#
#import yaml
#
#
#class TypedYamlType(Enum):
#    SCALAR = auto()
#    SEQUENCE = auto()
#    MAPPING = auto()
#
#
#class TypedYaml:
#    suffix: str
#    type_: TypedYamlType
#    value: Any
#
#    def __init__(self, suffix: str, type_: TypedYamlType, value: any):
#        self.suffix = f"tag:{suffix}"
#        self.type_ = type_
#        self.value = value
#
#    @staticmethod
#    def construct(loader: yaml.Loader, suffix: str, node: yaml.Node) -> TypedYaml:
#        if isinstance(node, yaml.ScalarNode):
#            constructor = loader.__class__.construct_scalar
#            type_ = TypedYamlType.SCALAR
#        elif isinstance(node, yaml.SequenceNode):
#            constructor = loader.__class__.construct_sequence
#            type_ = TypedYamlType.SEQUENCE
#        elif isinstance(node, yaml.MappingNode):
#            constructor = loader.__class__.construct_mapping
#            type_ = TypedYamlType.MAPPING
#
#        return TypedYaml(suffix=suffix, type_=type_, value=constructor(loader, node))
#
#    @staticmethod
#    def represent(dumper: yaml.Dumper, data: TypedYaml) -> yaml.Node:
#        if data.type_ == TypedYamlType.SCALAR:
#            return dumper.represent_scalar(tag=data.suffix, value=data.value)
#        elif data.type_ == TypedYamlType.SEQUENCE:
#            return dumper.represent_sequence(tag=data.suffix, sequence=data.value)
#        elif data.type_ == TypedYamlType.MAPPING:
#            return dumper.represent_mapping(tag=data.suffix, mapping=data.value)
#        else:
#            raise ValueError(f"Unknown TypedYaml variant: {data.type_}")
#
#
#class TypedYamlLoader(yaml.SafeLoader):
#    """
#    SafeLoader on which multi-constructors are registered without influencing SafeLoader.
#
#    Usage:
#    yaml.load_all(yaml_string, Loader=TypedYamlLoader)
#    """
#
#    pass
#
#
#TypedYamlLoader.add_multi_constructor("!", TypedYaml.construct)
#TypedYamlLoader.add_multi_constructor("tag:", TypedYaml.construct)
#
#
#class TypedYamlDumper(yaml.Dumper):
#    """
#    Dumper on which a representer for TypedYaml is registered without influecing the regular Dumper.
#    """
#
#    pass
#
#
#TypedYamlDumper.add_representer(TypedYaml, TypedYaml.represent)
#
#### and using this as e.g.
#
#parsed_all = yaml.load_all(contents, Loader=TypedYamlLoader)
## ...
#contents = yaml.dump_all(output, Dumper=TypedYamlDumper)
#############################################################################}}
#############################################################################}}
#############################################################################}}






#############################################################################{{
#############################################################################{{
#############################################################################{{
# https://stackoverflow.com/questions/33048540/pyyaml-safe-load-how-to-ignore-local-tags
import yaml,getopt

class SafeLoaderIgnoreUnknown(yaml.SafeLoader):
	def ignore_unknown(self, node):
		return None 

SafeLoaderIgnoreUnknown.add_constructor(None, SafeLoaderIgnoreUnknown.ignore_unknown)

# root = yaml.load(content, Loader=SafeLoaderIgnoreUnknown)
#############################################################################}}
#############################################################################}}
#############################################################################}}






try:
    with open('allfew.yaml', 'r') as file:
        data = yaml.load(file, Loader=SafeLoaderIgnoreUnknown)
    print(data)
except FileNotFoundError:
    print("Error: The file 'allfew.yaml' was not found.")
except yaml.YAMLError as exc:
    print(f"Error parsing YAML file: {exc}")


import sys
import getopt

#Remove the file name from the commandline arguments
argumentList = sys.argv[1:]
short_options ="h:m:o:"
long_options = ["Help=", ¡°My_file=","Output="]
#Parsing arguments -extract meaningful information from command line arguments
try£º
	arguments,values=getopt.getopt£¨argumentList£¬shortoptions£¬long_options)
	except getopt.error as err:
		print(str(err))
		sys.exit(2)
		
print('arguments:', arguments)
print('values:',values)
for currentArgument,currentvalue in arguments:
	print£¨'currentArgument:£¬currentArgument£©
	print('currentValue:',currentValue)
	if currentArgument in ("-h", "--Help"): 
		print(*Help message')
	
	elif currentArgument in ("-m", "--My_file"):
		print('File name:',sys.argv[o])
		
	elif currentArgument in ("-o",¡°--Output"):
		print('Showing output:',currentValue£©