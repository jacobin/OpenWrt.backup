import yaml

# Data to be dumped
data = {
    "quoted_string": "This is a string with an exclamation mark!",
    "another_quoted_string": "This is also a string with an exclamation mark!",
    "escaped_string": "This string contains a literal ! within double quotes."
}

# Dump to YAML
yaml_output = yaml.dump(data, default_flow_style=False)
print(yaml_output)

# Load from YAML
loaded_data = yaml.safe_load(yaml_output)
print(loaded_data)
