""" CloudWatch Event """

import logging
import boto3 as aws

cw = aws.client("events")
logging.basicConfig(format="%(asctime)s | Cloudwatch: %(message)s")


def create_rule(rule_name, cron_expression, target_arn):
    """
    Creates a rule in Cloudwatch that activates a resource based on time

    Args:
        rule_name (srt): Name given to the rule
        cron_expression (srt): Cron expression that describes the schedule
        target_arn (srt): Arn of the resource
    """
    rule = get_rule(rule_name)
    if rule:
        logging.warning(f"Rule {rule_name} already exists")
        cw.remove_targets(Rule=rule_name, Ids=[rule_name], Force=True)
        cw.delete_rule(Name=rule_name)
        logging.warning(f"Rule {rule_name} deleted")

    try:
        rule = cw.put_rule(
            Name=rule_name, ScheduleExpression=cron_expression, State="ENABLED"
        )
        logging.warning(f"Rule {rule_name} created")
        cw.put_targets(Rule=rule_name, Targets=[{"Arn": target_arn, "Id": rule_name}])
        logging.warning(f"Rule {rule_name} attached to target")

    except Exception as err:
        logging.exception(f"Create rule exception: {err}")

    return rule


def get_rule(rule_name):
    rules = cw.list_rules()["Rules"]
    rule = [rule for rule in rules if rule["Name"] == rule_name]
    return rule[0] if rule else None
