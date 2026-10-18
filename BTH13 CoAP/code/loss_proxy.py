"""One lab client. Drop the FIRST server response, then forward normally."""
import select,socket
front=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);front.bind(('127.0.0.1',5684));back=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);back.connect(('127.0.0.1',5683));peer=None;dropped=False
print('Proxy 127.0.0.1:5684 -> 127.0.0.1:5683; drop first response',flush=True)
try:
 while True:
  for s in select.select([front,back],[],[],1)[0]:
   if s is front:
    data,peer=front.recvfrom(4096);back.send(data)
   else:
    data=back.recv(4096)
    if not dropped:dropped=True;print('DROPPED first response',flush=True)
    elif peer:front.sendto(data,peer)
except KeyboardInterrupt:pass
finally:front.close();back.close()
