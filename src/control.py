import paramiko
import sys
import logging
import colorlog

from config import *

# Configure logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'reset',
        'INFO': 'bold_blue',
        'WARNING': 'yellow',
        'ERROR': 'bold_red',
        'CRITICAL': 'bold_red',
    }
))
logger = colorlog.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def ssh_connect(target, port, ssh_user, ssh_pass):
    """Establish an SSH connection to the remote host."""
    logger.info(f"Establishing connection to {target} on {port} (SSH).")
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(target, port=port, username=ssh_user, password=ssh_pass)
        logger.info(f"Connected to {target} on {port}.")
        return client
    except paramiko.SSHException as e:
        logger.error(f"Failed to connect to {target}: {e}")
        sys.exit(1)


def clean_potential_leftovers(client, hostname, remote_script_path):
    """Delete previously executed scripts."""
    output, errors = execute_remote_command(client, f"if [ -f {remote_script_path} ]; then rm {remote_script_path}; fi")
    if errors:
        logger.error(f"Error checking/deleting file: {errors}")
    else:
        logger.info(f"Checked and deleted previous runner script '{remote_script_path}' on {hostname} (if it existed).")


def sftp_transfer(client, local_path, remote_path, target):
    """Transfer a file to the remote host using SFTP."""
    try:
        sftp = client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        logger.info(f"Transferred {local_path} to {remote_path} on {target}.")
    except Exception as e:
        logger.error(f"Failed to transfer {local_path} to {remote_path} on {target}: {e}")


def execute_runner_script_on_target(client, remote_python_path, remote_script_path):
    """Execute a runner script on the remote host."""
    logger.info(f"Executing runner script on: {remote_script_path}")
    output, errors = execute_remote_command(client, f"{remote_python_path} {remote_script_path}")
    if errors:
        logger.error(f"Error running script: {errors}")
    else:
        logger.info(f"\nOutput:\n {output}")


def clean_device(client, hostname, remote_script_path):
    """Delete executed script from target."""
    output, errors = execute_remote_command(client, f"rm {remote_script_path}")
    if errors:
        logger.error(f"Error deleting file: {errors}")
    else:
        logger.info(f"Deleted {remote_script_path} on {hostname}.")


def execute_remote_command(client, command):
    """Execute a command on the remote host. Redirect I/O to us."""
    try:
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode()
        errors = stderr.read().decode()
        return output, errors
    except Exception as e:
        logger.error(f"Failed to execute command '{command}': {e}")
        return "", str(e)


def main():
    # Establish SSH connection with the iOS device
    client = ssh_connect(target, port, ssh_user, ssh_pass)

    # Check if a previous runner script already exists on the remote device and delete it so.
    clean_potential_leftovers(client, target, remote_script_path)

    # Transfer the script to the remote device
    sftp_transfer(client, local_script_path, remote_script_path, target)

    # Run the runner script on the remote device
    execute_runner_script_on_target(client, remote_python, remote_script_path)

    # Delete the runner script from the remote device after execution ends.
    clean_device(client, target, remote_script_path)

    # Close the SSH connection
    client.close()


if __name__ == "__main__":
    main()
