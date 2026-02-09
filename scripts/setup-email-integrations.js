#!/usr/bin/env node
/**
 * Setup multiple email integrations for OpenClaw lead scraping
 * Creates 9 IMAP email integrations (EMAIL_1 through EMAIL_9)
 */

const db = require('../lib/database');

// Email configuration templates (3 per domain)
const emailIntegrations = [
  // CAIRE.SE (AppCaire main product)
  {
    id: 'int-email-imap-1',
    type: 'email',
    platform: 'imap',
    name: 'Sales @ caire.se',
    config: JSON.stringify({
      email_var: 'EMAIL_1',
      domain: 'caire.se',
      purpose: 'Direct sales inquiries (highest intent)',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'sales@caire.se'
    })
  },
  {
    id: 'int-email-imap-2',
    type: 'email',
    platform: 'imap',
    name: 'Info @ caire.se',
    config: JSON.stringify({
      email_var: 'EMAIL_2',
      domain: 'caire.se',
      purpose: 'General inquiries (mix of leads and support)',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'info@caire.se'
    })
  },
  {
    id: 'int-email-imap-3',
    type: 'email',
    platform: 'imap',
    name: 'Bjorn @ caire.se',
    config: JSON.stringify({
      email_var: 'EMAIL_3',
      domain: 'caire.se',
      purpose: 'Personal inquiries (high-value partnerships)',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'bjorn@caire.se'
    })
  },

  // EIRTECH.AI (Ireland/EU market)
  {
    id: 'int-email-imap-4',
    type: 'email',
    platform: 'imap',
    name: 'Sales @ eirtech.ai',
    config: JSON.stringify({
      email_var: 'EMAIL_4',
      domain: 'eirtech.ai',
      purpose: 'EU market sales inquiries',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'sales@eirtech.ai'
    })
  },
  {
    id: 'int-email-imap-5',
    type: 'email',
    platform: 'imap',
    name: 'Info @ eirtech.ai',
    config: JSON.stringify({
      email_var: 'EMAIL_5',
      domain: 'eirtech.ai',
      purpose: 'EU market general inquiries',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'info@eirtech.ai'
    })
  },
  {
    id: 'int-email-imap-6',
    type: 'email',
    platform: 'imap',
    name: 'Bjorn @ eirtech.ai',
    config: JSON.stringify({
      email_var: 'EMAIL_6',
      domain: 'eirtech.ai',
      purpose: 'EU market personal inquiries',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'bjorn@eirtech.ai'
    })
  },

  // NACKAHEMTJANST.SE (Nacka local market)
  {
    id: 'int-email-imap-7',
    type: 'email',
    platform: 'imap',
    name: 'Sales @ nackahemtjanst.se',
    config: JSON.stringify({
      email_var: 'EMAIL_7',
      domain: 'nackahemtjanst.se',
      purpose: 'Local market sales inquiries',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'sales@nackahemtjanst.se'
    })
  },
  {
    id: 'int-email-imap-8',
    type: 'email',
    platform: 'imap',
    name: 'Info @ nackahemtjanst.se',
    config: JSON.stringify({
      email_var: 'EMAIL_8',
      domain: 'nackahemtjanst.se',
      purpose: 'Local market general inquiries',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'info@nackahemtjanst.se'
    })
  },
  {
    id: 'int-email-imap-9',
    type: 'email',
    platform: 'imap',
    name: 'Bjorn @ nackahemtjanst.se',
    config: JSON.stringify({
      email_var: 'EMAIL_9',
      domain: 'nackahemtjanst.se',
      purpose: 'Local market personal inquiries',
      imap_host: 'imap.gmail.com',
      imap_port: 993,
      default_user: 'bjorn@nackahemtjanst.se'
    })
  }
];

console.log('📧 Setting up email integrations for OpenClaw...\n');

let created = 0;
let updated = 0;

for (const integration of emailIntegrations) {
  try {
    const existing = db.getIntegration(integration.id);

    if (existing) {
      console.log(`  ⚠️  ${integration.name} already exists, skipping...`);
      updated++;
    } else {
      console.log(`  📝 Creating: ${integration.name}...`);
      const params = {
        id: integration.id,
        type: integration.type,
        platform: integration.platform,
        name: integration.name,
        is_active: 0,
        credentials: null,
        config: integration.config
      };
      console.log(`     Params:`, JSON.stringify(params));

      db.createIntegration(params);
      console.log(`  ✅ Created: ${integration.name}`);
      created++;
    }
  } catch (error) {
    console.error(`  ❌ Error with ${integration.name}:`);
    console.error(`     ${error.message}`);
    console.error(`     Stack:`, error.stack);
  }
}

console.log(`\n✅ Setup complete!`);
console.log(`   Created: ${created} integrations`);
console.log(`   Skipped: ${updated} (already exist)`);
console.log(`\nNext steps:`);
console.log(`1. Open http://localhost:3030/settings.html`);
console.log(`2. Configure each email with username and app password`);
console.log(`3. See EMAIL_SETUP_GUIDE.md for Gmail app password setup`);
