const WebSocket = require('ws');

const ws = new WebSocket('ws://localhost:4001');

ws.on('open', function open() {
    console.log('Connected to backend');
    ws.send(JSON.stringify({ type: 'chat', text: 'Can you find me a good rating contractor to replace my bathroom floor and wall tile and vanity in Vancouver WA 98662?' }));
});

ws.on('message', function message(data) {
    const msg = JSON.parse(data);
    if (msg.type === 'chat_response') {
        console.log('\n\nFINAL RESPONSE FROM AGENT:', msg.data);
        process.exit(0);
    } else if (msg.type === 'agent_flow') {
        process.stdout.write('+');
    } else if (msg.type === 'log') {
        process.stdout.write('.');
    }
});
