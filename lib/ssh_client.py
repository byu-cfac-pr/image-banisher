

import paramiko


class Client:

    def __init__(self, username, hostname, key_path, passphrase, optional_args=None):
        self.username = username
        self.hostname = hostname
        self.key_path = key_path
        self.passphrase = passphrase
        self.optional_args = optional_args
        self.construct_client()

    def construct_client(self):
        self.client = paramiko.SSHClient()
        key = paramiko.RSAKey.from_private_key_file(self.key_path, password=self.passphrase)
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        args = {
            'hostname': self.hostname,
            'username': self.username,
            'pkey': key,
        }
        if self.optional_args is not None:
            if 'port' in self.optional_args:
                args['port'] = self.optional_args['port']
            if 'password' in self.optional_args:
                args['password'] = self.optional_args['password']
        self.client.connect(**args)

    def do(self, cmd):
        try:
            stdin, stdout, stderr = self.client.exec_command(cmd)
        except paramiko.SSHException:
            self.construct_client()
            stdin, stdout, stderr = self.client.exec_command(cmd)
        return stdout.read().decode('utf-8').strip()

    def __del__(self):
        self.client.close()
