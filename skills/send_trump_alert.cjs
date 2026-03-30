const { sendWhatsAppMessage } = require('/Users/vbalaraman/OpenSpider/tools/whatsapp_relay.js');

const msg = '🚨 TRUMP TRUTH SOCIAL POST — March 30, 2026 (7:41 AM EDT)\n\nExact verbatim post:\n\n"The United States of America is in serious discussions with A NEW, AND MORE REASONABLE, REGIME to end our Military Operations in Iran. Great progress has been made but, if for any reason a deal is not shortly reached, which it probably will be, and if the Hormuz Strait is not immediately \'Open for Business,\' we will conclude our lovely \'stay\' in Iran by blowing up and completely obliterating all of their Electric Generating Plants, Oil Wells and Kharg Island (and possibly all desalinization plants!), which we have purposefully not yet \'touched.\'"\n\n— Donald J. Trump, Truth Social';

async function send() {
  const targets = [
    '14156249639@s.whatsapp.net',
    '16507965072@s.whatsapp.net',
    '120363423852747118@g.us'
  ];
  for (const target of targets) {
    try {
      await sendWhatsAppMessage(target, msg);
      console.log('SUCCESS: Sent to ' + target);
    } catch(e) {
      console.log('ERROR sending to ' + target + ': ' + e.message);
    }
  }
}
send();
