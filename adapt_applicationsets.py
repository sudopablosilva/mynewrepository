import yaml
import subprocess
import os

# Define a custom dumper that avoids quoting strings
class LiteralDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(LiteralDumper, self).increase_indent(flow, False)

# Custom representers for handling unquoted strings
def unquoted_representer(dumper, data):
    if isinstance(data, str) and '\n' not in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

# Adding custom representers to the Dumper
LiteralDumper.add_representer(str, unquoted_representer)

def modify_and_print_yaml(cluster_name, cell_name, service_name, workload_type, template_path):
    with open(template_path, 'r') as file:
        data = yaml.safe_load(file)
    
    data['metadata']['name'] = f'{cell_name}-{service_name}-{workload_type}'
    data['spec']['template']['metadata']['name'] = f'{cell_name}-{service_name}-{workload_type}'
    data['spec']['template']['destination']['name'] = f'{cell_name}'
    
    element = data['spec']['generators'][0]['list']['elements'][0]
    element['clusterName'] = cluster_name
    element['cellName'] = cell_name
    element['serviceName'] = service_name
    element['workloadType'] = workload_type
    
    # Use the custom dumper to write the YAML without quotes
    return yaml.dump(data, Dumper=LiteralDumper, default_flow_style=False)

cells = os.getenv('cells')
print(f'This is the input cells: {cells}')
# Split the string into a list based on the comma
cell_list = cells.split(',')
types = ["onebox", "normal"]
for cluster_name in cell_list:
    for workload_type in types:
        yaml_output = modify_and_print_yaml(cluster_name, cluster_name, os.getenv('serviceName'), workload_type, os.getenv('templatePath'))
        with open(f'modified_manifest_{cluster_name}_{workload_type}.yaml', 'w') as f:
            f.write(yaml_output)
        # subprocess.run(['kubectl', 'apply', '-f', f'modified_manifest_{cluster_name}_{workload_type}.yaml'])
        print(f"Deployed {workload_type} in {cluster_name}")
