import subprocess
from shlex import quote
import asyncio
import json


class Shell(object) :

    def runCmd(self, cmd) :
        res = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        sout2 ,serr = res.communicate()
        # sout2 = res.stdout.read().decode().splitlines()
        return  sout2 #res.returncode, sout, serr, res.pid

formatt = "{\"container\":\"{{ .Name }}\",\"memory\":{\"raw\":\"{{ .MemUsage }}\",\"percent\":\"{{ .MemPerc }}\"},\"cpu\":\"{{ .CPUPerc }}\"}".strip('\n')
# cmd = "docker stats --no-stream --format {\"container\":\"{{ .Name }}\",\"memory\":{\"raw\":\"{{ .MemUsage }}\",\"percent\":\"{{ .MemPerc }}\"},\"cpu\":\"{{ .CPUPerc }}\",\"networkIO\":\"{{.NetIO}}\",\"BlockIO\":\"{{.BlockIO}}\"}"
# cmd = ['docker', 'stats','--no-stream','--format','{\"container\":\"{{ .Name }}\",\"memory\":{\"raw\":\"{{ .MemUsage }}\",\"percent\":\"{{ .MemPerc }}\"},\"cpu\":\"{{ .CPUPerc }}\",\"networkIO\":\"{{.NetIO}}\",\"BlockIO\":\"{{.BlockIO}}\"}']
# cmd = ['ls','-a']
cmd = 'docker stats --no-stream --format {}'.format(quote(formatt))
# cmd = ' '.join(cmd)
print(cmd)
p = Shell().runCmd(cmd).decode().splitlines()
print(p)

# print(cmd)----p000000000000000000000

q= [json.loads(i) for i in p]
print(q)
