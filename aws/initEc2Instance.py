import boto3
import paramiko
import time
from botocore.exceptions import ClientError
from os import path


SECURITY_GROUP_NAME = 'BigDataProjectSecurityGroup'
SECURITY_GROUP_DESCRIPTION = 'This is Security group for our BigData project'
KEY_PAIR_FILE_NAME = 'BigDataProject-ec2-keypair'
USERNAME = 'ec2-user'

def initInstance() :
    print("Starting init EC2 instance ...")
    key_pair_file_name = KEY_PAIR_FILE_NAME
    instance_public_dns = createEc2Instance(key_pair_file_name)
    client = connectInstance(key_pair_file_name, instance_public_dns)
    installPackets(client)
    sendEc2WorkerPythonFiles(client)
    startEc2Worker(client)
    
    print("Init Ec2 instance done.")
    return client


def createEc2Instance(key_pair_file_name) :
    ec2_ressource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    vpcs = ec2_client.describe_vpcs()
    vpc_id = vpcs.get('Vpcs', [{}])[0].get('VpcId', '')
    print('VpcId= %s' % vpc_id)

    ###### Create ec2 key pair ######

    # call the boto ec2 function to create a key pair
    key_pair = ec2_ressource.create_key_pair(KeyName=key_pair_file_name)

    # create a file to store the key locally
    outfile = open(key_pair_file_name,'w')

    # capture the key and store it in a file
    KeyPairOut = str(key_pair.key_material)
    print(KeyPairOut)
    outfile.write(KeyPairOut)


    ###### Create ec2 security group ######

    try:
        response = ec2_client.create_security_group(GroupName=SECURITY_GROUP_NAME,
                                            Description=SECURITY_GROUP_DESCRIPTION,
                                            VpcId=vpc_id)
        security_group_id = response['GroupId']
        print('Security Group Created %s in vpc %s.' % (security_group_id, vpc_id))

        data = ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {'IpProtocol': 'tcp',
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
                {'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
            ])
        print('Ingress Successfully Set %s' % data)
    except ClientError as e:
        print(e)


    ###### Create ec2 instance ######

    instances = ec2_ressource.create_instances(
        ImageId='ami-0c94855ba95c71c99',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.large',
        KeyName=key_pair_file_name,
        SecurityGroupIds=[
            security_group_id
        ]
    )

    instance = instances[0]

    print('Wait until running instance ...')
    instance.wait_until_running()
    print('Wait until initializing instance ...')
    time.sleep(20)

    # Reload the instance attributes
    instance.load()

    instance_id = instance.id
    instance_public_dns = instance.public_dns_name
    print('public_dns=%s' % instance_public_dns)

    return instance_public_dns

# Penser à client.close()
def connectInstance(key_pair_file_name, instance_public_dns) :

    key = paramiko.RSAKey.from_private_key_file(key_pair_file_name)
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect/ssh to an instance
    try:
        print("Try to connect to ec2 instance ...")
        client.connect(hostname=instance_public_dns, username=USERNAME, pkey=key, timeout=30, auth_timeout=30)
        return client
    except Exception as e:
        print(e)

def installPythonPackage(client,name):
    print("Installing"+name+"...")
    stdin, stdout, stderr = client.exec_command('sudo python3 -m pip install '+name)
    print("E : %s / O : %s" %(stderr.read(), stdout.read()))
    

def installPackets(client) :
    print("Installing python3 ...")
    stdin, stdout, stderr = client.exec_command('sudo yum install python3 -y')
    print("E : %s / O : %s" %(stderr.read(), stdout.read()))
    installPythonPackage(client,"scikit-learn")
    installPythonPackage(client,"nltk")
    installPythonPackage(client,"numpy")
    installPythonPackage(client,"re")
    installPythonPackage(client,"pandas")

    
    

def sendEc2WorkerPythonFiles(client) :
    print("Sending Ec2 Worker Python Files ...")
    ftp_client=client.open_sftp()

    local_home = path.expanduser("~")
    remote_home = "/home/"+USERNAME

    ftp_client.put('../processing/trainingTFIDF.py',remote_home+'/trainingTFIDF.py')
    ftp_client.put('../processing/utils.py',remote_home+'/utils.py')
    ftp_client.put('../processing/data.json',remote_home+'/data.json')
    ftp_client.put('../processing/label.csv',remote_home+'/label.csv')
    ftp_client.put('../processing/categories_string.csv',remote_home+'/categories_string.csv')


    ftp_client.close()
    print("Done sending all worker files.")

def startEc2Worker(client) :
    print("Starting ec2 worker ...")

    stdin, stdout, stderr = client.exec_command('python3 trainingTFIDF.py',get_pty = True)
    print("E : %s / O : %s" %(stderr.read(), stdout.read()))
    
    print("Starting ec2 worker ...")


def fetchPredictFile(client):
    ftp_client=client.open_sftp()
    local_home = path.expanduser("~")
    remote_home = "/home/"+USERNAME

    ftp_client.get(remote_home+'/predict.csv', '../result/predict.csv')
    ftp_client.close()
    print("Done fetching all worker files.")

if __name__ == "__main__":

    client=initInstance()
    
    fetchPredictFile(client)
    
    client.close()
    


