import unittest,subprocess,sys,pathlib,importlib.util,json,time,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('coap',ROOT/'code/client.py');coap=importlib.util.module_from_spec(spec);spec.loader.exec_module(coap)
class Integration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.server=subprocess.Popen(['node',str(ROOT/'code/server.cjs')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  line=cls.server.stdout.readline()
  if 'CoAP' not in line:raise RuntimeError('Server not started: '+cls.server.stderr.read())
 @classmethod
 def tearDownClass(cls):cls.server.terminate();cls.server.communicate(timeout=3)
 def test_post_non_and_get_stored_value(self):
  c=coap.Client()
  try:
   r=c.get('/sensor/temp',typ=1,code=2,payload=b'temp=30.5');self.assertEqual(r['type'],1);self.assertEqual(r['code'],68)
   r=c.get('/sensor/temp');self.assertEqual(json.loads(r['payload'])['temp'],30.5)
  finally:c.close()
 def test_post_con_and_deduplicate(self):
  c=coap.Client()
  try:
   token=b'PQ';r=c.get('/sensor/temp',code=2,payload=b'temp=28.2',token=token);self.assertEqual(r['type'],2);self.assertEqual(r['code'],68)
   packet=coap.encode(c.mid,token,'/sensor/temp',code=2,payload=b'temp=28.2');c.sock.send(packet);x=coap.decode(c.sock.recv(4096));self.assertEqual(x,r)
  finally:c.close()
 def test_reject_bad_post(self):
  c=coap.Client()
  try:self.assertEqual(c.get('/sensor/temp',code=2,payload=b'not-a-temperature')['code'],128)
  finally:c.close()
 def test_get_non(self):
  c=coap.Client()
  try:self.assertEqual(c.get('/sensor/temp',typ=1)['type'],1)
  finally:c.close()
 def test_block2_2048(self):
  c=coap.Client()
  try:self.assertEqual(c.firmware(),b'TVQ-IOT-'*256)
  finally:c.close()
 def test_observe(self):
  c=coap.Client();token=b'OB'
  try:
   first=c.get('/sensor/temp',options=[(6,b'')],token=token);self.assertIn(6,first['options']);c.sock.settimeout(6)
   r=coap.decode(c.sock.recv(4096));self.assertEqual(r['token'],token);self.assertIn(6,r['options']);c.get('/sensor/temp',options=[(6,b'\x01')],token=token)
  finally:c.close()
 def test_retry_when_response_dropped(self):
  proxy=subprocess.Popen([sys.executable,str(ROOT/'code/loss_proxy.py')],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
  self.assertIn('Proxy',proxy.stdout.readline());c=coap.Client(port=5684)
  try:self.assertEqual(c.get('/sensor/temp',code=2,payload=b'temp=31.5')['code'],68)
  finally:c.close();proxy.terminate();proxy.communicate(timeout=3)
if __name__=='__main__':unittest.main(verbosity=2)
