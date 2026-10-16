// Minimal RFC7252 lab server + Observe / Block2. No dependencies.
const dgram=require('node:dgram'),crypto=require('node:crypto');
const socket=dgram.createSocket('udp4'),observers=new Map();let nextId=100,serial=0;
const firmware=Buffer.from('TVQ-IOT-'.repeat(256)); // 2048 bytes; deterministic
function nib(n){if(n<13)return [n,Buffer.alloc(0)];if(n<269)return [13,Buffer.from([n-13])];const b=Buffer.alloc(2);b.writeUInt16BE(n-269);return [14,b];}
function encode(type,code,id,token,options=[],payload=Buffer.alloc(0)){
 const h=Buffer.from([0x40|(type<<4)|token.length,code,id>>8,id&255]);let last=0,parts=[h,token];
 for(const [n,v]of options.sort((a,b)=>a[0]-b[0])){const[d,de]=nib(n-last),[l,le]=nib(v.length);parts.push(Buffer.from([(d<<4)|l]),de,le,v);last=n;}
 if(payload.length)parts.push(Buffer.from([255]),payload);return Buffer.concat(parts);
}
function uint(n){if(n===0)return Buffer.alloc(0);const a=[];while(n){a.unshift(n&255);n>>>=8;}return Buffer.from(a);}
function parse(b){if(b.length<4||b[0]>>6!==1)throw Error('header');const tkl=b[0]&15;if(tkl>8||b.length<4+tkl)throw Error('token');let i=4+tkl,n=0,opts=[];
 function ext(x){if(x<13)return x;if(x===13){if(i>=b.length)throw Error('option');return 13+b[i++];}if(x===14){if(i+2>b.length)throw Error('option');const v=b.readUInt16BE(i);i+=2;return v+269;}throw Error('reserved');}
 while(i<b.length&&b[i]!==255){const x=b[i++],delta=ext(x>>4),len=ext(x&15);n+=delta;if(i+len>b.length)throw Error('truncated');opts.push([n,b.subarray(i,i+len)]);i+=len;}
 return {type:(b[0]>>4)&3,code:b[1],id:b.readUInt16BE(2),token:b.subarray(4,4+tkl),opts};
}
function value(b){let n=0;for(const v of b)n=n*256+v;return n;}
const cache=new Map();
socket.on('message',(b,r)=>{try{const q=parse(b);if(q.code!==1)return;const key=r.address+':'+r.port+':'+q.id;
 if(cache.has(key)){socket.send(cache.get(key).packet,r.port,r.address);return;}
 const uri=q.opts.filter(x=>x[0]===11).map(x=>x[1].toString()).join('/');let payload,opts=[];
 if(uri==='sensor/temp'){
  payload=Buffer.from(JSON.stringify({temp:25+(serial%10)/10,simulated:true}));const ob=q.opts.find(x=>x[0]===6),ok=r.address+':'+r.port+':'+q.token.toString('hex');
  if(ob&&value(ob[1])===0){if(observers.size>=32&&!observers.has(ok))return;observers.set(ok,{...r,token:q.token,at:Date.now()});opts.push([6,uint(serial)]);}
  if(ob&&value(ob[1])===1)observers.delete(ok);
 }else if(uri==='firmware'){
  let num=0,szx=4;const blk=q.opts.find(x=>x[0]===23);if(blk){const v=value(blk[1]);num=v>>4;szx=Math.min(v&7,6);}
  const size=1<<(szx+4),begin=num*size;if(begin>=firmware.length){socket.send(encode(q.type===0?2:1,130,q.id,q.token),r.port,r.address);return;}
  payload=firmware.subarray(begin,begin+size);const more=begin+size<firmware.length;opts.push([23,uint((num<<4)|(more?8:0)|szx)],[28,uint(firmware.length)]);
 }else{socket.send(encode(q.type===0?2:1,132,q.id,q.token),r.port,r.address);return;}
 const packet=encode(q.type===0?2:1,69,q.type===0?q.id:(nextId++&65535),q.token,opts,payload);
 cache.set(key,{packet,at:Date.now()});socket.send(packet,r.port,r.address);
 }catch(e){console.error('Drop:',e.message);}});
setInterval(()=>{serial=(serial+1)&0xffffff;const now=Date.now();for(const [k,o]of observers){if(now-o.at>65000){observers.delete(k);continue;}const payload=Buffer.from(JSON.stringify({temp:25+(serial%10)/10,simulated:true}));socket.send(encode(1,69,nextId++&65535,o.token,[[6,uint(serial)]],payload),o.port,o.address);}for(const [k,x]of cache)if(now-x.at>60000)cache.delete(k);},5000).unref();
const HOST=process.env.COAP_HOST||'127.0.0.1',PORT=Number(process.env.COAP_PORT||5683);
socket.bind(PORT,HOST,()=>console.log(`TVQ CoAP ${HOST}:${PORT}; /sensor/temp /firmware; sha256=${crypto.createHash('sha256').update(firmware).digest('hex')}`));
module.exports={parse,encode};
