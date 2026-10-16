import argparse,csv,xml.etree.ElementTree as E

def seconds(s):
 units={'ns':1e-9,'us':1e-6,'ms':1e-3,'s':1}
 for u in ('ns','us','ms','s'):
  if s.endswith(u):return float(s[:-len(u)])*units[u]
 raise ValueError('unknown time '+s)
def rows(file):
 r=E.parse(file).getroot();addresses={x.attrib['flowId']:x.attrib for x in r.findall('./Ipv4FlowClassifier/Flow')}
 out=[]
 for x in r.findall('./FlowStats/Flow'):
  a=x.attrib;tx=int(a['txPackets']);rx=int(a['rxPackets']);duration=seconds(a['timeLastRxPacket'])-seconds(a['timeFirstTxPacket']) if rx else 0
  out.append({'flowId':a['flowId'],'source':addresses.get(a['flowId'],{}).get('sourceAddress','?'),'destination':addresses.get(a['flowId'],{}).get('destinationAddress','?'),'txPackets':tx,'rxPackets':rx,'txBytes':a['txBytes'],'rxBytes':a['rxBytes'],'loss_pct':round(100*(tx-rx)/tx,3) if tx else 0,'mean_delay_ms':round(1000*seconds(a['delaySum'])/rx,3) if rx else '', 'throughput_kbps':round(int(a['rxBytes'])*8/duration/1000,3) if duration>0 else ''})
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('xml');a=p.parse_args();r=rows(a.xml)
 if not r:raise SystemExit('No IPv4 flows: check UDP apps/routes/duration')
 import sys
 w=csv.DictWriter(sys.stdout,fieldnames=r[0].keys());w.writeheader();w.writerows(r)
