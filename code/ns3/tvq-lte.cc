#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/lte-module.h"
#include "ns3/mobility-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/netanim-module.h"
using namespace ns3;
int main(int argc,char**argv){
 uint32_t users=1;double distance=30,duration=6;std::string prefix="tvq-lte";
 CommandLine cmd(__FILE__);cmd.AddValue("users","UE count",users);cmd.AddValue("distance","UE distance m",distance);cmd.AddValue("duration","Seconds",duration);cmd.AddValue("prefix","Output prefix",prefix);cmd.Parse(argc,argv);
 NS_ABORT_MSG_IF(users<1||users>20||distance<1||duration<2,"Invalid parameters");
 auto epc=CreateObject<PointToPointEpcHelper>();auto lte=CreateObject<LteHelper>();lte->SetEpcHelper(epc);
 NodeContainer enb,ue,remote;enb.Create(1);ue.Create(users);remote.Create(1);InternetStackHelper internet;internet.Install(remote);internet.Install(ue);
 PointToPointHelper p2p;p2p.SetDeviceAttribute("DataRate",StringValue("1Gbps"));p2p.SetChannelAttribute("Delay",StringValue("5ms"));
 auto dev=p2p.Install(epc->GetPgwNode(),remote.Get(0));Ipv4AddressHelper address;address.SetBase("1.0.0.0","255.255.255.0");auto back=address.Assign(dev);
 Ipv4StaticRoutingHelper routing;routing.GetStaticRouting(remote.Get(0)->GetObject<Ipv4>())->AddNetworkRouteTo(Ipv4Address("7.0.0.0"),Ipv4Mask("255.0.0.0"),1);
 MobilityHelper mob;mob.SetMobilityModel("ns3::ConstantPositionMobilityModel");mob.Install(enb);mob.Install(ue);
 enb.Get(0)->GetObject<MobilityModel>()->SetPosition(Vector(0,0,0));
 for(uint32_t i=0;i<users;i++)ue.Get(i)->GetObject<MobilityModel>()->SetPosition(Vector(distance,5.0*i,0));
 auto enbDev=lte->InstallEnbDevice(enb),ueDev=lte->InstallUeDevice(ue);auto ip=epc->AssignUeIpv4Address(ueDev);
 for(uint32_t i=0;i<users;i++){
  auto ipv4=ue.Get(i)->GetObject<Ipv4>();int32_t iface=ipv4->GetInterfaceForDevice(ueDev.Get(i));routing.GetStaticRouting(ipv4)->SetDefaultRoute(epc->GetUeDefaultGatewayAddress(),iface);
  lte->Attach(ueDev.Get(i),enbDev.Get(0));uint16_t port=9000+i;
  UdpServerHelper sink(port);auto receiver=sink.Install(ue.Get(i));receiver.Start(Seconds(.2));receiver.Stop(Seconds(duration));
  UdpClientHelper source(ip.GetAddress(i),port);source.SetAttribute("Interval",TimeValue(MilliSeconds(20)));source.SetAttribute("PacketSize",UintegerValue(256));source.SetAttribute("MaxPackets",UintegerValue(100000));auto sender=source.Install(remote.Get(0));sender.Start(Seconds(1));sender.Stop(Seconds(duration-.5));
 }
 FlowMonitorHelper flow;auto mon=flow.InstallAll();AnimationInterface anim(prefix+"-anim.xml");anim.SetConstantPosition(remote.Get(0),-50,20);
 Simulator::Stop(Seconds(duration));Simulator::Run();mon->CheckForLostPackets();mon->SerializeToXmlFile(prefix+"-flow.xml",true,true);Simulator::Destroy();return 0;
}
