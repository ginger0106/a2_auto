import os

os.system('docker stop `docker ps -a -q`')
os.system('docker rm `docker ps -a -q`')
print('done!')
