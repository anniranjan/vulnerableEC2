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
    for instance in instances:
        if 'aws:eks:cluster-name' in [tag['Key'] for tag in instance.get('Tags', [])]:
            kubernetes_nodes.append(instance)
   # print(kubernetes_nodes)
    return kubernetes_nodes
    #return instances

def get_k8s_resources():
    config.load_kube_config()  # Assuming kubeconfig is set up
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)
    services = v1.list_service_for_all_namespaces(watch=False)
    return pods.items, services.items

def evaluate_with_rego(instance_data, rego_script_path):
    # Assuming OPA binary is available and rego script is prepared
    with open('data.json', 'w') as file:
        json.dump(instance_data, file, indent=4, sort_keys=True, default=str)

    result = subprocess.run(['opa', 'eval', '--data', rego_script_path, '--input', 'data.json', 'true', '--format', 'json'],
                            capture_output=True, text=True)
    print(result)
    output = result.stdout
    parsed_output = json.loads(output)
    #return result.stdout.strip() == 'true'
    return parsed_output['result'][0]['expressions'][0]['value']

def main():
    ec2_instances = get_ec2_instances()
    #print(ec2_instances)
    pods, services = get_k8s_resources()
    #print(pods)
    #print(services)
    vulnerable_instances = []
    for instance in ec2_instances:
        security_group_ids = [sg['GroupId'] for sg in instance['SecurityGroups']]
        print(security_group_ids)

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
            print("Else block")
    print("Vulnerable EC2 Instances:", vulnerable_instances)

if __name__ == '__main__':
    main()
