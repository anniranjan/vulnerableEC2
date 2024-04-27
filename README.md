# vulnerableEC2
# 1. get_vulnerableec2_nodes.py
This script authenticates using AWS credentials, retrieves EC2 instances associated with the specified EKS cluster, gathers relevant Kubernetes resources, and applies the Rego script for evaluation

# policy.rego
This Rego script receives comprehensive information about an EC2 instance, including its security groups, associated pods, and Kubernetes services. It then processes this data to return a boolean value indicating the vulnerability status of the instance.

# How to Execute
python3 get_vulnerableec2_nodes.py

# 2. Superset Exploit Checker
Superset Exploit Checker is a Python script that checks whether a Superset instance is vulnerable to a specific exploit by forging session cookies.

## Prerequisites

- Python 3.x

## Usage
Run the script 'check_exploitable.py' and follow the instructions
python3 check_exploitable.py





