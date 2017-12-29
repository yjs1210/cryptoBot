const Tail = require('tail').Tail;
const Deque = require("collections/deque");
const http = require('http');
const port = 80;
const ip = '0.0.0.0';

var deque = new Deque(100);
tail = new Tail("logs/data/arb_20171221.log");
tail.on("line", function(data) {
    if (deque.length > 100) {
        deque.shift();
    }
    deque.push(data);
});

http.createServer(function (req, res) {
    res.writeHead(200, {'Content-Type': 'text/plain'});
    res.end(deque.toArray().reverse().join("\n"));
}).listen(port, ip);

console.log(`server is running on ${ip}:${port}`);

