import os
import time
from scripts import iam, ec2, aux_sim

FILE_DIR = os.path.dirname(__file__)
FILTERED_BUCKET = "dell-filtered-data"
ARTIFACTS_BUCKET = "dell-artifacts"
SIMULATOR_POLICY = "SimulatorPolicy"
SIMULATOR_ROLE = "SimulatorRole"
SIMULATOR_PROFILE = "SimulatorProfile"
SIMULATOR_SG = "SimulatorSG"
KEYPAIR = "SimulatorKey"


simulator_policy_content = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "S3ListObjects",
            "Effect": "Allow",
            "Action": "s3:ListBucket",
            "Resource": [
                f"arn:aws:s3:::{ARTIFACTS_BUCKET}",
                f"arn:aws:s3:::{FILTERED_BUCKET}",
            ],
        },
        {
            "Sid": "S3ObjectActions",
            "Effect": "Allow",
            "Action": "s3:*Object",
            "Resource": [
                f"arn:aws:s3:::{ARTIFACTS_BUCKET}/*",
                f"arn:aws:s3:::{ARTIFACTS_BUCKET}",
                f"arn:aws:s3:::{FILTERED_BUCKET}/*",
                f"arn:aws:s3:::{FILTERED_BUCKET}",
            ],
        },
    ],
}

simulator_role_content = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {"Service": "ec2.amazonaws.com"},
            "Action": "sts:AssumeRole",
        }
    ],
}

SIMULATOR_SG_PERMISSIONS = {
    "IpProtocol": "tcp",
    "FromPort": 22,
    "ToPort": 22,
    "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
}


def init_simulator():

    # Create IAM permissions for the Simulator Instance
    simulator_role = iam.create_role(SIMULATOR_ROLE, simulator_role_content)
    simulator_policy = iam.create_policy(SIMULATOR_POLICY, simulator_policy_content)
    iam.attach_role_policy(SIMULATOR_ROLE, simulator_policy["Policy"]["Arn"])
    simulator_profile = iam.create_instance_profile(SIMULATOR_PROFILE)
    iam.attach_role_profile(SIMULATOR_ROLE, SIMULATOR_PROFILE)

    # Create Security Group for the Simulator Instance
    sg_simulador = ec2.create_security_group(
        SIMULATOR_SG, "Default SG Configuration SSH Only", SIMULATOR_SG_PERMISSIONS
    )

    # Create Keypair used to create Simulator Instance
    ec2.create_key_pair(KEYPAIR)


def get_simulator_infra():
    sg = ec2.get_security_group(SIMULATOR_SG)
    policy = iam.get_policy(SIMULATOR_POLICY)
    role = iam.get_role(SIMULATOR_ROLE)
    profile = iam.get_instance_profile(SIMULATOR_PROFILE)
    keypair = ec2.get_keypair(KEYPAIR)

    simulator_data = {
        "SecurityGroup": sg,
        "Policy": policy,
        "Role": role,
        "Profile": profile,
        "Keypair": keypair,
    }

    return simulator_data


def deploy_simulator(simulator_settings):
    simulator = get_simulator_infra()
    commands = aux_sim.script_commands(simulator_settings)

    sg_id = simulator["SecurityGroup"]["GroupId"]
    profile_name = simulator["Profile"]["InstanceProfileName"]
    keypair_name = simulator["Keypair"]["KeyName"]

    instance = ec2.deploy_instance(
        "Simulador", "t2.micro", keypair_name, profile_name, sg_id, commands
    )
    ec2.set_waiter(instance, "instance_status_ok", "Simulator Created")


# /var/log/cloud-init-output.log
# sudo shutdown -H now
