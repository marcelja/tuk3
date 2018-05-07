var express = require('express');
var app = express();

app.get('/', function (req, res) {
   res.send('Hello World');
})

app.use(express.static('map'));

app.use('/jquery', express.static(__dirname + '/node_modules/jquery/dist/'));

var server = app.listen(8081, function () {
   var host = server.address().address
   var port = server.address().port
   
   console.log("App listening at http://%s:%s", host, port)
})
