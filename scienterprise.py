import click
import json
import paramiko
import sys
import os
import docker
import time

filename = 'user-server.json'

def usertest():
    try:
        f=open('user.json')
        f.close()
        return True
    except IOError:
        print("There is no userfile, please use \n        scienterprise setusr \nbefore uploading or downloading.")
        return False

# def remoteConnectSSHCommand(ip,port,user,password,ssh_command_list):
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect(ip, port, user, password, timeout=1000)
    # for ssh_command in ssh_command_list:      
        # stdin, stdout, stderr = ssh.exec_command(ssh_command)
        # result = stdout.read()
        # if result:
            # print(result.decode())
    # ssh.close()
    
    
def tempUpload(ip, port, username, password, target, dest, container_id):
    transport = paramiko.Transport((ip, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(target, dest)
    ssh = paramiko.SSHClient()
    ssh._transport = transport
    file_name=target.split('\\')[-1]
    dest_path="/root/ScienterpriseServer/temporary/"
    ssh_command=f'docker cp {dest_path}{file_name} {container_id}:/home/boincadm/project/{file_name}'
    stdin, stdout, stderr=ssh.exec_command(ssh_command)
    result = stdout.read()
    # print(result.decode())
    print(target, "uploaded successfully")
    transport.close()
    
    
# def runApp(ip, container_id, appname, input):
    # client = docker.DockerClient(base_url='tcp://'+ip+':2375')
# #     images=client.images.list()
    # container=client.containers
# #     print(images)
# #     print(container)
    # C=container.get(container_id)
    # out=C.exec_run(f'bin/create_work --appname {appname} {input}').output.decode()
    # workunit=out.split(':')[-1]
    # print('workunit', workunit)
# #     print(container.list())
    # return workunit

def runApp(ip, port, username, password, container_name, appname, input_dir):
    transport = paramiko.Transport((ip, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    ssh = paramiko.SSHClient()
    ssh._transport = transport
#     ssh_command=f'docker exec {container_name} "bin/create_work --appname {appname} input"'
    if appname=='gromacs':
        print('running gromacs')
        ssh_command=f'docker exec {container_name} sh -c "mv {input_dir} md_0_1.tpr"'
        stdin, stdout, stderr=ssh.exec_command(ssh_command)
        result = stdout.read()
        ssh_command=f'docker exec {container_name} sh -c "bin/create_work --appname {appname} --target_user 1 md_0_1.tpr"'
        stdin, stdout, stderr=ssh.exec_command(ssh_command)
        result = stdout.read().decode()
        workunit=result.split(':')[-1]
        print('workunit', workunit)
    else:
        ssh_command=f'docker exec {container_name} sh -c "bin/stage_file {input_dir}"'
        stdin, stdout, stderr=ssh.exec_command(ssh_command)
        result = stdout.read()
    #     print(result.decode())
        ssh_command=f'docker exec {container_name} sh -c "bin/create_work --appname {appname} {input_dir}"'
        stdin, stdout, stderr=ssh.exec_command(ssh_command)
        result = stdout.read().decode()
        workunit=result.split(':')[-1]
        print('workunit', workunit)
    transport.close()
    return workunit
    
def tempDownloadDir(ip, port, username, password, remote_path, remote_dir, local_path, container_id):
    transport = paramiko.Transport((ip, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    dir_name=remote_path.split('/')[-1]
    local_path=local_path+'/'+dir_name
    print("Downloading from "+dir_name)
    
    ssh = paramiko.SSHClient()
    ssh._transport = transport
    dest_path="/root/ScienterpriseServer/temporary/"
    remote_path='/root/ScienterpriseServer/temporary/'+remote_dir
    ssh_command=f'docker cp {container_id}:/home/boincadm/project/upload/{remote_dir} {remote_path}'
    stdin, stdout, stderr=ssh.exec_command(ssh_command)
    result = stdout.read()
    
    # print(result.decode())
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    for file in sftp.listdir(remote_path):
        # print(file)
        sftp.get(remote_path+'/'+file, local_path+'/'+file)
        print(dir_name, file, "downloaded successfully")
    
    
    temp_list=sftp.listdir(remote_path)
    for f in temp_list:
        sftp.remove(remote_path+'/'+f)
    sftp.rmdir(remote_path)
    transport.close()

def downloadThroughWorkUnit(ip, port, username, password, local_path, container_name, container_id, work_unit):
    r=findWorkUnit(ip, port, username, password, container_name, work_unit)
    p=r.split('\n')
    file_list=[]
    for i in range(0,len(p)-1):
        file_list.append(p[i].split('/')[2])
    transport = paramiko.Transport((ip, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport) 
    ssh = paramiko.SSHClient()
    ssh._transport = transport
    container_path='/home/boincadm/project/upload/'
    dest_path="/root/ScienterpriseServer/temporary/"
    if not os.path.exists(local_path):
            os.makedirs(local_path)
    for f in file_list:
        ssh_command=f'docker cp {container_id}:{container_path}{f} {dest_path}{f}'
        #print(ssh_command)
        stdin, stdout, stderr=ssh.exec_command(ssh_command)
#         print(stdout)
    print("Preparing files...")
    time.sleep(5)
    print("Processing...")
    for f in file_list:
        remote_path=dest_path+f
        #print(remote_path)
        local_path_f=local_path+'/'+f
        print("Downloading to " + local_path_f)
        if not os.path.exists(local_path_f):
            os.makedirs(local_path_f)
        for file in sftp.listdir(remote_path):
            print("Start downloading "+ file)
            sftp.get(remote_path+'/'+file, local_path_f+'/'+file)
            print(file, "downloaded successfully")
            
    for f in file_list:
        remote_path=dest_path+f
        temp_list=sftp.listdir(remote_path)
        for tf in temp_list:
            sftp.remove(remote_path+'/'+tf)
        sftp.rmdir(remote_path)
    transport.close()

def findWorkUnit(ip, port, username, password, container_name, work_unit):
    transport = paramiko.Transport((ip, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    ssh = paramiko.SSHClient()
    ssh._transport = transport

    ssh_command=f'docker exec {container_name} sh -c "find -name *{work_unit}*"'
    stdin, stdout, stderr=ssh.exec_command(ssh_command)
    result = stdout.read().decode()
    return result

@click.group()
def cli():
    click.echo("Using Scienterprise")



@cli.command()
@click.option('--target', default=None, help="Enter the path of the files or programs you want to upload", prompt="Which file do you want to upload?")
# @click.option('--container_id', default=None, help="Enter the container ID", prompt="Please input the container ID?")
def upload(target):
    '''
    Upload the target program.
    '''
    user = {}
    if usertest()==False:
        return
    else:
        with open(filename, 'r') as f:
            user = json.load(f)
    if(target):
        print("The target is " +target )
        '''
        Modify here!!!!
        '''
        ip=user["ip"]
        port=user["port"]
        username=user["username"]
        password=user["passwd"]
        container_id=user["container_id"]
        file_name=target.split('\\')[-1]
        dest_path="/root/ScienterpriseServer/temporary/"
        dest=dest_path+file_name
        # ssh_command_list=['docker ps',
                          # f'docker cp {dest_path}{file_name} {container_id}:/home/boincadm/project/{file_name}']
        tempUpload(ip, port, username, password, target, dest, container_id)
        # remoteConnectSSHCommand(ip,port,username,password,ssh_command_list)
        print(f"{target} has been uploaded to containerID={container_id}")
    else:
        print("No target or containerID is specified.")
        return



@cli.command()
@click.option('--local_path', default='.', help="Enter the path you want to download to")
# @click.option('--container_id', default=None, help="Enter the path of the target location", prompt="container id: ")
@click.option('--remote_dir', default=None, help="Enter the path of the target location")
@click.option('--workunit', default=None, help="Enter the work unit")
def download(local_path,remote_dir,workunit):
    '''
    Download ther result based on 'workunit' or 'remote_dir'.
    '''
    user = {}
    if usertest()==False:
        return
    else:
        with open(filename, 'r') as f:
            user = json.load(f)

    ip=user["ip"]
    port=user["port"]
    username=user["username"]
    password=user["passwd"]
    container_id=user["container_id"]
    container_name=user["container_name"]
    containerID=container_id

    if(local_path == '.'):
        click.echo("Download to current working directory: " + os.getcwd() )

    if((remote_dir != None) and (workunit != None)):
        click.echo("Please only choose one way to find the remote address, 'remote_dir' or 'workunit'.")
        return
    elif(remote_dir):
        remote_path='/root/ScienterpriseServer/temporary/'+remote_dir
        #ssh_command_list=['docker ps',f'docker cp {containerID}:/home/boincadm/project/upload/{remote_dir} {remote_path}']
        # remoteConnectSSHCommand(ip,port,username,password,ssh_command_list)
        tempDownloadDir(ip, port, username, password, remote_path, remote_dir, local_path, container_id)
    elif(workunit):
        downloadThroughWorkUnit(ip, port, username, password, local_path, container_name, container_id, workunit)
    
    else:
        click.echo("Neither remote_dir nor workunit is specified. Fail to download")

        return



@cli.command()
@click.option('--app_name', default=None, help="Enter the path of the files or programs you want to download", prompt="local path")
@click.option('--input', default=None, help="Enter the path of the files or programs you want to download", prompt="local path")
# @click.option('--container_id', default=None, help="Enter the path of the target location", prompt="container id: ")
def run(app_name, input):
    '''
    Run the program based on 'app_name' and 'input'
    '''
    user = {}
    if usertest()==False:
        return
    else:
        with open(filename, 'r') as f:
            user = json.load(f)
    # print(user)#test
    ip=user["ip"]
    port=user["port"]
    username=user["username"]
    password=user["passwd"]
    container_id=user["container_id"]
    container_name=user["container_name"]
    workunit=runApp(ip, port, username, password, container_name, app_name, input)


@cli.command()
@click.option('--workunit', default=None, help="Enter the work unit", prompt="Enter the work unit")
def check_workunit(workunit):
    '''
    Check the directory of the result of the work unit.
    '''
    click.echo("Checking "+workunit)
    user={}
    with open(filename, 'r') as f:
            user = json.load(f)
    ip=user["ip"]
    port=user["port"]
    username=user["username"]
    password=user["passwd"]
    container_id=user["container_id"]
    container_name=user["container_name"]
    r=findWorkUnit(ip, port, username, password, container_name, workunit)
    if(r==''):
        print("No such workunit")
    else:
        p=r.split('\n')
        for i in range(0,len(p)-1):
            print(p[i].split('/')[2]+'/'+p[i].split('/')[3])
            
            
# @cli.command()
# @click.option('--local_path', default='.', help="Enter the path you want to download to")
# @click.option('--workunit', default=None, help="Enter the work unit", prompt="Enter the work unit")
# def download_workunit(local_path, workunit):
#     user={}
#     with open(filename, 'r') as f:
#             user = json.load(f)
#     ip=user["ip"]
#     port=user["port"]
#     username=user["username"]
#     password=user["passwd"]
#     container_id=user["container_id"]
#     container_name=user["container_name"]
#     downloadThroughWorkUnit(ip, port, username, password, local_path, container_name, container_id, workunit)
