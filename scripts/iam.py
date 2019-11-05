""" IAM Service """

import logging
import json
import boto3 as aws

iam = aws.client("iam")
logging.basicConfig(format="%(asctime)s | IAM: %(message)s")


def create_policy(policy_name, policy_content):
    """
    Create a Policy in the IAM Service

    Args:
        policy_name (str): Name of the policy policy
        policy_content (dict): Policy specifications (resources and actions)
    """
    policy = get_policy(policy_name)
    if policy:
        logging.warning(f"Policy {policy_name} already exists")
        delete_policy(policy["Arn"])
        logging.warning(f"Policy {policy_name} deleted")

    try:
        policy = iam.create_policy(
            PolicyName=policy_name, PolicyDocument=json.dumps(policy_content)
        )
        logging.warning(f"Policy {policy_name} created")

    except Exception as err:
        logging.exception(f"Create policy exception: {err}")

    return policy


def create_role(role_name, role_content):
    """
    Create a Role in the IAM Service

    Args:
        role_name (str): Name of the role
        role_content (dict): Role specifications
    """
    role = get_role(role_name)
    if role:
        logging.warning(f"Role {role_name} already exists")
        delete_role(role_name)
        logging.warning(f"Role {role_name} deleted")

    try:
        role = iam.create_role(
            Path="/",
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(role_content),
        )
        logging.warning(f"Role {role_name} created")

    except Exception as err:
        logging.exception(f"Create role exception: {err}")

    return role


def get_policy(policy_name):
    """
    Return a list with the specified policy

    Args:
        policy_name (str): Name of the policy
    """
    pages = iam.get_paginator("list_policies").paginate()
    policy = [
        policy
        for page in pages
        for policy in page["Policies"]
        if policy["PolicyName"] == policy_name
    ]
    return policy[0] if policy else None


def get_role(role_name):
    """
    Return a list with the specified role

    Args:
        role_name (str): Name of the role
    """
    roles = iam.list_roles()["Roles"]
    role = [role for role in roles if role["RoleName"] == role_name]
    return role[0] if role else None


def delete_policy(policy_arn):
    """
    Delete a given policy

    Args:
        policy_name (str): Name of the policy
    """
    try:
        iam.delete_policy(PolicyArn=policy_arn)
    except Exception as err:
        logging.exception(f"Delete policy exception: {err}")


def delete_role(role_name):
    """
    Detach all policies from specified role and deletes it

    Args:
        role_name (str): Name of the role
    """
    try:
        iam_res = aws.resource("iam")
        role = iam_res.Role(role_name)
        for policy in role.attached_policies.all():
            iam.detach_role_policy(RoleName=role_name, PolicyArn=policy.arn)

        for profile in role.instance_profiles.all():
            iam.remove_role_from_instance_profile(
                InstanceProfileName=profile.name, RoleName=role_name
            )
        iam.delete_role(RoleName=role_name)

    except Exception as err:
        logging.exception(f"Delete role exception: {err}")


def attach_role_policy(role_name, policy_arn):
    """
    Attach policy to specified role

    Args:
        role_name (str): Name of the role
        policy_arn (str): Arn of the policy
    """
    try:
        iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
        logging.warning(f"Policy attached to {role_name} role")

    except Exception as err:
        logging.exception(f"Attach policy to role exception: {err}")


def create_instance_profile(profile_name):
    """
    Create a Instance profile with the given name

    Args:
        profile_name (str): Name of the instance profile
    """
    profile = get_instance_profile(profile_name)

    if profile:
        logging.warning(f"Instance profile {profile_name} already exists")
        # delete_instance_profile(profile_name, role_name)

    try:
        profile = iam.create_instance_profile(InstanceProfileName=profile_name)
        logging.warning(f"Instance profile {profile_name} created")

    except Exception as err:
        logging.exception(f"Create instance profile exception: {err}")

    return profile


def get_instance_profile(profile_name):
    """
    Return a list with the specified instance profile

    Args:
        profile_name (str): Name of the instance profile
    """
    profile = [
        profile
        for profile in iam.list_instance_profiles()["InstanceProfiles"]
        if profile["InstanceProfileName"] == profile_name
    ]
    return profile[0] if profile else None


def delete_instance_profile(profile_name, role_name):
    """
    Delete the specified instance profile

    Args:
        profile_name (str): Name of the instance profile
    """

    # A instance profile pode estar sendo utilizada em instâncias EC2.
    # Deletar o profile sem desvincular das instâncias pode gerar diversos
    # erros.

    # # To-do: listar as instâncias em que o profile está sendo usado, se
    # resulto for 0, deleta profile, senão raise error.

    iam.remove_role_from_instance_profile(
        InstanceProfileName=profile_name, RoleName=role_name
    )
    iam.delete_instance_profile(InstanceProfileName=profile_name)


def attach_role_profile(role_name, profile_name):
    """
    Attach a role to a instance profile

    Args:
        role_name (str): Name of the role
        profile_name (str): Name of the instance profile
    """
    try:
        iam.add_role_to_instance_profile(
            InstanceProfileName=profile_name, RoleName=role_name
        )
        logging.warning(f"Role {role_name} attached to {profile_name} profile")

    except Exception as err:
        logging.exception(f"Attach role to profile exception: {err}")
