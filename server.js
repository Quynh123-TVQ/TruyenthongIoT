
const coap = require('coap');

const server = coap.createServer();

server.on('request', (req, res) => {
    console.log('Received:', req.payload.toString());

    // Tam thoi khong phan hoi tuong minh
    // res.end('OK');
});

server.listen(() => {
    console.log('CoAP server started');
});
