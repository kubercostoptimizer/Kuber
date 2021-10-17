import subprocess

class ssh:
    def run_command_on_host(self,host,pwd,cmd):
            try:
                return subprocess.check_output(["sshpass -p "+pwd +" ssh -t "+host+" "+cmd], shell=True)
            except Exception as e:
                logging.error(str(e.output))
            return b''

ssh_client = ssh()