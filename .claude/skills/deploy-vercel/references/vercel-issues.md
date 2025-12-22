# Vercel Deployment Issues Reference

## Common Issues and Solutions

### Frontend (Next.js)

#### Build Timeout

**Symptom**: Build exceeds maximum time limit

**Solutions**:
```json
// vercel.json
{
  "buildCommand": "next build",
  "framework": "nextjs",
  "regions": ["iad1"]  // Use closer region
}
```

#### Environment Variables Not Loading

**Symptom**: `process.env.NEXT_PUBLIC_*` is undefined

**Solution**:
```bash
# Add with --prod flag
vercel env add NEXT_PUBLIC_API_URL production
# Verify: vercel env ls
```

#### Static Page Generation Fails

**Symptom**: Error during `npm run build`

**Solutions**:
1. Check for server-only code in client components
2. Use dynamic imports: `const Component = dynamic(() => import('./Component'))`
3. Add `export const dynamic = 'force-dynamic'` to route

### Backend (FastAPI)

#### Worker Timeout

**Symptom**: Request times out after 10 seconds

**Solutions**:
1. Break long tasks into background jobs
2. Use async operations efficiently
3. Implement webhook pattern for long operations

#### Cold Start Issues

**Symptom**: First request is slow

**Solutions**:
- Use `vercel --prod` for warm instances
- Keep dependencies minimal
- Use connection pooling

#### Database Connection Errors

**Symptom**: "Connection refused" or timeout

**Solutions**:
```python
# Use connection pooling with SSL
DATABASE_URL = f"{base_url}?sslmode=require&pool_size=1"

# Or use Neon's serverless driver
import psycopg_pool
pool = psycopg_pool.ConnectionPool(conninfo=DATABASE_URL)
```

### General

#### Deployment Succeeds but 404 on Access

**Symptom**: Vercel shows deployed but URL returns 404

**Solutions**:
1. Check vercel.json routes configuration
2. Verify entry point file exists
3. Check build output for file structure

#### Environment Variables Visible in Logs

**Symptom**: Secrets showing in Vercel logs

**Solution**: Never log `process.env`. Use masked values in logs.

#### Domains Not Configuring

**Symptom**: Custom domain fails to add

**Solutions**:
1. Verify DNS A record points to Vercel
2. Wait up to 24 hours for DNS propagation
3. Check domain verification in Vercel dashboard

## Health Check Commands

```bash
# Check deployment status
vercel ls

# View deployment logs
vercel logs <deployment-url>

# Inspect specific deployment
vercel inspect <deployment-url>

# List environment variables
vercel env ls
```

## Production Best Practices

1. **Always use `--prod` flag for production deployments**
2. **Set environment variables before deploying** (not after)
3. **Test in preview environment first**: `vercel` (without --prod)
4. **Monitor Vercel dashboard for errors** after deployment
5. **Keep vercel.json in version control**
6. **Use project settings for team-wide configurations**
