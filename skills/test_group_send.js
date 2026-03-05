const path = require('path');
const { getSocket } = require(path.join('/Users/vbalaraman/OpenSpider', 'dist', 'whatsapp.js'));

async function testGroupSend() {
  const sock = getSocket();
  if (!sock) {
    console.log('ERROR: No socket available - the socket is only available inside the main running process');
    return;
  }
  console.log('Socket found, attempting group send...');
  
  const groupJid = '120363364529832104@g.us';
  try {
    const result = await sock.sendMessage(groupJid, { text: 'Test group message from diagnostic script' });
    console.log('SUCCESS:', JSON.stringify(result, null, 2));
  } catch (err) {
    console.log('ERROR:', err.message);
    console.log('ERROR STACK:', err.stack);
  }
}

testGroupSend();
