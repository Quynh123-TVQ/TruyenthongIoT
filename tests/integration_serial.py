"""Linux PTY checks for the real Node Serial bridge; no physical board assumed."""
import json,os,pty,select,subprocess,threading,time,urllib.request,pathlib
from websockets.sync.client import connect
R=pathlib.Path(__file__).resolve().parents[1];master,slave=pty.openpty();port=os.ttyname(slave)
stop=threading.Event();seen=[]
def board():
 buf=b''
 while not stop.is_set():
  if not select.select([master],[],[],.1)[0]:continue
  try:buf+=os.read(master,1024)
  except OSError:return
  while b'\n' in buf:
   line,buf=buf.split(b'\n',1);line=line.strip();seen.append(line)
   os.write(master,b'STATE '+line+b'\n')
thread=threading.Thread(target=board,daemon=True);thread.start()
server=subprocess.Popen(['node','server.cjs'],cwd=R/'code/bluetooth_web',stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
http=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def req(path,data=None):
 r=urllib.request.Request('http://127.0.0.1:3085'+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
 with http.open(r,timeout=3) as response:return response.status,response.read()
try:
 assert 'TVQ' in server.stdout.readline()
 assert 'Trạm Bluetooth' in req('/')[1].decode();print('PASS web HTML served UTF-8')
 with connect('ws://127.0.0.1:3085',proxy=None) as ws:
  assert json.loads(req('/connect',{'port':port})[1])['connected']
  assert json.loads(req('/led',{'cmd':'ON'})[1])['sent']=='ON'
  frame=json.loads(ws.recv(timeout=3));assert frame.get('line')=='STATE ON',frame;assert seen==[b'ON'];print('PASS HTTP -> Serial ON newline -> WebSocket ACK')
  os.write(master,b'{"temp":26.5,"hum":61}\n');frame=json.loads(ws.recv(timeout=3));assert frame['temp']==26.5 and frame['hum']==61;print('PASS Serial JSON -> WebSocket numeric telemetry')
  assert not json.loads(req('/disconnect',{})[1])['connected'];print('PASS disconnect API')
finally:
 stop.set();server.terminate();out,err=server.communicate(timeout=3);os.close(master);os.close(slave)
