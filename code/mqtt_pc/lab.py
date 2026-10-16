"""Local broker companion: publish, subscribe, device simulator, bounded load."""
import argparse,json,os,time,threading
import paho.mqtt.client as mqtt
p=argparse.ArgumentParser();p.add_argument('mode',choices=['pub','sub','device','load']);p.add_argument('--host',default='127.0.0.1');p.add_argument('--port',type=int,default=1883);p.add_argument('--topic',default='tvq/lab12/cmd');p.add_argument('--message',default='ON');p.add_argument('--retain',action='store_true');p.add_argument('--count',type=int,default=100);p.add_argument('--rate',type=float,default=5);p.add_argument('--ca');a=p.parse_args()
if not 1<=a.count<=200 or not 0<a.rate<=10:p.error('count 1..200; rate (0,10]')
c=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,client_id='TVQ-PC-'+a.mode);ready=threading.Event();state=False
if os.getenv('MQTT_USER'):c.username_pw_set(os.environ['MQTT_USER'],os.getenv('MQTT_PASS',''))
if a.ca:c.tls_set(ca_certs=a.ca)
if a.mode=='device':c.will_set('tvq/lab12/availability','OFFLINE',qos=1,retain=True)
def on_connect(client,u,f,reason,props):
 if reason.is_failure:print('connect failed',reason);return
 if a.mode=='sub':client.subscribe(a.topic,1)
 if a.mode=='device':
  client.subscribe('tvq/lab12/cmd',1);client.publish('tvq/lab12/availability','ONLINE',retain=True);client.publish('tvq/lab12/state','OFF',retain=True)
 ready.set()
def on_message(client,u,msg):
 global state
 s=msg.payload.decode(errors='replace');print(msg.topic,s,'retain=',msg.retain,flush=True)
 if a.mode=='device' and s in ('ON','OFF','TOGGLE'):
  state=(not state) if s=='TOGGLE' else s=='ON';client.publish('tvq/lab12/state','ON' if state else 'OFF',retain=True)
c.on_connect=on_connect;c.on_message=on_message;c.connect(a.host,a.port,15);c.loop_start()
if not ready.wait(8):raise SystemExit('No CONNACK')
try:
 if a.mode in ('pub','load'):
  for i in range(a.count if a.mode=='load' else 1):
   c.publish(a.topic,a.message,qos=1,retain=a.retain).wait_for_publish(timeout=5)
   if a.mode=='load':time.sleep(1/a.rate)
 else:
  tick=0
  while True:
   if a.mode=='device':c.publish('tvq/lab12/sensor',json.dumps({'temp':25+tick%10/10,'hum':60,'simulated':True}));tick+=1
   time.sleep(5)
except KeyboardInterrupt:pass
finally:
 if a.mode=='device':c.publish('tvq/lab12/availability','OFFLINE',retain=True).wait_for_publish(timeout=3)
 c.disconnect();c.loop_stop()
