# Deploying Docs to Cloudflare Pages

This guide explains how to deploy the Cross-Inertia documentation to Cloudflare Pages.

## Prerequisites

- Cloudflare account (free tier works fine)
- GitHub repository access

## Method 1: Cloudflare Dashboard (Recommended)

### 1. Connect Repository

1. Go to [Cloudflare Pages](https://dash.cloudflare.com/)
2. Click **"Create a project"**
3. Select **"Connect to Git"**
4. Authorize Cloudflare to access your GitHub
5. Select the `patrick91/cross-inertia` repository

### 2. Configure Build

Set these build settings:

| Setting | Value |
|---------|-------|
| **Project name** | `cross-inertia-docs` |
| **Production branch** | `main` |
| **Framework preset** | `Astro` |
| **Build command** | `npm run build` |
| **Build output directory** | `dist` |
| **Root directory** | `docs` ⚠️ |

⚠️ **Important**: Set "Root directory" to `docs` since the documentation is in a subdirectory.

### 3. Environment Variables

No environment variables needed for basic deployment.

### 4. Deploy

Click **"Save and Deploy"**

Cloudflare will:
1. Clone your repository
2. Run `npm install` in the `docs` directory
3. Run `npm run build`
4. Deploy the `dist` folder
5. Give you a URL like: `https://cross-inertia-docs.pages.dev`

### 5. Custom Domain (Optional)

After first deployment:

1. Go to your project → **"Custom domains"**
2. Click **"Set up a custom domain"**
3. Enter your domain (e.g., `docs.yourdomain.com`)
4. Follow DNS instructions
5. Cloudflare will provision SSL automatically

## Method 2: Wrangler CLI

### 1. Install Wrangler

```bash
npm install -g wrangler
# or
bun install -g wrangler
```

### 2. Login

```bash
wrangler login
```

### 3. Build Locally

```bash
cd docs
npm install
npm run build
```

### 4. Deploy

```bash
npx wrangler pages deploy dist --project-name=cross-inertia-docs
```

### 5. Subsequent Deploys

```bash
npm run build && npx wrangler pages deploy dist
```

## Automatic Deployments

Cloudflare Pages automatically deploys:

- **Production**: Every push to `main` branch
- **Preview**: Every pull request gets a preview URL

### Preview Deployments

Each PR gets a unique URL like:
```
https://abc123.cross-inertia-docs.pages.dev
```

Perfect for reviewing documentation changes!

## Build Configuration

The build uses these settings from `package.json`:

```json
{
  "scripts": {
    "build": "astro build"
  }
}
```

Astro automatically:
- Generates static HTML/CSS/JS
- Optimizes images
- Creates search index
- Outputs to `dist/` directory

## Troubleshooting

### Build Fails: "Cannot find module"

**Solution**: Make sure "Root directory" is set to `docs` in Cloudflare settings.

### Build Fails: "npm ERR!"

**Solution**: Clear build cache in Cloudflare Pages settings.

### 404 on Custom Domain

**Solution**: Check DNS propagation. Can take up to 24 hours.

### Slow Build Times

**Solution**: Cloudflare Pages caches `node_modules`. First build is slow (~2 min), subsequent builds are fast (~30s).

## Performance Tips

1. **Cloudflare CDN**: Your docs are served from 300+ locations worldwide
2. **Automatic SSL**: HTTPS enabled by default
3. **Caching**: Static assets cached aggressively
4. **HTTP/3**: Enabled automatically

## Monitoring

View deployment status:
1. Cloudflare Dashboard → Pages → Your Project
2. See build logs, analytics, and errors
3. Monitor page views and bandwidth

## Custom Redirects (Optional)

Create `docs/public/_redirects`:

```
/guides/old-page /guides/new-page 301
/api /reference 302
```

## Headers (Optional)

Create `docs/public/_headers`:

```
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: no-referrer-when-downgrade
```

## Next Steps

After deployment:

1. ✅ Test the live site
2. ✅ Set up custom domain
3. ✅ Add deployment badge to README
4. ✅ Share the docs URL!

---

**Need help?** Check [Cloudflare Pages docs](https://developers.cloudflare.com/pages/) or [Astro deployment guide](https://docs.astro.build/en/guides/deploy/cloudflare/).
