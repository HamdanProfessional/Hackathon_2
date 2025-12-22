# Production Database Migration Guide

## Critical Issues Identified

### 1. Database Schema Mismatch (Production)
**Error:** `column "role" is of type message_role but expression is of type character varying`

**Root Cause:** The production database (Vercel/Neon) has a PostgreSQL ENUM type `message_role` for the `messages.role` column, but the SQLAlchemy model expects `VARCHAR(20)`.

### 2. Gemini API Rate Limit Exceeded
**Error:** `429 - Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 20`

**Root Cause:** You've hit the free tier limit for Gemini API (20 requests/day for `gemini-2.5-flash`).

---

## Solution 1: Fix Database Schema (Immediate Priority)

### Step 1: Connect to Production Database

You have two options to run the migration on production:

#### Option A: Run Migration via Vercel CLI (Recommended)

```bash
# 1. Install Vercel CLI if not already installed
npm install -g vercel

# 2. Login to Vercel
vercel login

# 3. Link to your project
cd backend
vercel link

# 4. Get production environment variables
vercel env pull .env.production

# 5. Run migration on production database
# Use the DATABASE_URL from .env.production
alembic upgrade head
```

#### Option B: Run Migration Directly on Neon Database

```bash
# 1. Get your production DATABASE_URL from Vercel dashboard
# Vercel Dashboard -> Your Project -> Settings -> Environment Variables -> DATABASE_URL

# 2. Set the production DATABASE_URL temporarily
$env:DATABASE_URL = "your-production-database-url-here"

# 3. Run the migration
cd backend
alembic upgrade head

# 4. Verify the migration
alembic current
```

### Step 2: Verify Migration Success

After running the migration, you should see:

```
[INFO] Detected message_role ENUM type - converting to VARCHAR(20)
[INFO] Converted messages.role from ENUM to VARCHAR(20)
[INFO] Added CHECK constraint: check_role_values
[INFO] Dropped message_role ENUM type
[SUCCESS] Migration complete: messages.role is now VARCHAR(20) with CHECK constraint
```

### Step 3: Test the Chat Functionality

1. Go to your deployed frontend: https://frontend-hamdanprofessionals-projects.vercel.app/chat
2. Try sending a message
3. Verify that the chat works without 500 errors

---

## Solution 2: Fix AI API Rate Limit

You have three options:

### Option A: Switch to OpenAI API (Recommended for Production)

```bash
# 1. Get an OpenAI API key from https://platform.openai.com/api-keys

# 2. Add to Vercel environment variables
vercel env add OPENAI_API_KEY

# When prompted:
# - Enter your OpenAI API key
# - Select: Production, Preview, Development (all environments)

# 3. Redeploy backend
cd backend
vercel --prod

# Your config.py already auto-detects OpenAI and uses gpt-4o-mini
```

**Benefits:**
- More reliable uptime
- Higher rate limits (pay-as-you-go)
- Better performance
- Production-ready

**Cost:** ~$0.10-0.30 per 1000 messages (gpt-4o-mini is very affordable)

### Option B: Upgrade Gemini API Tier

```bash
# 1. Go to https://ai.google.dev/gemini-api/docs/pricing
# 2. Enable billing for your Google Cloud project
# 3. Get a new API key with higher limits
# 4. Update GEMINI_API_KEY in Vercel

vercel env add GEMINI_API_KEY
# Enter new key with higher limits
```

**Free Tier Limits:**
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

**Paid Tier:** Higher limits available

### Option C: Wait for Quota Reset (Temporary Fix)

The free tier quota resets daily. According to the error:
```
Please retry in 14.235425955s.
```

However, this will happen again after 20 requests. **Not recommended for production.**

---

## Deployment Checklist

- [ ] **Step 1:** Run database migration on production (Option A or B above)
- [ ] **Step 2:** Verify migration success by checking logs
- [ ] **Step 3:** Choose AI API solution (OpenAI recommended)
- [ ] **Step 4:** Add API key to Vercel environment variables
- [ ] **Step 5:** Redeploy backend to Vercel
- [ ] **Step 6:** Test chat functionality on production frontend
- [ ] **Step 7:** Monitor error logs for any remaining issues

---

## Vercel Deployment Commands

```bash
# Deploy backend with new environment variables
cd backend
vercel --prod

# Check deployment logs
vercel logs <deployment-url>

# View current environment variables
vercel env ls
```

---

## Rollback Plan (If Needed)

If something goes wrong with the migration:

```bash
# 1. Connect to production database
$env:DATABASE_URL = "your-production-database-url-here"

# 2. Rollback one migration
cd backend
alembic downgrade -1

# 3. Check current version
alembic current
```

**Note:** The migration is designed to be idempotent and safe. Rollback should only be needed in extreme cases.

---

## Expected Timeline

1. **Database Migration:** 5 minutes
2. **AI API Setup:** 10 minutes (OpenAI) or 5 minutes (Gemini upgrade)
3. **Deployment & Testing:** 10 minutes

**Total:** ~25 minutes to fully resolve both issues

---

## Support Resources

- **Vercel CLI Docs:** https://vercel.com/docs/cli
- **Neon Database Console:** https://console.neon.tech/
- **OpenAI API Keys:** https://platform.openai.com/api-keys
- **Gemini API Pricing:** https://ai.google.dev/gemini-api/docs/pricing
- **Alembic Migrations:** https://alembic.sqlalchemy.org/

---

## Questions?

If you encounter any issues during deployment:
1. Check Vercel deployment logs: `vercel logs`
2. Check database migration status: `alembic current`
3. Verify environment variables: `vercel env ls`
4. Test locally first: Run the same migration on local database to ensure it works
