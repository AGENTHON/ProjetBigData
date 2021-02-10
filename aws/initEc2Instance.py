import boto3
import botocore
import paramiko
import time
from botocore.exceptions import ClientError
from os.path import expanduser

SECURITY_GROUP_NAME = 'Lab3SecurityGroup'
SECURITY_GROUP_DESCRIPTION = 'This is Security group for Lab3'
KEY_PAIR_FILE_NAME = 'lab3-ec2-keypair'
USERNAME = 'ec2-user'

def initInstance() :
    print("Starting init EC2 instance ...")
    key_pair_file_name = KEY_PAIR_FILE_NAME
    instance_public_dns = createEc2Instance(key_pair_file_name)
    #instance_public_dns='ec2-18-206-253-121.compute-1.amazonaws.com'
    client = connectInstance(key_pair_file_name, instance_public_dns)
    installPackets(client)
    sendEc2WorkerPythonFiles(client)
    startEc2Worker(client)
    
    client.close()
    print("Init Ec2 instance done.")


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
        InstanceType='t2.micro',
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
    

def installPackets(client) :
    print("Intalling python3 ...")
    stdin, stdout, stderr = client.exec_command('sudo yum install python3 -y')
    print("E : %s / O : %s" %(stderr.read(), stdout.read()))
    print("Intalling boto3 ...")
    stdin, stdout, stderr = client.exec_command('sudo python3 -m pip install boto3')
    print("E : %s / O : %s" %(stderr.read(), stdout.read()))
    #stdin, stdout, stderr = client.exec_command('sudo python3 -m pip install paramiko')

def sendEc2WorkerPythonFiles(client) :
    print("Sending Ec2 Worker Python Files ...")
    ftp_client=client.open_sftp()

    local_home = expanduser("~")
    remote_home = "/home/"+USERNAME

    ftp_client.put('../Serveur/serv.py',remote_home+'/serv.py')

    local_aws = local_home+'/.aws'
    remote_aws = remote_home+'/.aws'

    print("Creating .aws directory ...")
    ftp_client.mkdir(remote_aws)

    print("Sending aws config ...")
    ftp_client.put(local_aws+'/config', remote_aws+'/config')

    print("Sending aws credentials ...")
    ftp_client.put(local_aws+'/credentials', remote_aws+'/credentials')

    ftp_client.close()
    print("Done sending all worker files.")

def startEc2Worker(client) :
    #stdin, stdout, stderr = client.exec_command('ls ~/.aws')
    #stdin, stdout, stderr = client.exec_command('ls -la')
    #print("Error : %s" % stderr.read())
    #print("Out : %s" % stdout.read())

    client.exec_command('nohup python3 serv.py &')

'''
def sendEc2WorkerPythonFiles(client) :
    ftp_client=client.open_sftp()
    ftp_client.put('myfile.py','myfile.py')
    ftp_client.close()

def startEc2Worker(client) :
    stdin, stdout, stderr = client.exec_command('python3 myfile.py')
    print("Error : %s" % stderr.read())
    print("Out : %s" % stdout.read())
'''
#initInstance()


