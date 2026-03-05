const fs = require('fs');
const path = require('path');

const filePath = path.join(__dirname, '..', 'src', 'agents', 'WorkerAgent.ts');
let content = fs.readFileSync(filePath, 'utf8');

// The target: after the else block that starts the non-keyword recipient handling
// We need to add a raw JID check before the phone number check

const oldCode = `} else {
                                     // See if it has digits, treat as phone number
                                     const rawNumber = r.replace(/\\D/g, '');
                                     if (rawNumber.length > 5 && /^\\+?\\d+$/.test(r.replace(/\\s/g, ''))) {
                                         targetJids.push(\`\${rawNumber}@s.whatsapp.net\`);`;

const newCode = `} else if (r.trim().endsWith('@g.us') || r.trim().endsWith('@s.whatsapp.net')) {
                                     // Raw JID passthrough — support direct group/DM JIDs
                                     targetJids.push(r.trim());
                                 } else {
                                     // See if it has digits, treat as phone number
                                     const rawNumber = r.replace(/\\D/g, '');
                                     if (rawNumber.length > 5 && /^\\+?\\d+$/.test(r.replace(/\\s/g, ''))) {
                                         targetJids.push(\`\${rawNumber}@s.whatsapp.net\`);`;

if (content.includes('// Raw JID passthrough')) {
  console.log('ALREADY PATCHED — raw JID passthrough code already exists.');
  process.exit(0);
}

// Let me do a more precise search and replace
const lines = content.split('\n');
let patchApplied = false;

for (let i = 0; i < lines.length; i++) {
  // Find the line with '// See if it has digits, treat as phone number'
  if (lines[i].includes('// See if it has digits, treat as phone number')) {
    // The line before this should be the '} else {' line
    // We need to insert our raw JID check before this else block
    // Replace the '} else {' on the previous line with our new code
    const prevLine = lines[i - 1];
    if (prevLine.trim() === '} else {') {
      // Get the indentation
      const indent = prevLine.match(/^(\s*)/)[1];
      // Replace the } else { with } else if (raw JID check) { ... } else {
      lines[i - 1] = indent + `} else if (r.trim().endsWith('@g.us') || r.trim().endsWith('@s.whatsapp.net')) {`;
      // Insert the raw JID handler lines and the new else block
      const insertLines = [
        indent + `    // Raw JID passthrough — support direct group/DM JIDs`,
        indent + `    targetJids.push(r.trim());`,
        indent + `} else {`,
      ];
      lines.splice(i, 0, ...insertLines);
      patchApplied = true;
      console.log(`Patch applied at line ${i} (inserted 3 lines before '// See if it has digits')`);
      break;
    }
  }
}

if (patchApplied) {
  fs.writeFileSync(filePath, lines.join('\n'), 'utf8');
  console.log('WorkerAgent.ts patched successfully.');
  
  // Verify the patch
  const patched = fs.readFileSync(filePath, 'utf8');
  const patchedLines = patched.split('\n');
  for (let i = 370; i < 410 && i < patchedLines.length; i++) {
    console.log(`${i+1}: ${patchedLines[i]}`);
  }
} else {
  console.log('ERROR: Could not find the target code to patch.');
  // Print surrounding lines for debugging
  for (let i = 370; i < 400 && i < lines.length; i++) {
    console.log(`${i+1}: ${lines[i]}`);
  }
}
