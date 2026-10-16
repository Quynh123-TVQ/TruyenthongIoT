const http=require('node:http'),fs=require('node:fs'),path=require('node:path');
const {SerialPort}=require('serialport'),{WebSocketServer}=require('ws');
let serial=null,buffer='';
const send=(res,n,x)=>{res.writeHead(n,{'Content-Type':'application/json'});res.end(JSON.stringify(x));};
const srv=http.createServer(async(req,res)=>{
 if(req.method==='GET'&&req.url==='/'){res.writeHead(200,{'Content-Type':'text/html; charset=utf-8'});return res.end(fs.readFileSync(path.join(__dirname,'index.html')));}
 if(req.method==='GET'&&req.url==='/ports'){try{return send(res,200,await SerialPort.list());}catch(e){return send(res,503,{error:e.message});}}
 if(req.method!=='POST')return send(res,404,{error:'not found'});
 let data='';try{for await(const part of req){data+=part;if(data.length>1024)return send(res,413,{error:'too large'});}const b=JSON.parse(data||'{}');
 if(req.url==='/connect'){
  if(serial?.isOpen)return send(res,409,{error:'already connected'});
  if(typeof b.port!=='string'||!b.port)return send(res,400,{error:'select port'});
  serial=new SerialPort({path:b.port,baudRate:9600,autoOpen:false});
  serial.on('error',e=>broadcast({error:e.message}));serial.on('close',()=>broadcast({connected:false}));
  serial.on('data',chunk=>{buffer+=chunk;while(buffer.includes('\n')){let i=buffer.indexOf('\n'),line=buffer.slice(0,i).trim();buffer=buffer.slice(i+1);try{broadcast(JSON.parse(line));}catch{broadcast({line});}}if(buffer.length>4096)buffer='';});
  return serial.open(e=>send(res,e?400:200,e?{error:e.message}:{connected:true}));
 }
 if(req.url==='/led'){if(!serial?.isOpen)return send(res,409,{error:'not connected'});if(!['ON','OFF'].includes(b.cmd))return send(res,400,{error:'invalid command'});serial.write(b.cmd+'\n');return send(res,200,{sent:b.cmd});}
 if(req.url==='/disconnect'){if(serial?.isOpen)return serial.close(e=>send(res,e?400:200,e?{error:e.message}:{connected:false}));return send(res,200,{connected:false});}
 return send(res,404,{error:'not found'});
 }catch(e){send(res,400,{error:e.message});}
});
const ws=new WebSocketServer({server:srv});function broadcast(x){for(const c of ws.clients)if(c.readyState===1)c.send(JSON.stringify(x));}
srv.listen(3085,'127.0.0.1',()=>console.log('TVQ http://127.0.0.1:3085'));
