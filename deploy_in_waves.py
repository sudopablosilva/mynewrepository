import time
import subprocess
import os
import logging

# Set the timezone to UTC-3
os.environ['TZ'] = 'UTC-3'
time.tzset()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the cells as a comma-separated string
CELLS = os.getenv('CELLS')
AWS_REGION = os.getenv('AWS_REGION')
MAX_BAKE_TIME_SECONDS = int(os.getenv('MAX_BAKE_TIME_SECONDS'))

def calculate_bake_time(stage, cell_wave):
    # Define bake time constants in minutes
    ONE_BOX_WAIT = 30
    FIRST_WAVE_WAIT = 60
    REST_WAVES_WAIT = 30
    DATA_POINTS_WAIT = 0 # The bake time includes requirements to wait for a specific number of data points in the team’s metrics (for example, "wait for at least 100 requests to the Create API") to ensure that enough requests have occurred to make it likely that the new code has been fully exercised.

    bake_time = 0
    
    # Add bake time based on the stage and region wave
    if stage == 'one_box':
        bake_time += ONE_BOX_WAIT
    elif stage == 'first_wave':
        bake_time += FIRST_WAVE_WAIT
    elif stage == 'rest_waves':
        bake_time += (REST_WAVES_WAIT * cell_wave)
    
    # Add bake time for waiting for data points in metrics
    bake_time += DATA_POINTS_WAIT

    # Limit bake time to a maximum
    bake_time = min(bake_time, MAX_BAKE_TIME_SECONDS)

    return bake_time
    
def verify_cell(cell):
    logging.info('#'*120)
    logging.info(f"Verifying {cell}")
    alarm_name = f"{cell}-opf-high-severity-aggregate-rollback"
    alarm_state = get_alarm_state(alarm_name)
    logging.info(f"Alarm state for {alarm_name}: {alarm_state}")
    if alarm_state == "ALARM":
        logging.error(f"{cell} normal workload failed")
        exit(1)

def get_alarm_state(alarm_name):
    # Assume 'aws' is installed and configured
    try:
        result = subprocess.run(
            f"aws cloudwatch describe-alarms --alarm-names {alarm_name} --alarm-types CompositeAlarm --region {AWS_REGION} --query 'CompositeAlarms[0].StateValue' --output text",
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting alarm state for {alarm_name}: {e}")
        return "UNKNOWN"

def deploy_cell(cell, manifest_file):
    logging.info(f"Deploying {cell}")
    # Assuming 'kubectl' is configured to apply manifests
    subprocess.run(f"kubectl apply -f {manifest_file}", shell=True, check=True)
    bake_time_seconds = calculate_bake_time('one_box', 1)
    logging.info(f"Waiting {bake_time_seconds} seconds before checking alarm")
    time.sleep(bake_time_seconds)
    logging.info(f"Monitoring {cell} onebox")
    alarm_name = f"{cell}-opf-onebox-rollback-alarm"
    alarm_state = get_alarm_state(alarm_name)
    logging.info(f"Alarm state for {alarm_name}: {alarm_state}")
    if alarm_state == "ALARM":
        logging.error(f"{cell} onebox workload failed")
        exit(1)

    bake_time_seconds = calculate_bake_time('rest_waves', 1)  # Assuming rest_waves bake time
    logging.info(f"Waiting {bake_time_seconds} seconds before checking alarm")
    time.sleep(bake_time_seconds)
    logging.info(f"Monitoring {cell} normal workload")
    alarm_name = f"{cell}-opf-high-severity-aggregate-rollback"
    alarm_state = get_alarm_state(alarm_name)
    logging.info(f"Alarm state for {alarm_name}: {alarm_state}")
    if alarm_state == "ALARM":
        logging.error(f"{cell} normal workload failed")
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
