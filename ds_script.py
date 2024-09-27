import os
from dotenv import load_dotenv
from subprocess import run

# Load parameters from .env
load_dotenv()

# DataSunrise parameters
DS_HOST = os.getenv("DS_HOST")
DS_LOGIN = os.getenv("DS_LOGIN")
DS_PASSWORD = os.getenv("DS_PASSWORD")
DS_PROTOCOL = os.getenv("DS_PROTOCOL", "https")

# Database parameters
DB_TYPE = os.getenv("DB_TYPE", "postgresql")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_LOGIN = os.getenv("DB_LOGIN")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_INSTANCE_NAME = os.getenv("DB_INSTANCE_NAME", "PostgreSQL")
PROXY_PORT = os.getenv("PROXY_PORT", "5433")


def execute_command(command):
    """
    Executes a DataSunrise CLI command.

    Args:
        command (list): List of command arguments.
    """

    cli_path = "C:\Program Files\DataSunrise Database Security Suite\cmdline\executecommand.bat"
    full_command = [cli_path] + command
    run(full_command)


def main():
    """
    Main function of the script.
    """

    # 1. Connect to DataSunrise
    connect_command = [
        "connect",
        "-host", DS_HOST,
        "-login", DS_LOGIN,
        "-password", DS_PASSWORD,
        "-protocol", DS_PROTOCOL,
    ]
    execute_command(connect_command)

    # 2. Register PostgreSQL database
    add_instance_command = [
        "addInstancePlus",
        "-dbHost", DB_HOST,
        "-dbPort", DB_PORT,
        "-dbType", DB_TYPE,
        "-database", DB_NAME,
        "-login", DB_LOGIN,
        "-password", DB_PASSWORD,
        "-name", DB_INSTANCE_NAME,
        "-proxyHost", "0.0.0.0",
        "-proxyPort", PROXY_PORT
    ]
    execute_command(add_instance_command)

    # 3. Create masking rule
    masking_rule_command = [
        "addMaskRule",
        "-name", "MaskingRule",
        "-dbType", DB_TYPE,
        "-instance", DB_INSTANCE_NAME,
        "-action", "mask",
        "-maskType", "maskFirst",
        "-maskCount", "2",
        "-maskColumns", "db.public.random_data.name;db.public.random_data.city",
        "-login", DB_LOGIN,
        "-password", DB_PASSWORD,
        "-logInStorage", "true"
    ]
    execute_command(masking_rule_command)

    # 4. Create audit rule for SELECT queries
    audit_rule_command = [
        "addAuditRule",
        "-name", "AuditRule",
        "-dbType", DB_TYPE,
        "-instance", DB_INSTANCE_NAME,
        "-action", "audit",
        "-intercSqlSelect", "true",
        "-login", DB_LOGIN,
        "-password", DB_PASSWORD,
        "-logInStorage", "true",
        "-logData", "true"
    ]
    execute_command(audit_rule_command)


if __name__ == "__main__":
    main()