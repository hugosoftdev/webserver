""" EC2 Service """

import logging
import os
import boto3 as aws


ec2 = aws.client("ec2")
logging.basicConfig(format="%(asctime)s | EC2: %(message)s")


def create_security_group(group_name, group_description, group_permissions):
    """
    Creates a default security group for a EC2 instance

    Args:
        group_name (srt): Name given to the group
    """
    vpcs = ec2.describe_vpcs()
    vpc_id = vpcs.get("Vpcs", [{}])[0].get("VpcId", "")

    group = get_security_group(group_name)

    if group:
        logging.warning(f"Security group {group_name} already exists")
        group_id = group["GroupId"]
        delete_security_group(group_id)
        logging.warning(f"Security group {group_name} deleted")
    try:
        group = ec2.create_security_group(
            GroupName=group_name, Description=group_description, VpcId=vpc_id
        )
        ec2.authorize_security_group_ingress(
            GroupId=group["GroupId"], IpPermissions=[group_permissions]
        )
        logging.warning(f"Security group {group_name} created")
    except Exception as err:
        logging.exception(f"Create security group exception: {err}")

    return group


def get_security_group(group_name):
    """
    Get specified security group

    Args:
        group_name (srt): Name of the group
    """
    group = [
        group
        for group in ec2.describe_security_groups()["SecurityGroups"]
        if group["GroupName"] == group_name
    ]
    return group[0] if group else None


def delete_security_group(group_id):
    """
    Delete specified security group

    Args:
        group_name (srt): Name of the group
    """
    try:
        ec2.delete_security_group(GroupId=group_id)
    except Exception as err:
        logging.exception(f"Delete security group exception: {err}")


def create_key_pair(keypair_name):
    key = get_keypair(keypair_name)

    if key:
        logging.warning(f"Keypair {keypair_name} already exists")
        # delete_keypair(keypair_name)

    try:
        key = ec2.create_key_pair(KeyName=keypair_name)
        with open(f"{keypair_name}.pem", "w") as f:
            f.write(key["KeyMaterial"])
            os.chmod(f"./{keypair_name}.pem", 400)
        logging.warning(f"Keypair {keypair_name} created at {os.getcwd()}")

    except Exception as err:
        logging.exception(f"Create keypair exception: {err}")


def get_keypair(keypair_name):
    key = [
        key
        for key in ec2.describe_key_pairs()["KeyPairs"]
        if key["KeyName"] == keypair_name
    ]
    return key[0] if key else None


def delete_keypair(keypair_name):
    """
    Delete the specified keypair

    Args:
        keypair_name (str): Name of the keypair
    """

    # A keypair pode estar sendo utilizada em instâncias EC2. Deletar uma
    # pode cessar o possível acesso com a máquina.

    # # To-do: listar as instâncias em que a keypair está sendo usada, se
    # resultado for 0, deleta keypair, senão raise error.

    if os.path.exists(f"{keypair_name}.pem"):
        os.remove(f"{keypair_name}.pem")

    try:
        ec2.delete_key_pair(KeyName=keypair_name)
    except Exception as err:
        logging.exception(f"Delete keypair exception: {err}")


def deploy_instance(name, flavor, key_name, profile_name, sg_id, commands):
    instance = None
    try:
        instance = ec2.run_instances(
            ImageId="ami-05c1fa8df71875112",  # Ubuntu 18.04 LTS
            InstanceType=flavor,
            KeyName=key_name,
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[sg_id],
            UserData=commands,
            IamInstanceProfile={"Name": profile_name},
            InstanceInitiatedShutdownBehavior="terminate",
            TagSpecifications=[
                {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": name}]}
            ],
        )
    except Exception as err:
        logging.exception(f"Deploy instance exception: {err}")

    return instance


def set_waiter(instance, waiter_type, message):
    instance_id = [instance["InstanceId"] for instance in instance["Instances"]]
    waiter = ec2.get_waiter(waiter_type)
    waiter.wait(InstanceIds=instance_id)
    logging.warning(f"EC2 Waiter: {message}")
