# Command Line Interface

Four commands are provided to manage the project on the server.

## Requirements
- Python3, pip
### Libraries of Python
- paramiko (to manage SSH by python)
- docker (might be needed in the future)
- python-click

## Build and Run the CLI
Clone this repo to your machine,
```bash
git clone git@github.com:scienterprise/ScienterpriseCLI.git
```
then run it,
```bash
cd ScienterpriseCLI
pip install --editable .
```

## Commmands Supported by the CLI
Now the information of the server and the container is included in the user-server.json. You can change it to other servers or containers.

**Upload Command**
- A file can be uploaded to the container by 
```bash
scienterprise upload --target ${file name}
```

**Run Command**
- A (gromacs) project can be started to run on the server by
```bash
scienterprise run --app_name gromacs --input ${file name}
```
- The workunit of this project will be returned. The statu of the project can be checked in http://47.100.27.38/ops/

**Download Command**
- The result files can be downloaded from the server by
```bash
scienterprise download --local_path ${directory name} --workunit ${workunit from above}
```
- Another way to download result files is through
```bash
scienterprise download --remote_dir ${directory on the server} --local_path ${directory in your machine}
```
Directory on the server only includes 2 to 3 bits of hexadecimals, like 160

**Check Command**
- The path of the result files can be checked by workunit.
```bash
scienterprise check-workunit --workunit {workunit}
```
