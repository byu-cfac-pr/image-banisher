

import paramiko


class Client:

    def __init__(self, username, hostname, key_path, passphrase):
        self.client = paramiko.SSHClient()
        key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(hostname=hostname, username=username, pkey=key)


    def do(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.read().decode('utf-8').strip()

    def __del__(self):
        self.client.close()
