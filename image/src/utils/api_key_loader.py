import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(override=False)

def get_google_api_key():
    """
    Returns Google API Key depending on the os environment.

    Return:
    str: The value of Google API Key
    """
    print(f"Google API Key Param: {os.getenv('GOOGLE_API_KEY_PARAM')}")

    if 'AWS_EXECUTION_ENV' in os.environ:
        try:
            ssm = boto3.client('ssm')
            api_key_param = os.getenv("GOOGLE_API_KEY_PARAM")
            response = ssm.get_parameter(
                Name=api_key_param,
                WithDecryption=True
            )
            return response['Parameter']['Value']
        except ClientError as e:
            print(f"SSM error: {e}")
            return None

    return os.getenv("GOOGLE_API_KEY")
