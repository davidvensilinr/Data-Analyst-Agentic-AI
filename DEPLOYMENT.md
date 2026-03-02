# Deployment Guide

This guide covers deploying the Autonomous Data Analyst to production.

## Quick Deploy to Vercel

Vercel is the recommended hosting platform for Next.js applications.

### Prerequisites
- Vercel account (free at https://vercel.com)
- GitHub repository (optional but recommended)

### Option 1: Deploy from GitHub

1. Push your code to GitHub
2. Go to https://vercel.com/new
3. Import your repository
4. Configure environment variables
5. Click "Deploy"

### Option 2: Deploy from CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Deploy to production
vercel --prod
```

### Environment Variables

Set these in your Vercel project settings:

```
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api
NEXT_PUBLIC_MOCK_MODE=false
API_TOKEN=your_token_here
```

## Docker Deployment

### Build Docker Image

```bash
# Build the image
docker build -t autonomous-data-analyst .

# Run the container
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:3001/api autonomous-data-analyst
```

### Docker Compose

```bash
# Start all services
docker-compose up

# Stop services
docker-compose down

# View logs
docker-compose logs -f frontend
```

Services:
- `frontend`: Next.js app on port 3000
- `backend`: Mock backend on port 3001

## Other Platforms

### AWS Amplify

1. Connect your GitHub repo to Amplify
2. Set environment variables
3. Deploy on commit

### Heroku

1. Create a Heroku app: `heroku create your-app-name`
2. Set environment variables: `heroku config:set NEXT_PUBLIC_API_URL=...`
3. Deploy: `git push heroku main`

### Google Cloud Run

1. Create a `gcp-deploy.sh` script
2. Build container
3. Deploy to Cloud Run

### Traditional VPS (AWS EC2, DigitalOcean, etc.)

```bash
# SSH into server
ssh user@your-server.com

# Clone repository
git clone https://github.com/your-repo/autonomous-data-analyst.git
cd autonomous-data-analyst

# Install dependencies
npm install

# Build
npm run build

# Start with PM2
npm install -g pm2
pm2 start npm --name "ada" -- start
pm2 save
pm2 startup
```

## Production Checklist

- [ ] Update `NEXT_PUBLIC_API_URL` to production backend
- [ ] Set `NEXT_PUBLIC_MOCK_MODE=false`
- [ ] Enable HTTPS/SSL
- [ ] Set up database backups
- [ ] Configure monitoring and logging
- [ ] Set up email notifications for errors
- [ ] Review security headers in `next.config.js`
- [ ] Test all features in staging environment
- [ ] Set up CI/CD pipeline
- [ ] Configure auto-scaling if needed
- [ ] Set up CDN for static assets
- [ ] Enable analytics tracking

## Performance Optimization

### Build Optimization

```bash
# Analyze bundle size
npm run build

# Use `npm run analyze` if added to package.json
```

### Caching Strategy

```javascript
// next.config.js
module.exports = {
  onDemandEntries: {
    maxInactiveAge: 60 * 1000,
    pagesBufferLength: 5,
  },
}
```

### Database Optimization

- Add indexes to frequently queried columns
- Implement query result caching
- Use connection pooling for database

### Image Optimization

Images are automatically optimized via Next.js Image component. Ensure:
- Use `<Image>` component instead of `<img>`
- Specify width and height
- Use appropriate formats (WebP, AVIF)

## Monitoring & Logging

### Recommended Tools

- **Monitoring**: Datadog, New Relic, Sentry
- **Logging**: CloudWatch, Loggly, Papertrail
- **Error Tracking**: Sentry, Rollbar, Bugsnag
- **APM**: Datadog, New Relic, AWS X-Ray

### Basic Logging Setup

```javascript
// lib/logger.ts
export const logger = {
  info: (msg: string, data?: any) => console.log(`[INFO] ${msg}`, data),
  error: (msg: string, error?: Error) => console.error(`[ERROR] ${msg}`, error),
  warn: (msg: string, data?: any) => console.warn(`[WARN] ${msg}`, data),
};
```

## Scaling Strategy

### Horizontal Scaling
- Stateless frontend (all state in database)
- Load balancer in front of multiple instances
- Shared database with connection pooling

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Upgrade database tier
- Use faster storage (SSD)

### Database Optimization
- Add read replicas
- Implement sharding for large datasets
- Use connection pooling
- Archive old data

## Security Hardening

### Environment Variables
- Never commit secrets
- Rotate credentials regularly
- Use strong API tokens

### Headers
```javascript
// next.config.js
headers: async () => [
  {
    source: '/(.*)',
    headers: [
      {
        key: 'X-Content-Type-Options',
        value: 'nosniff',
      },
      {
        key: 'X-Frame-Options',
        value: 'SAMEORIGIN',
      },
      {
        key: 'X-XSS-Protection',
        value: '1; mode=block',
      },
    ],
  },
]
```

### CORS
- Restrict to known origins only
- Disable in production if not needed

### Rate Limiting
- Implement per-IP rate limiting
- Use API gateway or nginx for global limits

### Database Security
- Use parameterized queries
- Enable encryption at rest
- Regular backups and testing

## Rollback Plan

```bash
# If deployment fails, rollback previous version
vercel --prod --env rollback=true

# Or manually:
git revert <commit-hash>
git push origin main
```

## Maintenance

### Regular Tasks
- Update dependencies: `npm outdated`
- Security patches: `npm audit`
- Monitor error rates
- Review performance metrics
- Test backup restoration

### Upgrade Process
1. Test in staging environment
2. Schedule downtime if needed
3. Backup database
4. Deploy to production
5. Monitor for errors
6. Keep previous version available for rollback

## Support & Troubleshooting

### Common Issues

**Deploy fails with "out of memory"**
- Increase server memory
- Optimize bundle size
- Use tree-shaking

**API requests timing out**
- Increase timeout limits
- Optimize backend queries
- Check network connectivity

**High CPU usage**
- Profile application
- Optimize algorithms
- Use caching
- Scale horizontally

## Environment Variables Reference

```
# Required
NEXT_PUBLIC_API_URL=                    # Backend API URL

# Optional
NEXT_PUBLIC_MOCK_MODE=false             # Use mock data
API_TOKEN=                              # Authentication token
NEXT_PUBLIC_THEME=light                 # UI theme

# Analytics (optional)
NEXT_PUBLIC_GA_ID=                      # Google Analytics

# Error tracking (optional)
SENTRY_DSN=                             # Sentry error tracking
```

---

For local development setup, see `GETTING_STARTED.md`.
For architecture details, see `ARCHITECTURE.md`.
