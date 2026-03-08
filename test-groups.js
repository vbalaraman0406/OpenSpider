"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const whatsapp_1 = require("./src/whatsapp");
async function test() {
    console.log("Starting whatsapp...");
    await (0, whatsapp_1.startWhatsApp)();
    setTimeout(async () => {
        const groups = await (0, whatsapp_1.getParticipatingGroups)();
        console.log("Groups retrieved:", groups);
        process.exit(0);
    }, 5000);
}
test();
//# sourceMappingURL=test-groups.js.map