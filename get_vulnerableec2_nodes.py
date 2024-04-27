import boto3
from kubernetes import client, config
import subprocess
import json

def get_ec2_instances():
    ec2_client = boto3.client('ec2')
    response = ec2_client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            # Retrieve security group IDs associated with the instance
            security_group_ids = [sg['GroupId'] for sg in instance['SecurityGroups']]
            # Describe security groups to get details
            security_groups = ec2_client.describe_security_groups(GroupIds=security_group_ids)['SecurityGroups']
            # Replace the security group IDs with security group details
            instance['SecurityGroups'] = security_groups
            # Append the modified instance to the instances list
            instances.append(instance)
    kubernetes_nodes = []
    #Iterate through the nodes and filter kubernetes nodes
    for instance in instances:
        if 'aws:eks:cluster-name' in [tag['Key'] for tag in instance.get('Tags', [])]:
            kubernetes_nodes.append(instance)
    return kubernetes_nodes

def get_k8s_resources():
    #Load the kube config
    config.load_kube_config()
    v1 = client.CoreV1Api()
    #get the pod lists
    pods = v1.list_pod_for_all_namespaces(watch=False)
    #get the services list
    services = v1.list_service_for_all_namespaces(watch=False, pretty="True")
    return f"{pods.items}", f"{services.items}"

def evaluate_with_rego(instance_data, rego_script_path):
    # Run the opa evaluation process
    with open('data.json', 'w') as file:
        json.dump(instance_data, file, indent=4, sort_keys=True, default=str)

    result = subprocess.run(['opa', 'eval', '--data', rego_script_path, '--input', 'data.json', 'data.ec2evaluation', '--format', 'json'],
                            capture_output=True, text=True)
    output = result.stdout
    parsed_output = json.loads(output)
    return parsed_output['result'][0]['expressions'][0]['value']

def main():
    #Get the EC2 instances
    ec2_instances = get_ec2_instances()
    #Get the pods and services running in EKS cluster
    pods, services = get_k8s_resources()
    vulnerable_instances = []
    #Run the policy
    for instance in ec2_instances:

        rego_script_path = 'policy.rego'

        instance_data = {
            'instance': instance,
            'pods': pods,
            'services': services
        }
        if evaluate_with_rego(instance_data, rego_script_path):
            vulnerable_instances.append(instance['InstanceId'])
            print("Vulnerable EC2: ", instance['InstanceId'])
        else:
            print("EC2 is not vulnerable")
    print("Vulnerable EC2 Instances:", vulnerable_instances)

if __name__ == '__main__':
    main()
