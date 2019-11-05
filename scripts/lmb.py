""" Lambda Service """

import logging
import os
import shutil
import boto3 as aws

lambda_service = aws.client("lambda")
logging.basicConfig(format="%(asctime)s | Lambda: %(message)s")


def create_lambda_function(**params):
    """
    Create a Lambda Function in the Lambda Service

    Args:
        **params (dict): {
            FunctionName, Runtime, Role,
            Timeout, MemorySize, Handler, File
        }
    """
    function_name = params["FunctionName"]
    file_path = params["File"]

    lambda_function = get_lambda_function(function_name)
    if lambda_function:
        logging.warning(f"Lambda function {function_name} already exists")
        delete_lambda_function(function_name)
        logging.warning(f"Lambda function {function_name} deleted")

    if os.path.exists(f"{file_path}.zip"):
        os.remove(f"{file_path}.zip")

    shutil.make_archive(file_path, "zip", file_path)

    try:
        lambda_function = lambda_service.create_function(
            FunctionName=function_name,
            Runtime=params["Runtime"],
            Role=params["Role"],
            Timeout=params["Timeout"],
            MemorySize=params["MemorySize"],
            Handler=params["Handler"],
            Code={"ZipFile": open(f"{file_path}.zip", "rb").read()},
            Layers=params["Layer"] if params["Layer"] else None,
        )
        logging.warning(f"Lambda function {function_name} created")

    except Exception as err:
        logging.exception(f"Create lambda function exception: {err}")

    return lambda_function


def get_lambda_function(function_name):
    """
    Return a list with the specified lambda function

    Args:
        function_name (str): Name of the lambda function
    """
    lambda_function = [
        function
        for function in lambda_service.list_functions()["Functions"]
        if function["FunctionName"] == function_name
    ]
    return lambda_function[0] if lambda_function else None


def delete_lambda_function(function_name):
    """
    Delete a given lambda function

    Args:
        function_name (str): Name of the lambda function
    """
    try:
        lambda_service.delete_function(FunctionName=function_name)
    except Exception as err:
        logging.exception(f"Delete lambda function exception: {err}")


def create_lambda_layer(**params):
    """
    Create a Lambda Layer in the Lambda Service

    Args:
        **params (dict): {LayerName, Description, File, Runtime}
    """
    layer_name = params["LayerName"]

    lambda_layer = get_lambda_layer(layer_name)
    if lambda_layer:
        logging.warning(f"Lambda Layer {layer_name} already exists")
        delete_lambda_layer(lambda_layer)
        logging.warning(f"Lambda Layer {layer_name} deleted")

    try:
        lambda_layer = lambda_service.publish_layer_version(
            LayerName=layer_name,
            Description=params["Description"],
            Content={"ZipFile": open(params["File"], "rb").read()},
            CompatibleRuntimes=params["Runtime"],
        )
        logging.warning(f"Lambda Layer {layer_name} created")

    except Exception as err:
        logging.exception(f"Create lambda layer exception: {err}")

    return lambda_layer


def get_lambda_layer(layer_name):
    """
    Return a list with the specified lambda layer

    Args:
        layer_name (str): Name of the lambda layer
    """
    lambda_layer = [
        layer
        for layer in lambda_service.list_layers()["Layers"]
        if layer["LayerName"] == layer_name
    ]
    return lambda_layer[0] if lambda_layer else None


def delete_lambda_layer(lambda_layer):
    """
    Delete a given lambda layer

    Args:
        lambda_layer (str): Name of the lambda layer
    """
    try:
        layer_version = lambda_layer["LatestMatchingVersion"]["Version"]
        layer_name = lambda_layer["LayerName"]
        lambda_service.delete_layer_version(
            LayerName=layer_name, VersionNumber=layer_version
        )
    except Exception as err:
        logging.exception(f"Delete lambda layer exception: {err}")


def create_layer_files(layer_path, layer_file):
    """
    Runs a shell script on the layer_path, creating the layer zip file

    Args:
        layer_path (str): Path of the lambda layer folder
        layer_path (str): Path of the lambda layer zip file
    """
    layer_dep_folder = layer_path + "/python"

    if os.path.exists(layer_file):
        os.remove(layer_file)

    os.system(layer_path + "/install_dependencies.sh")
    logging.warning(f"Lambda Layer file created")

    if os.path.exists(layer_dep_folder):
        shutil.rmtree(layer_dep_folder)
