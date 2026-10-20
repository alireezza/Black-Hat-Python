import paramiko 

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient() 
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    
    _, stdout, stderr = client.exec_command(cmd)
    output = stdout.readlines() + stderr.readlines()
    if output: 
        print('___ Output ___')
        for line in output:
            print(line.strip())
            
if __name__ == "__main__":
    import getpass 
    # user = getpass.getuser()
    user = input('Username: ')
    passwd = getpass.getpass() 
    
    ip = input('Enter target IP: ')
    port = int(input('Enter target port: '))
    command = input('Enter command to execute: ')
    ssh_command(ip, port, user, passwd, command)
# Execute a command on a remote host over SSH using Paramiko.

    