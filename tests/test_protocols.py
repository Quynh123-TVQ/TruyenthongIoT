import importlib.util,pathlib,subprocess,unittest,tempfile,time,socket,hashlib,json,sys,os
R=pathlib.Path(__file__).resolve().parents[1]
def module(name,file):
 s=importlib.util.spec_from_file_location(name,R/file);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
coap=module('coap_client','code/coap/client.py');guard=module('guard','code/security/replay_guard.py');flow=module('flow','code/ns3/read_flow.py')
class Security(unittest.TestCase):
 def test_duplicate_tamper_expiry_and_restart(self):
  with tempfile.TemporaryDirectory() as t:
   db=t+'/guard.sqlite';key=b'K'*32;c=guard.sign(dict(device='TVQ',cmd='OPEN',seq=1,time=100),key)
   self.assertEqual(guard.verify(c,key,db,100),(True,'accepted'))
   self.assertEqual(guard.verify(c,key,db,100),(False,'duplicate'))
   c['seq']=2;self.assertEqual(guard.verify(c,key,db,100),(False,'signature'))
   c=guard.sign(dict(device='TVQ',cmd='CLOSE',seq=2,time=100),key)
   self.assertEqual(guard.verify(c,key,db,111),(False,'expired'))
   self.assertEqual(guard.verify(c,key,db,100),(True,'accepted'))
   restarted=module('guard2','code/security/replay_guard.py')
   self.assertEqual(restarted.verify(c,key,db,100),(False,'duplicate'))
 def test_schema(self):
  self.assertFalse(guard.verify({},b'K'*32,':memory:',100)[0])
class Coap(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.p=subprocess.Popen(['node',str(R/'code/coap/server.cjs')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  line=cls.p.stdout.readline()
  if 'CoAP' not in line:raise RuntimeError('server failed: '+cls.p.stderr.read())
 @classmethod
 def tearDownClass(cls):cls.p.terminate();cls.p.communicate(timeout=3)
 def test_con_non(self):
  c=coap.Client()
  try:
   for typ in [0,1]:
    x=c.get('/sensor/temp',typ=typ);self.assertEqual(x['code'],69);self.assertEqual(x['type'],2 if typ==0 else 1);self.assertTrue(json.loads(x['payload'])['simulated'])
  finally:c.close()
 def test_block2_all_2048(self):
  c=coap.Client()
  try:self.assertEqual(c.firmware(),b'TVQ-IOT-'*256)
  finally:c.close()
 def test_observe_and_cancel(self):
  c=coap.Client();token=b'QQ'
  try:
   r=c.get('/sensor/temp',options=[(6,b'')],token=token);self.assertIn(6,r['options']);c.sock.settimeout(6)
   x=coap.decode(c.sock.recv(4096));self.assertEqual(x['token'],token);self.assertIn(6,x['options']);self.assertNotEqual(x['mid'],r['mid'])
   c.get('/sensor/temp',options=[(6,b'\x01')],token=token)
  finally:c.close()
 def test_lost_response_retries(self):
  proxy=subprocess.Popen([sys.executable,str(R/'code/coap/loss_proxy.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);self.assertIn('Proxy',proxy.stdout.readline());c=coap.Client(port=5684)
  try:self.assertEqual(c.get('/sensor/temp')['code'],69)
  finally:c.close();proxy.terminate();proxy.communicate(timeout=3)
class Flow(unittest.TestCase):
 def test_time_units_and_stats(self):
  self.assertAlmostEqual(flow.seconds('+1000000ns'),.001)
  with tempfile.TemporaryDirectory() as t:
   f=pathlib.Path(t)/'f.xml';f.write_text('<FlowMonitor><FlowStats><Flow flowId="1" txPackets="10" rxPackets="8" txBytes="1000" rxBytes="800" delaySum="+8000000ns" timeFirstTxPacket="+1000000000ns" timeLastRxPacket="+2000000000ns"/></FlowStats><Ipv4FlowClassifier><Flow flowId="1" sourceAddress="1.0.0.2" destinationAddress="7.0.0.2"/></Ipv4FlowClassifier></FlowMonitor>')
   row=flow.rows(f)[0];self.assertEqual(row['loss_pct'],20);self.assertEqual(row['mean_delay_ms'],1);self.assertEqual(row['throughput_kbps'],6.4)
if __name__=='__main__':unittest.main(verbosity=2)
