import os
import logging
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

logger = logging.getLogger(__name__)


def load_secrets_to_env_var():
    try:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)

        # Specify all the secrets you want to integrate into this app as environment variables
        # the dict is {"<Secret name in AKV>":"<environmet variable name you name in this app>"}
        secrets = [{"OPENAI-API-KEY": "OPENAI_API_KEY"}]

        logger.info(f"Retrieving your secret from {keyVaultName}.")

        # build them into environment variables
        for secret_name in secrets.keys():
            retrieved_secret = client.get_secret(secret_name)
            os.environ[secrets[secret_name]] = retrieved_secret.value
    except Exception as e:
        logger.exception(
            f"""Loading secrets from AKV has failed due to the following error. Please ignore this if you are in local environmet:\n{e}"""
        )
    else:
        logger.info("Succeeded in loading secrets from AKV!")
