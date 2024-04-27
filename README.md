# vulnerableEC2
# get_vulnerableec2_nodes.py
This script authenticates using AWS credentials, retrieves EC2 instances associated with the specified EKS cluster, gathers relevant Kubernetes resources, and applies the Rego script for evaluation

# policy.rego
This Rego script receives comprehensive information about an EC2 instance, including its security groups, associated pods, and Kubernetes services. It then processes this data to return a boolean value indicating the vulnerability status of the instance.

# How to Execute
python3 get_vulnerableec2_nodes.py



