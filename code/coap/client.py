"""CoAP client for lab13, using only the Python standard library."""
import argparse,hashlib,json,secrets,socket,time

def uint(v):return v.to_bytes((v.bit_length()+7)//8,'big')
def encode(mid,token,path,typ=0,options=()):
 opts=[(11,p.encode()) for p in path.strip('/').split('/')]+list(options);opts.sort();b=bytearray([0x40|(typ<<4)|len(token),1,mid>>8,mid&255]);b+=token;prev=0
 def nib(v):
  if v<13:return v,b''
  if v<269:return 13,bytes([v-13])
  return 14,(v-269).to_bytes(2,'big')
 for n,v in opts:
  d,de=nib(n-prev);l,le=nib(len(v));b+=bytes([(d<<4)|l])+de+le+v;prev=n
 return bytes(b)
def decode(b):
 if len(b)<4 or b[0]>>6!=1:raise ValueError('bad header')
 k=b[0]&15
 if k>8 or len(b)<4+k:raise ValueError('bad token')
 i=4+k;opts={};num=0
 def ext(x):
  nonlocal i
  if x<13:return x
  if x==13:v=13+b[i];i+=1;return v
  if x==14:v=269+int.from_bytes(b[i:i+2],'big');i+=2;return v
  raise ValueError('reserved option')
 while i<len(b) and b[i]!=255:
  x=b[i];i+=1;d=ext(x>>4);n=ext(x&15);num+=d
  if i+n>len(b):raise ValueError('truncated option')
  opts[num]=b[i:i+n];i+=n
 return {'type':(b[0]>>4)&3,'code':b[1],'mid':int.from_bytes(b[2:4],'big'),'token':b[4:4+k],'options':opts,'payload':b[i+1:] if i<len(b) else b''}
class Client:
 def __init__(self,host='127.0.0.1',port=5683):
  self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);self.sock.connect((host,port));self.mid=secrets.randbelow(65536)
 def close(self):self.sock.close()
 def get(self,path,typ=0,options=(),token=None):
  token=token or secrets.token_bytes(2);self.mid=(self.mid+1)&65535;packet=encode(self.mid,token,path,typ,options)
  for attempt in range(4 if typ==0 else 1):
   self.sock.send(packet);deadline=time.monotonic()+2*(2**attempt)
   while time.monotonic()<deadline:
    self.sock.settimeout(max(.01,deadline-time.monotonic()))
    try:r=decode(self.sock.recv(4096))
    except socket.timeout:break
    if r['token']!=token:continue
    if typ==0 and r['type']==2 and r['mid']!=self.mid:continue
    print('RX',r['mid'],'type=',r['type'],'bytes=',len(r['payload']),flush=True)
    return r
   print('timeout/retry',attempt+1,flush=True)
  raise TimeoutError('No matching response')
 def firmware(self):
  out=bytearray();num=0;token=secrets.token_bytes(2);szx=4
  while True:
   r=self.get('/firmware',options=[(23,uint((num<<4)|szx))],token=token)
   if r['code']!=69:raise ValueError('CoAP response '+str(r['code']))
   value=int.from_bytes(r['options'][23],'big');got=value>>4;szx=value&7
   if got*(1<<(szx+4))!=len(out):raise ValueError('block offset mismatch')
   out+=r['payload']
   if not value&8:break
   num=got+1
  if len(out)!=2048:raise ValueError('Incomplete payload')
  print('complete=',len(out),'sha256=',hashlib.sha256(out).hexdigest());return bytes(out)

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['con','non','poll','observe','block']);p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',default=5683,type=int);p.add_argument('--seconds',default=60,type=int);a=p.parse_args();c=Client(a.host,a.port)
 try:
  if a.mode=='block':c.firmware();return
  if a.mode in ('con','non'):print(c.get('/sensor/temp',typ=0 if a.mode=='con' else 1)['payload'].decode());return
  end=time.monotonic()+a.seconds
  if a.mode=='poll':
   while time.monotonic()<end:print(c.get('/sensor/temp')['payload'].decode());time.sleep(2)
  else:
   token=secrets.token_bytes(2);print(c.get('/sensor/temp',options=[(6,b'')],token=token)['payload'].decode())
   while time.monotonic()<end:
    c.sock.settimeout(max(.01,end-time.monotonic()))
    try:r=decode(c.sock.recv(4096))
    except socket.timeout:break
    if r['token']==token:print('NOTIFY MID',r['mid'],'OBS',int.from_bytes(r['options'].get(6,b''),'big'),r['payload'].decode(),flush=True)
   c.get('/sensor/temp',options=[(6,b'\x01')],token=token)
 finally:c.close()
if __name__=='__main__':main()
