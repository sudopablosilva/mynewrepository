import time
import subprocess
import os

# Define the cells as a comma-separated string
CELLS = os.getenv('cells')

def verify_cell(cell):
    print(f"Verifying {cell}")
    # Assume 'aws' and 'kubectl' are installed and configured
    alarm_state = subprocess.run(
        f"aws cloudwatch describe-alarms --alarm-names {cell}-opf-high-severity-aggregate-rollback --alarm-types CompositeAlarm --region {AWS_REGION} --query 'CompositeAlarms[0].StateValue' --output text",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    print(f"Alarm state for {cell}: {alarm_state}")
    if alarm_state == "ALARM":
        print(f"{cell} normal workload failed")
        exit(1)

def deploy_cell(cell, manifest_file):
    print(f"Deploying {cell}")
    # Assuming 'kubectl' is configured to apply manifests
    subprocess.run(f"kubectl apply -f {manifest_file}", shell=True, check=True)
    bake_time_seconds = calculate_bake_time('one_box', 1) * 60  # Convert bake time from minutes to seconds
    print(f"Waiting {bake_time_seconds} seconds before checking alarm")
    time.sleep(bake_time_seconds)
    print(f"Monitoring {cell} onebox")
    alarm_state = subprocess.run(
        f"aws cloudwatch describe-alarms --alarm-names {cell}-opf-onebox-rollback-alarm --alarm-types CompositeAlarm --region {AWS_REGION} --query 'CompositeAlarms[0].StateValue' --output text",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    print(f"Alarm state for {cell}: {alarm_state}")
    if alarm_state == "ALARM":
        print(f"{cell} onebox workload failed")
        exit(1)

    bake_time_seconds = calculate_bake_time('rest_waves', 1) * 60  # Assuming rest_waves bake time
    print(f"Waiting {bake_time_seconds} seconds before checking alarm")
    time.sleep(bake_time_seconds)
    print(f"Monitoring {cell} normal workload")
    alarm_state = subprocess.run(
        f"aws cloudwatch describe-alarms --alarm-names {cell}-opf-high-severity-aggregate-rollback --alarm-types CompositeAlarm --region {AWS_REGION} --query 'CompositeAlarms[0].StateValue' --output text",
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()
    print(f"Alarm state for {cell}: {alarm_state}")
    if alarm_state == "ALARM":
        print(f"{cell} normal workload failed")
        exit(1)

def main():
    # Create an array based on CELLS value split by comma
    cells = CELLS.split(',')

    for cell in cells:
        verify_cell(cell)
        deploy_cell(cell, f"modified_manifest_{cell}_onebox.yaml")
        deploy_cell(cell, f"modified_manifest_{cell}_normal.yaml")

if __name__ == "__main__":
    main()
