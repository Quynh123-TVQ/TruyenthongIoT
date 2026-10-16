"""Requires paho-mqtt + amqtt (test-only). Starts a broker only on loopback."""
from pathlib import Path
import subprocess,sys,time,threading,queue,os
import paho.mqtt.client as mqtt
R=Path(__file__).resolve().parents[1];broker=None;device=None;sub=None
try:
 broker=subprocess.Popen([sys.executable,str(R/'tests/mqtt_test_broker.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 assert 'READY' in broker.stdout.readline(),'broker did not start'
 device=subprocess.Popen([sys.executable,str(R/'code/mqtt_pc/lab.py'),'device','--port','18884'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 time.sleep(.3)
 sub=mqtt.Client(mqtt.CallbackAPIVersion.VERSION2);messages=queue.Queue();ready=threading.Event()
 def connected(c,u,f,r,p):c.subscribe('tvq/lab12/#',1);ready.set()
 sub.on_connect=connected;sub.on_message=lambda c,u,m:messages.put((m.topic,m.payload,m.retain));sub.connect('127.0.0.1',18884,15);sub.loop_start();assert ready.wait(3)
 def wait(topic,payload,retained=None):
  deadline=time.monotonic()+4
  while time.monotonic()<deadline:
   try:x=messages.get(timeout=.3)
   except queue.Empty:continue
   if x[0]==topic and x[1]==payload and (retained is None or x[2]==retained):return
  raise AssertionError((topic,payload,retained))
 wait('tvq/lab12/state',b'OFF',True)
 print('PASS new subscriber received retained OFF')
 subprocess.run([sys.executable,str(R/'code/mqtt_pc/lab.py'),'pub','--port','18884','--message','ON'],check=True,timeout=8)
 wait('tvq/lab12/state',b'ON');print('PASS cmd ON -> state ON')
 # Abrupt process termination causes a transport close without MQTT DISCONNECT.
 device.kill();device.communicate(timeout=3);wait('tvq/lab12/availability',b'OFFLINE');print('PASS abrupt disconnect -> LWT OFFLINE')
 subprocess.run([sys.executable,str(R/'code/mqtt_pc/lab.py'),'load','--port','18884','--count','3','--rate','10'],check=True,timeout=8);print('PASS bounded publisher completed')
finally:
 if sub:sub.disconnect();sub.loop_stop()
 if device and device.poll() is None:device.terminate();device.communicate(timeout=3)
 if broker and broker.poll() is None:broker.terminate();out,err=broker.communicate(timeout=5)
