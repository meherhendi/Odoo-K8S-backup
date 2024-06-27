#this is a python script
# step 1 get all pods with annotation "name=odoo"
# step 2 extract the POD_NAME and persistant volume claim attached to it
# step 3 create a loop
# step 3.1 create a config and replace pod name and volume claim name with appropriate variables POD_NAME, DB_HOST and DB_NAME,
# take these as enviroment variables RESTIC_REPOSITORY ,RESTIC_BACKUP_PATH ,ODOO_DATA_DIR ,DB_USER ,DATABASE_DUMP_DIR ,NAMESPACE ,TOKEN_FILE ,CACERT ,API_SERVER
# step 3.2 create a job config that takes the config and spans a job accroding to this yaml config

import os
import yaml
from dotenv import load_dotenv
from kubernetes import client, config

# Load Kubernetes configuration
config.load_kube_config()

# load env vars
load_dotenv(".env")

# Initialize the Kubernetes API clients
v1 = client.CoreV1Api()
batch_v1 = client.BatchV1Api()

# # Environment variables
restic_repository = os.getenv('RESTIC_REPOSITORY')
restic_backup_path = os.getenv('RESTIC_BACKUP_PATH')
odoo_data_dir = os.getenv('ODOO_DATA_DIR')
db_user = os.getenv('DB_USER')
database_dump_dir = os.getenv('DATABASE_DUMP_DIR')
namespace = os.getenv('NAMESPACE', 'default')
token_file = os.getenv('TOKEN_FILE')
cacert = os.getenv('CACERT')
api_server = os.getenv('API_SERVER')


# Function to create a job configuration
def create_job_config(pod_name, db_host, db_name, pvcs):
    print("mounting volume", pvcs[0])
    job_template = f"""
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-job-{pod_name}
spec:
  schedule: "0 0 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: visiogain/odoo-backup-job
            env:
            - name: POD_NAME
              value: {pod_name}
            - name: DB_HOST
              value: {db_host}
            - name: DB_NAME
              value: {db_name}
            - name: RESTIC_REPOSITORY
              value: {restic_repository}
            - name: RESTIC_BACKUP_PATH
              value: {restic_backup_path}
            - name: ODOO_DATA_DIR
              value: {odoo_data_dir}
            - name: DB_USER
              value: {db_user}
            - name: DATABASE_DUMP_DIR
              value: {database_dump_dir}
            - name: NAMESPACE
              value: {namespace}
            - name: TOKEN_FILE
              value: {token_file}
            - name: CACERT
              value: {cacert}
            - name: API_SERVER
              value: {api_server}
            - name: RESTIC_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: RESTIC_PASSWORD
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: PGPASSWORD
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: PGPASSWORD
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: AWS_ACCESS_KEY_ID
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: backup-secrets
                  key: AWS_SECRET_ACCESS_KEY
            volumeMounts:
            - name: odoo-data-volume
              mountPath: bitnami/odoo/data/
          volumes:
          - name: odoo-data-volume
            persistentVolumeClaim:
              claimName: {pvcs[0]}
          restartPolicy: OnFailure
"""
    return yaml.safe_load(job_template)

def loop_through_pods():
# Loop through each pod and create a job configuration
    # Get all pods with annotation "name=odoo"
    pods = v1.list_pod_for_all_namespaces(label_selector="app.kubernetes.io/name=odoo")

    for pod in pods.items:
        pod_name = pod.metadata.name
        namespace = pod.metadata.namespace
        pvcs = []
        db_host=""
        db_name=""

        for volume in pod.spec.volumes:
            if volume.persistent_volume_claim:
                pvc_name = volume.persistent_volume_claim.claim_name
                pvcs.append(pvc_name)

        # Extract environment variables
        for container in pod.spec.containers:
            for env in container.env:
                if env.name == 'DB_HOST':
                    db_host = env.value
                elif env.name == 'DB_NAME':
                    db_name = env.value
        
        pod_info = {
            'namespace': namespace,
            'pod_name': pod_name,
            'pvcs': pvcs,
            'db_host': db_host,
            'db_name': db_name
        }

        print("pod_info", pod_info)

        print(f"Pod Name: {pod_name}")
        print(f"Database Host: {db_host}")
        print(f"Database Name: {db_name}")
        print(f"Persistent Volume Claims: {pvcs}")

        job_config = create_job_config(pod_name, db_host, db_name, pvcs)

        print("job_config", job_config)
        # Create the job in the cluster
        response = batch_v1.create_namespaced_cron_job(
            body=job_config,
            namespace=namespace
        )
        print(f"Job created for pod {pod_name} with response: {response.metadata.name}")


    

 

if __name__ == "__main__":
    loop_through_pods()
    # create_job_config()