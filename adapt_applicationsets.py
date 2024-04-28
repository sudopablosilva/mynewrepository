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

def modify_and_print_yaml(cluster_name, cell_name, service_name, workload_type, template_path, BAKE_TIME_BETWEEN_CANARY_AND_STABLE_IN_SECONDS):
    with open(template_path, 'r') as file:
        data = yaml.safe_load(file)
    
    data['metadata']['name'] = f'{cell_name}-{service_name}-{workload_type}'
    data['spec']['template']['metadata']['name'] = f'{cell_name}-{service_name}-{workload_type}'
    data['spec']['template']['spec']['destination']['name'] = f'{cell_name}'
    
    element = data['spec']['generators'][0]['list']['elements'][0]
    element['clusterName'] = cluster_name
    element['cellName'] = cell_name
    element['serviceName'] = service_name
    element['workloadType'] = workload_type
    element['BAKE_TIME_BETWEEN_CANARY_AND_STABLE_IN_SECONDS'] = BAKE_TIME_BETWEEN_CANARY_AND_STABLE_IN_SECONDS
    
    # Use the custom dumper to write the YAML without quotes
    return yaml.dump(data, Dumper=LiteralDumper, default_flow_style=False)

cells = os.getenv('cells')
workloadTypes = os.getenv('workloadTypes')
print(f'This is the input cells: {cells}')
print(f'This is the input workloadTypes: {workloadTypes}')
# Split the string into a list based on the comma
cell_list = cells.split(',')

workloadTypes = workloadTypes.split(',')

for cluster_name in cell_list:
    for workload_type in workloadTypes:
        yaml_output = modify_and_print_yaml(cluster_name, cluster_name, os.getenv('serviceName'), workload_type, os.getenv('templatePath'), os.getenv('BAKE_TIME_BETWEEN_CANARY_AND_STABLE_IN_SECONDS'))
        with open(f'modified_manifest_{cluster_name}_{workload_type}.yaml', 'w') as f:
            print(f'Writing modified_manifest_{cluster_name}_{workload_type}.yaml')
            f.write(yaml_output)
        # subprocess.run(['kubectl', 'apply', '-f', f'modified_manifest_{cluster_name}_{workload_type}.yaml'])
        print(f"Generated modified_manifest for {workload_type} in {cluster_name}")
