import yaml

# Create a sample YAML file (hexyconfig.yaml) for demonstration
yaml_content = """
database:
  host: localhost
  port: 5432
  name: my_database
  user: admin
  password: secure_password
"""
with open('hexyconfig.yaml', 'w') as f:
    f.write(yaml_content)

# Load data from the YAML file
with open('hexyconfig.yaml', 'r') as file:
    hexyconfig_data = yaml.safe_load(file)

print("Loaded YAML data:")
print(hexyconfig_data)
print(f"Database host: {hexyconfig_data['database']['host']}")