"""Edit this file to be compatible with your settings"""

target = '10.0.0.38'                         # Your iOS ip address.
port = 22                                       # device's SSH port (default=22).
ssh_user = 'root'                               # iOS SSH username (should run with root privileges).
ssh_pass = 'alpine'                             # iOS SSH password.
local_script_path = 'runner.py'                 # Path to the runner python script.
remote_script_path = '/var/mobile/runner.py'    # iOS path to place the runner python script in.
remote_python = 'python'                        # Command or path to run python on iOS.
