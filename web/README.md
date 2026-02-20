# Protocol Lab Website - Deployment Guide

## Overview
Static website for browsing and playing meditation/breathwork protocols. Designed for S3 hosting with CloudFront.

## Structure
```
web/
├── index.html          # Main page
├── protocols-data.js   # Protocol metadata
├── app.js             # Application logic
└── README.md          # This file
```

## S3 Bucket Structure

Upload files to S3 with this structure:

```
your-bucket/
├── index.html
├── protocols-data.js
├── app.js
├── audio/
│   ├── ATTN/
│   │   ├── FSP-01_master.wav
│   │   ├── FSP-02_master.wav
│   │   └── FSP-03_master.wav
│   ├── ARC/
│   │   ├── ARC-1TB_master.wav
│   │   ├── ARC-2_master.wav
│   │   └── ARC-3_master.wav
│   └── ... (all families)
├── docs/
│   ├── ATTN/
│   │   ├── FSP-01.md
│   │   ├── diagrams/
│   │   │   ├── ATTN_phase_timeline.md
│   │   │   ├── ATTN_signal_chain.md
│   │   │   └── ATTN_practice_flow.md
│   │   └── ...
│   └── ... (all families)
└── narration/
    ├── ATTN/
    │   ├── FSP-01_coaching.md
    │   └── ...
    └── ... (all families)
```

## Deployment Steps

### 1. Create S3 Bucket
```bash
aws s3 mb s3://protocol-lab-website --region us-east-1
```

### 2. Enable Static Website Hosting
```bash
aws s3 website s3://protocol-lab-website \
  --index-document index.html \
  --error-document index.html
```

### 3. Set Bucket Policy (Public Read)
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": "s3:GetObject",
    "Resource": "arn:aws:s3:::protocol-lab-website/*"
  }]
}
```

Apply policy:
```bash
aws s3api put-bucket-policy \
  --bucket protocol-lab-website \
  --policy file://bucket-policy.json
```

### 4. Upload Website Files
```bash
# Upload HTML/JS
cd protocol-lab/web
aws s3 cp index.html s3://protocol-lab-website/
aws s3 cp protocols-data.js s3://protocol-lab-website/
aws s3 cp app.js s3://protocol-lab-website/

# Upload audio files
cd ../protocols
for family in ATTN ARC PERF RECON SLEEP CREA SENSE META FLOW BODY SOC PAIN; do
  aws s3 sync $family/renders/ s3://protocol-lab-website/audio/$family/ \
    --exclude "*" --include "*_master.wav"
done

# Upload documentation
for family in ATTN ARC PERF RECON SLEEP CREA SENSE META FLOW BODY SOC PAIN; do
  aws s3 sync ../docs/protocols/ s3://protocol-lab-website/docs/$family/ \
    --exclude "*" --include "$family-*.md"
done

# Upload narration scripts
for family in ATTN ARC PERF RECON SLEEP CREA SENSE META FLOW BODY SOC PAIN; do
  aws s3 sync $family/narration/ s3://protocol-lab-website/narration/$family/ \
    --exclude "*" --include "*_coaching.md"
done
```

### 5. Set CORS Configuration
Create `cors.json`:
```json
{
  "CORSRules": [{
    "AllowedOrigins": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedHeaders": ["*"],
    "MaxAgeSeconds": 3000
  }]
}
```

Apply:
```bash
aws s3api put-bucket-cors \
  --bucket protocol-lab-website \
  --cors-configuration file://cors.json
```

### 6. (Optional) Add CloudFront CDN
```bash
aws cloudfront create-distribution \
  --origin-domain-name protocol-lab-website.s3-website-us-east-1.amazonaws.com \
  --default-root-object index.html
```

## Access Website

**S3 Website URL:**
```
http://protocol-lab-website.s3-website-us-east-1.amazonaws.com
```

**CloudFront URL (if configured):**
```
https://d1234567890.cloudfront.net
```

## Features

### Browse Protocols
- View all 32 protocols organized by 12 families
- Filter by family type
- See protocol duration and goals

### Play Audio
- Stream audio directly in browser
- HTML5 audio player with controls
- No download required

### View Documentation
- Access full protocol documentation
- View protocol family diagrams (phase timeline, signal chain, practice flow)
- View narration scripts with timestamps
- Open in new tab for reference

### Responsive Design
- Works on desktop, tablet, mobile
- Dark theme optimized for focus
- Smooth animations and transitions

## Customization

### Update Protocol Data
Edit `protocols-data.js` to add/modify protocols.

### Change Theme
Edit CSS variables in `index.html` `<style>` section:
```css
--primary-color: #00d4ff;
--background: #1a1a2e;
--card-bg: rgba(15, 52, 96, 0.5);
```

### Modify Audio Paths
Update paths in `app.js` `playProtocol()` function if your S3 structure differs.

## Cost Estimate

**S3 Storage:**
- ~15 GB audio files: $0.35/month
- Minimal HTML/JS: negligible

**S3 Requests:**
- 1000 users/month: ~$0.01

**Data Transfer:**
- 100 GB/month: $9.00

**CloudFront (optional):**
- 100 GB/month: $8.50
- Requests: $0.10

**Total: ~$10-18/month** for moderate usage

## Security Considerations

### Public Access
- Website is publicly accessible
- No authentication required
- Consider adding CloudFront signed URLs for premium content

### Content Protection
- Audio files are publicly accessible
- Consider watermarking audio
- Use CloudFront signed cookies for access control

### HTTPS
- S3 website endpoints don't support HTTPS
- Use CloudFront for HTTPS support
- Required for modern browsers and PWA features

## Maintenance

### Update Content
```bash
# Update single protocol audio
aws s3 cp PERF-03_master.wav s3://protocol-lab-website/audio/PERF/

# Update documentation
aws s3 cp FSP-01.md s3://protocol-lab-website/docs/ATTN/

# Clear CloudFront cache (if using)
aws cloudfront create-invalidation \
  --distribution-id E1234567890 \
  --paths "/*"
```

### Monitor Usage
```bash
# Check S3 metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/S3 \
  --metric-name NumberOfObjects \
  --dimensions Name=BucketName,Value=protocol-lab-website \
  --start-time 2026-01-01T00:00:00Z \
  --end-time 2026-02-01T00:00:00Z \
  --period 86400 \
  --statistics Average
```

## Troubleshooting

### Audio Won't Play
- Check CORS configuration
- Verify audio file exists in S3
- Check browser console for errors
- Ensure WAV format is supported

### 403 Forbidden
- Verify bucket policy allows public read
- Check object ACLs
- Ensure bucket is not blocking public access

### Slow Loading
- Enable CloudFront CDN
- Compress audio files (convert to MP3)
- Enable S3 Transfer Acceleration

## Next Steps

1. **Convert to MP3** - Reduce file sizes by 90%
2. **Add Analytics** - Track usage with CloudWatch or Google Analytics
3. **User Accounts** - Add authentication with Cognito
4. **Progress Tracking** - Store user progress in DynamoDB
5. **Mobile App** - Wrap in Capacitor/React Native
6. **Offline Support** - Add service worker for PWA

## Support

For issues or questions, refer to:
- Protocol documentation in `docs/`
- User guide: `USER_GUIDE.md`
- Quick reference: `QUICK_REFERENCE.md`
