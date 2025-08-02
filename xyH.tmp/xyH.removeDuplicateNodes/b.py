
import yaml

# YAML data as a string
yaml_string = """
name: John Doe
age: 30
occupations:
    - Software Engineer
    - Data Scientist
address:
    street: 123 Main St
    city: Anytown
"""

# Load YAML from a string
data = yaml.safe_load(yaml_string)
print(f"Loaded data: {data}")

# Accessing elements
print(f"Name: {data['name']}")
print(f"First occupation: {data['occupations'][0]}")

# Dump Python object to YAML
python_data = {
    'product': 'Example Gadget',
    'price': 99.99,
    'features': ['Wireless', 'Portable', 'Long Battery Life']
}
yaml_output = yaml.dump(python_data, default_flow_style=False)
print(f"\nDumped YAML:\n{yaml_output}")



# import yaml
# 
# yaml_string = """
# name: John Doe
# age: 30
# city: New York
# """
# data = yaml.safe_load(yaml_string)
# print(data)

