import os
from dotenv import load_dotenv
import psycopg2
import json
from datetime import datetime, timedelta
from prettytable import PrettyTable
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

MASKING_RULE_NAME = "MaskingRule"

AUDIT_RULE_NAME = "AuditRule"

TABLE_NAME = "random_data"

SCHEMA_NAME = "public"

CLI_PATH = "C:\Program Files\DataSunrise Database Security Suite\cmdline\executecommand.bat"


def execute_command(command):
    """
    Executes a DataSunrise CLI command.

    Args:
        command (list): List of command arguments.

    Returns:
        Output of the CLI command.
    """

    full_command = [CLI_PATH] + command
    result = run(full_command, capture_output=True, text=True)
    return result


def parse_json(result, multiple_json=False):
    """
    Parse the output of execute_command function to json

    Args:
        result (subprocess.CompletedProcess): Output of execute_command function(command should contain -json)
        multiple_json (Bool): Output contains several json objects
        
    Returns:
        Output in json
    """

    try:
        result = result.stdout

        if not multiple_json:
            json_str = result[result.index("-json")+5:]
            return json.loads(json_str)
        
        json_str = result[result.index("-json")+5:]
        json_lst = json_str.split("}\n{")

        for i in range(len(json_lst)):
            if i == 0:
                json_lst[0] += "}"
            elif i == len(json_lst)-1:
                json_lst[i] = "\n{" + json_lst[i]
            else:
                json_lst[i] = "\n{" + json_lst[i] + "}"
        
        return [json.loads(i) for i in json_lst]
    
    except Exception as e:
        print(f"Error during parsing: {e}")


def get_db_connection(port):
    """
    Returns a database connection object.
    """

    conn = psycopg2.connect(
        host=DB_HOST,
        port=port,
        database=DB_NAME,
        user=DB_LOGIN,
        password=DB_PASSWORD
    )
    return conn


def test_masking():
    """
    Tests the masking rule.
    """

    try:
        # Connect to DataSunrise proxy
        conn = get_db_connection(PROXY_PORT)
        cur = conn.cursor()

        # Execute a query through the proxy
        cur.execute(f"SELECT * FROM {SCHEMA_NAME}.{TABLE_NAME}")
        rows = cur.fetchall()

        # Check for masked data
        masked_data_found = False
        for row in rows:
            name, city = row[1], row[4]
            if name.startswith("**") or city.startswith("**"):
                masked_data_found = True
                break

        cur.close()
        conn.close()

        return masked_data_found

    except Exception as e:
        print(f"Error during masking test: {e}")
        return False
    

def test_audit_events(t):
    """
    Checks for masked data in audit events.

    Args:
        t (datetime): datetime of started event
    """
    
    try:
        # Connect to DataSunrise CLI
        connect_command = [
            "connect",
            "-host", DS_HOST,
            "-login", DS_LOGIN,
            "-password", DS_PASSWORD,
            "-protocol", DS_PROTOCOL,
        ]
        run([CLI_PATH] + connect_command)

        # Get sessions id
        show_sessions_command = [
            "showSessions",
            "-beginDate", f"{t}",
            "-json"
        ]
        result = execute_command(show_sessions_command)
        session_id = parse_json(result)["sessions"][1][0]

        # Get event information
        show_events_command = [
            "showEvents",
            "-id", f"{session_id}",
            "-rule", AUDIT_RULE_NAME,
            "-type", "audit",
            "-json"
        ]
        result = execute_command(show_events_command)
        event = parse_json(result)["events"][1]
        operation_id = event[1]
        exec_id = event[2]


        # Get event data
        show_event_command = [
            "showEvent",
            "-eid", f"{exec_id}",
            "-oid", f"{operation_id}",
            "-sid", f"{session_id}",
            "-json"
        ]
        result = execute_command(show_event_command)
        event_data = parse_json(result, multiple_json=True)[1]["data"][0]

        # Check if data is masked in audit event
        masked_audit_data_found = False
        for row in event_data[1:]:
            name, city = row[1], row[4]
            if name.startswith("**") or city.startswith("**"):
                masked_audit_data_found = True
                break

        return masked_audit_data_found

    except Exception as e:
        print(f"Error during audit events check: {e}")
        return False


def write_test_results(masking_result, audit_result):
    """
    Writes the test results to a file.
    """

    with open("test_results.txt", "w") as f:
        # Table for masking check
        masking_table = PrettyTable(["Test", "Expected Result", "Actual Result"])
        masking_table.add_row(["Data Masking", "True", masking_result])
        f.write("## Data Masking Test Results:\n")
        f.write(str(masking_table) + "\n\n")

        # Table for audit check
        audit_table = PrettyTable(["Test", "Expected Result", "Actual Result"])
        audit_table.add_row(["Masked Data in Audit", "True", audit_result])
        f.write("## Audit Events Check Results:\n")
        f.write(str(audit_table) + "\n")


if __name__ == "__main__":
    start_masking_checking = datetime.now()
    masking_result = test_masking()
    audit_result = test_audit_events(start_masking_checking)
    write_test_results(masking_result, audit_result)
    print("Test results written to 'test_results.txt'")