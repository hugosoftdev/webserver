import boto3

import botocore

import json

import sys

import os

from botocore.exceptions import ClientError

import logging

import time



s3_policy_name = 'presentation'

ec2_role = 'presentation'

ec2_profile = 'presentation'



iam = boto3.client('iam')

ec2 = boto3.client('ec2')





def script_commands(relationsList, dependeciesList, date_init, date_end):

  relations = relationsList[0]

  if(len(relationsList) > 1):

    for name in relationsList[1:]:

      relations += "\n{0}".format(name)



  dependeciesString = ''

  for i in dependeciesList:

    dependeciesString += '\n{0}'.format(i)



  commands = """#!/bin/bash                                                                                               

  cd home/ubuntu/

  apt update

  apt install python3

  apt install python3-pip -y

  pip3 install pandas

  pip3 install boto3

  git clone https://github.com/Jean-Low/bt_test.git

  cd bt_test

  cd Backtesting

  echo '{0}' >> relations.txt

  python3 copy_to_local.py {1} {2} &> error.txt

  echo '{3}' >> requirements.txt

  pip3 install -r requirements.txt

  python3 behavior.py > output.txt

  """.format(relations, date_init, date_end,dependeciesString)

  print(commands)

  return commands





def getInstancesIpFromId(ids):

    instances = ec2.describe_instances(

        InstanceIds=ids

    )

    if(len(instances['Reservations']) < 1):

      print('não foi retornado reservations')

      return []

    else:

      intancesIp = [instance['PublicIpAddress']

                    for instance in instances['Reservations'][0]['Instances']]

      return intancesIp





def create_security_group(name):

  exists = check_if_security_group_exists(name)

  if(exists != False):

    return exists

    #delete_security_group(exists)

    #time.sleep(3)

  response = ec2.describe_vpcs()

  vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

  try:

      response = ec2.create_security_group(

          GroupName=name, Description='None', VpcId=vpc_id)

      security_group_id = response['GroupId']

      data = ec2.authorize_security_group_ingress(

          GroupId=security_group_id,

          IpPermissions=[

              {'IpProtocol': 'tcp',

               'FromPort': 8888,

               'ToPort': 8888,

               'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},

              {'IpProtocol': 'tcp',

               'FromPort': 22,

               'ToPort': 22,

               'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}

          ])

      return security_group_id

  except ClientError as e:

      print(e)





def check_if_security_group_exists(name):

  try:

    response = ec2.describe_security_groups()

    for group in response['SecurityGroups']:

      if(group['GroupName'] == name):

        return group['GroupId']

    return False

  except ClientError as e:

      print(e)





def delete_security_group(id):

    # Delete security group

  try:

      response = ec2.delete_security_group(GroupId=id)

  except ClientError as e:

      print(e)





def create_key_pair(keyPairName):

  exists = check_if_key_pair_exists(keyPairName)

  if(exists):

    deleteKeyPair(keyPairName)

    if os.path.exists("{0}.pem".format(keyPairName)):

      os.remove("{0}.pem".format(keyPairName))

  response = ec2.create_key_pair(KeyName=keyPairName)

  with open("{0}.pem".format(keyPairName), "w") as pemFile:

    pemFile.write(response['KeyMaterial'])

    os.chmod('./{0}.pem'.format(keyPairName), 0o400)





def check_if_key_pair_exists(keyPairName):

  response = ec2.describe_key_pairs()

  keyPairs = response["KeyPairs"]

  exists = False

  for key in keyPairs:

    if(key["KeyName"] == keyPairName):

      exists = True

      break

  return exists





def deleteKeyPair(keyPairName):

  ec2.delete_key_pair(KeyName=keyPairName)





def main(configs):

  #get strategy names

  args = sys.argv





  dependeciesList = []

  relationsList = []

  for i in configs['relations']:

    instruments = ""

    for j in i['instruments']:

      instruments += ' {0}'.format(j)

    relationsList.append("{0}:{1}-{2}{3}".format(

        i['strategy'], i['model_class'], i['model'], instruments))

    for j in i['dependencies']:

      dependeciesList.append(j)



  date_init = configs['date_init']

  date_end = configs['date_end']



  ##check if instance profile exists and deletes

  print("Checking instance profiles")

  instance_profiles = iam.list_instance_profiles()['InstanceProfiles']

  profileExists = False

  for profile in instance_profiles:

    if profile['InstanceProfileName'] == ec2_profile:

      print("Instance Profile already exists")

      profileExists = True

      """

      iam.remove_role_from_instance_profile(

          InstanceProfileName=ec2_profile,

          RoleName=ec2_role

      )

      iam.delete_instance_profile(

          InstanceProfileName=ec2_profile

      )

      """



  if not profileExists:

    print("Creating instance profile")

    instanceProfile = iam.create_instance_profile(

        InstanceProfileName=ec2_profile

    )



  #check if policy exists

  print("Checking existing policies")

  policy_arn = None

  paginator = iam.get_paginator('list_policies')

  all_policies = [policy for page in paginator.paginate()

                  for policy in page['Policies']]

  policy = [p for p in all_policies if p['PolicyName'] == s3_policy_name]



  if(len(policy) > 0):

    policy_arn = policy[0]['Arn']



  #check if role exists and delete it

  print("Checking existing roles...")

  roles = iam.list_roles()

  Role_list = roles['Roles']

  roleExists = False

  for key in Role_list:

      if(key['RoleName'] == ec2_role):

        print("Role {0} already exists".format(ec2_role))

        roleExists = True

        """

        if(policy_arn is not None):

            print("Detaching policies from role before deleting")

            iam.detach_role_policy(

                RoleName=ec2_role,

                PolicyArn=policy_arn

            )

        iam.delete_role(

            RoleName=ec2_role

        )

        """

        break



  if(not roleExists):

    #create Role

    print("Creating ec2 Role...")



    #indica que é uma role para ser usada dentro do serviço lambda da aws

    trust_policy = {

        "Version": "2012-10-17",

        "Statement": [

            {

                "Sid": "",

                "Effect": "Allow",

                "Principal": {

                    "Service": "ec2.amazonaws.com"

                },

                "Action": "sts:AssumeRole"

            }

        ]

    }



    role_response = iam.create_role(

        Path='/',

        RoleName=ec2_role,

        Description='Role to grant access to s3',

        AssumeRolePolicyDocument=json.dumps(trust_policy)

    )



  """

  #if policy exists delete

  if policy_arn is not None:

    print("Policy {0} already exists, deleting...".format(s3_policy_name))

    response = iam.delete_policy(

        PolicyArn=policy_arn

    )

  """



  if policy_arn is None:

    print("Creating policy...")

    # Create a policy

    my_managed_policy = {

                "Version": "2012-10-17",

                "Statement": [

                    {

                        "Sid": "S3ListObjects",

                        "Effect": "Allow",

                        "Action": "s3:ListBucket",

                        "Resource": [

                            "arn:aws:s3:::dell-filtred-data",

                            "arn:aws:s3:::dell-artifacts",

                        ],

                    },

                   {

                        "Sid": "S3ObjectActions",

                        "Effect": "Allow",

                        "Action": "s3:*Object",

                        "Resource": [

                            "arn:aws:s3:::dell-filtred-data/*",

                            "arn:aws:s3:::dell-filtred-data",

                            "arn:aws:s3:::dell-artifacts/*",

                            "arn:aws:s3:::dell-artifacts",

                        ],

                    },

                ],

            }



    response = iam.create_policy(

        PolicyName=s3_policy_name,

        PolicyDocument=json.dumps(my_managed_policy)

    )



    policy_arn = response['Policy']['Arn']



  print("Attaching created policy with role")

  response = iam.attach_role_policy(

      RoleName=ec2_role, PolicyArn=policy_arn)



  if not profileExists:

    print("Adding role to instance profile")

    iam.add_role_to_instance_profile(

        InstanceProfileName=ec2_profile,

        RoleName=ec2_role

    )



  imageId = "ami-05c1fa8df71875112"

  tipo = 't2.micro'

  KeyName = 'ACESSO_SIMULACAO'

  create_key_pair(KeyName)

  print('key pairs created')

  security_group_id = create_security_group('sg_teste')

  print('security group created')

  print("Creating Instances")

  response = ec2.run_instances(

      ImageId=imageId,

      InstanceType=tipo,

      MinCount=1,

      MaxCount=1,

      KeyName=KeyName,

      IamInstanceProfile={

          'Name': ec2_profile

      },

      SecurityGroupIds=[security_group_id],

      UserData=script_commands(relationsList,dependeciesList,date_init,date_end))



  instances = response['Instances']

  createdInstancesId = [instance['InstanceId'] for instance in instances]

  time.sleep(1)



  print('waiting okay status')

  # Also wait status checks to complete

  waiter = ec2.get_waiter('instance_status_ok')

  waiter.wait(InstanceIds=createdInstancesId)



  print('instances status okay')




def startSimulation(params):
    return main(params)
