
  

# ODOO K8S backup

  

  

## Warning:

  

If possible use mature tools to back up your Odoo workloads like [velero](https://velero.io/)

  

  

# Features

  

This script creates a Kubernetes cronjob that allows the backup of Odoo's data and database to any [Restic compatible storage](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html) (S3 buckets - SFTP ...)

  

  

This project was created to enable backup of Odoo workloads where K8S volume snapshots are not available and making backups with tools like Velero isn't possible (i.e.: when using Hostpath or rancher.io/local-path provisioner)

  

  

Work is still in progress and **contributions are welcome**

  

  

## Instructions

  

  

How to run:

  

1- Create python virtual environment:

  

  

    python -m venv .venv

  

2- Activate virtual environment

  

  

    source .venv/bin/activate

  

  

3- Install required packages

  

  

    pip install -r requirements.txt

  
 4- copy .env.example and fill the necessary environement variables

    cp .env.example .env

5- Create a Kubernetes cronjob that generates the backup jobs

    python cronjob.py

  

  

## TODO:

  

  

- [ ] Automatic restoration for odoo instances
