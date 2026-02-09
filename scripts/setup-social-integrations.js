#!/usr/bin/env node
/**
 * Setup multiple social media integrations for all brands
 * Creates LinkedIn, X (Twitter), Instagram, Facebook accounts for:
 * - caire (AppCaire main brand)
 * - eirtech.ai (Ireland/EU market)
 * - bjorbevers (Personal/founder brand)
 */

const db = require('../lib/database');

// Social media integrations for all brands
const socialIntegrations = [
  // ========================================
  // CAIRE (AppCaire - Main Product Brand)
  // ========================================
  {
    id: 'int-social-linkedin-caire',
    type: 'social',
    platform: 'linkedin',
    name: 'LinkedIn - Caire',
    config: JSON.stringify({
      brand: 'caire',
      page_url: 'https://linkedin.com/company/caire',
      purpose: 'B2B marketing, thought leadership, product updates',
      managed_by: 'agent-vision',
      post_frequency: '3x per week'
    })
  },
  {
    id: 'int-social-x-caire',
    type: 'social',
    platform: 'twitter',
    name: 'X (Twitter) - @caire_se',
    config: JSON.stringify({
      brand: 'caire',
      handle: '@caire_se',
      purpose: 'Product announcements, customer support, industry news',
      managed_by: 'agent-quill',
      post_frequency: '5x per week'
    })
  },
  {
    id: 'int-social-instagram-caire',
    type: 'social',
    platform: 'instagram',
    name: 'Instagram - @caire.se',
    config: JSON.stringify({
      brand: 'caire',
      handle: '@caire.se',
      purpose: 'Visual storytelling, customer success stories, behind-the-scenes',
      managed_by: 'agent-wanda',
      post_frequency: '3x per week'
    })
  },
  {
    id: 'int-social-facebook-caire',
    type: 'social',
    platform: 'facebook',
    name: 'Facebook Page - Caire',
    config: JSON.stringify({
      brand: 'caire',
      page_url: 'https://facebook.com/caire.se',
      purpose: 'Community engagement, events, customer testimonials',
      managed_by: 'agent-quill',
      post_frequency: '2x per week'
    })
  },

  // ========================================
  // EIRTECH.AI (Ireland/EU Market)
  // ========================================
  {
    id: 'int-social-linkedin-eirtech',
    type: 'social',
    platform: 'linkedin',
    name: 'LinkedIn - Eirtech.ai',
    config: JSON.stringify({
      brand: 'eirtech.ai',
      page_url: 'https://linkedin.com/company/eirtech-ai',
      purpose: 'EU market B2B, GDPR compliance messaging, partnerships',
      managed_by: 'agent-vision',
      post_frequency: '3x per week'
    })
  },
  {
    id: 'int-social-x-eirtech',
    type: 'social',
    platform: 'twitter',
    name: 'X (Twitter) - @eirtech_ai',
    config: JSON.stringify({
      brand: 'eirtech.ai',
      handle: '@eirtech_ai',
      purpose: 'EU tech community, AI insights, product updates',
      managed_by: 'agent-quill',
      post_frequency: '4x per week'
    })
  },
  {
    id: 'int-social-instagram-eirtech',
    type: 'social',
    platform: 'instagram',
    name: 'Instagram - @eirtech.ai',
    config: JSON.stringify({
      brand: 'eirtech.ai',
      handle: '@eirtech.ai',
      purpose: 'EU customer stories, Dublin office culture, tech insights',
      managed_by: 'agent-wanda',
      post_frequency: '2x per week'
    })
  },

  // ========================================
  // BJORBEVERS (Personal/Founder Brand)
  // ========================================
  {
    id: 'int-social-linkedin-bjorn',
    type: 'social',
    platform: 'linkedin',
    name: 'LinkedIn - Bjorn Evers (Personal)',
    config: JSON.stringify({
      brand: 'bjorbevers',
      profile_url: 'https://linkedin.com/in/bjornevers',
      purpose: 'Thought leadership, founder journey, AI insights, hiring',
      managed_by: 'agent-vision',
      post_frequency: '5x per week',
      notes: 'Personal voice, authentic stories, industry commentary'
    })
  },
  {
    id: 'int-social-x-bjorn',
    type: 'social',
    platform: 'twitter',
    name: 'X (Twitter) - @bjornevers',
    config: JSON.stringify({
      brand: 'bjorbevers',
      handle: '@bjornevers',
      purpose: 'Founder insights, tech commentary, product building, AI/startup thoughts',
      managed_by: 'agent-quill',
      post_frequency: 'Daily',
      notes: 'Casual tone, threads, engagement with AI community'
    })
  },
  {
    id: 'int-social-instagram-bjorn',
    type: 'social',
    platform: 'instagram',
    name: 'Instagram - @bjornevers',
    config: JSON.stringify({
      brand: 'bjorbevers',
      handle: '@bjornevers',
      purpose: 'Personal life, work-life balance, travel, product screenshots',
      managed_by: 'agent-wanda',
      post_frequency: '2-3x per week',
      notes: 'Authentic, behind-the-scenes, less corporate'
    })
  }
];

console.log('📱 Setting up social media integrations for all brands...\n');

let created = 0;
let updated = 0;

for (const integration of socialIntegrations) {
  try {
    const existing = db.getIntegration(integration.id);

    if (existing) {
      console.log(`  ⚠️  ${integration.name} already exists, skipping...`);
      updated++;
    } else {
      db.createIntegration({
        id: integration.id,
        type: integration.type,
        platform: integration.platform,
        name: integration.name,
        is_active: 0,
        credentials: null,
        config: integration.config
      });
      console.log(`  ✅ Created: ${integration.name}`);
      created++;
    }
  } catch (error) {
    console.error(`  ❌ Error with ${integration.name}: ${error.message}`);
  }
}

console.log(`\n✅ Setup complete!`);
console.log(`   Created: ${created} integrations`);
console.log(`   Skipped: ${updated} (already exist)`);

console.log(`\n📊 Summary by Brand:`);
console.log(`   Caire:       4 platforms (LinkedIn, X, Instagram, Facebook)`);
console.log(`   Eirtech.ai:  3 platforms (LinkedIn, X, Instagram)`);
console.log(`   Bjorbevers:  3 platforms (LinkedIn, X, Instagram)`);
console.log(`   Total:       10 social media accounts`);

console.log(`\nNext steps:`);
console.log(`1. Open http://localhost:3030 (dashboard)`);
console.log(`2. Configure each social account with API tokens/credentials (via DB or API until Settings UI is added)`);
console.log(`3. See platform docs for obtaining API access:`);
console.log(`   - LinkedIn: https://www.linkedin.com/developers/`);
console.log(`   - X (Twitter): https://developer.x.com/`);
console.log(`   - Instagram: https://developers.facebook.com/products/instagram/`);
console.log(`   - Facebook: https://developers.facebook.com/`);
