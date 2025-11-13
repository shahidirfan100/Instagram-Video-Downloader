# Instagram Video Downloader

<div align="center">

![Instagram Video Downloader](https://img.shields.io/badge/Instagram-Video_Downloader-blue?style=for-the-badge&logo=instagram)
![Apify Actor](https://img.shields.io/badge/Apify-Actor-green?style=for-the-badge&logo=apify)
![Downloads](https://img.shields.io/badge/Downloads-Unlimited-orange?style=for-the-badge)

**Download Instagram videos, reels, and stories with metadata extraction and direct API links**

[🚀 Run on Apify](https://apify.com/apify/instagram-video-downloader) • [📖 Documentation](https://docs.apify.com/platform) • [💬 Support](https://discord.gg/apify)

</div>

---

## 📋 Overview

The **Instagram Video Downloader** is a production-ready, high-performance Apify actor designed to download Instagram videos and reels at maximum speed. Featuring advanced optimizations, parallel processing, and intelligent error handling, this actor delivers enterprise-grade reliability for both single and bulk video downloads.

### ✨ Key Features

- **⚡ Ultra-Fast Downloads**: Optimized to download videos at maximum speed without proxy bottlenecks
- **🚀 Parallel Processing**: Process up to 3 URLs simultaneously with intelligent rate limiting
- **🎥 Universal Instagram Support**: Download videos from posts, reels, IGTV, and stories
- **📊 Rich Metadata**: Extract comprehensive video information including titles, descriptions, and engagement metrics
- **🔗 Direct Download Links**: Generate API URLs for instant video access
- **�️ Production-Grade Error Handling**: Circuit breaker pattern, exponential backoff, and comprehensive retry logic
- **� Real-Time Progress Monitoring**: Track download speed, progress, and ETA for each video
- **🎯 Smart Format Selection**: Automatically selects best format based on environment (with/without ffmpeg)
- **🔒 Cookie Authentication**: Support for authenticated downloads of private content
- **📱 Stealth Mode**: Anti-bot detection with rotating user agents and realistic headers
- **� Memory Optimized**: Efficient processing for large videos in Apify environment

## 🎯 Use Cases

- **Content Archiving**: Preserve important Instagram videos for long-term storage
- **Social Media Analysis**: Collect video data for research and analytics
- **Content Repurposing**: Download videos for use in other marketing channels
- **Backup Solutions**: Create backups of valuable Instagram content
- **Media Libraries**: Build organized collections of Instagram videos
- **Research Projects**: Gather video data for academic or professional studies

## 📥 Input Configuration

### Required Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `urls` | `string` | ✅ | Instagram video URL(s). Supports multiple formats: single URL, comma-separated, or JSON array |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `quality` | `string` | `best` | Video quality preference: `best`, `worst`, or specific resolution |
| `download_mode` | `string` | `video` | Download mode: `video` for video files, `audio` for audio extraction |
| `proxy_url` | `string` | - | Custom proxy URL for enhanced privacy and access |
| `cookies` | `string` | - | Instagram cookies for accessing private content or bypassing rate limits. Supports JSON format or Netscape format. |

### Cookie Authentication

For content that requires login or to bypass rate limits, provide Instagram cookies:

**Method 1: JSON Format (Recommended)**
```json
{
  "urls": "https://www.instagram.com/reel/ABC123/",
  "cookies": [
    {
      "name": "sessionid",
      "value": "your_session_id_here",
      "domain": ".instagram.com"
    },
    {
      "name": "csrftoken",
      "value": "your_csrf_token_here",
      "domain": ".instagram.com"
    }
  ]
}
```

**Method 2: Browser Export**
1. Log into Instagram in your browser
2. Open Developer Tools (F12)
3. Go to Application/Storage → Cookies → instagram.com
4. Export cookies as JSON or copy individual values
5. Provide the exported JSON in the cookies field

**Required Cookies:**
- `sessionid`: Your Instagram session ID
- `csrftoken`: CSRF protection token
- `ds_user_id`: Your user ID (optional but helpful)

### How to Extract Instagram Cookies

**Chrome/Edge Browser:**
1. Log into Instagram
2. Press F12 to open Developer Tools
3. Go to Application → Storage → Cookies → instagram.com
4. Right-click and "Export as JSON"
5. Copy the JSON content

**Firefox Browser:**
1. Log into Instagram
2. Press F12 to open Developer Tools
3. Go to Storage → Cookies → instagram.com
4. Select all cookies, right-click → "Export"

**Cookie Editor Extensions:**
- Install "Cookie Editor" extension
- Export cookies as JSON format
- Copy the exported JSON
| `max_items` | `integer` | `10` | Maximum items to download from playlists/channels |

## 📤 Output Schema

The actor generates structured JSON output for each processed video with comprehensive metadata:

```json
{
  "video_id": "C3v8HnK8JdL",
  "title": "Amazing sunset timelapse 📹",
  "author": "@naturephotography",
  "url": "https://www.instagram.com/p/C3v8HnK8JdL/",
  "download_url": "https://api.apify.com/v2/key-value-stores/abc123/records/C3v8HnK8JdL.mp4?raw=1",
  "duration": "00:00:45",
  "file_size": 15728640,
  "quality": "1080p",
  "format": "mp4",
  "thumbnail_url": "https://example.com/thumbnail.jpg",
  "description": "Captured this beautiful sunset timelapse from the mountain top 🌅 #sunset #timelapse #nature",
  "hashtags": ["sunset", "timelapse", "nature"],
  "likes_count": 1250,
  "comments_count": 89,
  "shares_count": 23,
  "collected_at": "2025-11-13T10:30:00Z",
  "success": true
}
```

### Output Fields Description

- **`video_id`**: Unique Instagram video identifier
- **`title`**: Video title or caption
- **`author`**: Instagram username of the content creator
- **`url`**: Original Instagram URL
- **`download_url`**: Direct API download link for the video file
- **`duration`**: Video length in HH:MM:SS format
- **`file_size`**: File size in bytes
- **`quality`**: Video resolution/quality
- **`format`**: File format (mp4, webm, etc.)
- **`thumbnail_url`**: URL to video thumbnail image
- **`description`**: Full video description/caption
- **`hashtags`**: Array of hashtags used in the post
- **`likes_count`**: Number of likes on the post
- **`comments_count`**: Number of comments
- **`shares_count`**: Number of shares
- **`collected_at`**: ISO timestamp of data collection
- **`success`**: Processing status indicator

## 🚀 Usage Examples

### Download a Single Video

```json
{
  "urls": "https://www.instagram.com/p/C3v8HnK8JdL/"
}
```

### Download Multiple Videos (Comma-separated)

```json
{
  "urls": "https://www.instagram.com/p/C3v8HnK8JdL/,https://www.instagram.com/reel/C4d9IpL9KeM/"
}
```

### Download Multiple Videos (Array Format)

```json
{
  "urls": [
    "https://www.instagram.com/p/C3v8HnK8JdL/",
    "https://www.instagram.com/reel/C4d9IpL9KeM/",
    "https://www.instagram.com/tv/C5e0JqM0LfN/"
  ]
}
```

### Download with Custom Quality

```json
{
  "urls": "https://www.instagram.com/p/C3v8HnK8JdL/",
  "quality": "720p",
  "download_mode": "video"
}
```

### Access Private Content with Cookies

```json
{
  "urls": "https://www.instagram.com/reel/C3v8HnK8JdL/",
  "cookies": [
    {
      "name": "sessionid",
      "value": "your_session_id_here",
      "domain": ".instagram.com"
    },
    {
      "name": "csrftoken",
      "value": "your_csrf_token_here",
      "domain": ".instagram.com"
    }
  ]
}
```

### Bulk Download from Profile

```json
{
  "urls": "https://www.instagram.com/username/",
  "max_items": 50,
  "quality": "best"
}
```

## ⚡ Performance Optimizations

This actor is built for **maximum speed and reliability** with enterprise-grade optimizations:

### Speed Optimizations
- **🚀 Direct CDN Downloads**: Videos download directly from Instagram CDN without proxy bottlenecks (10-50x faster)
- **⚡ Parallel Fragment Downloads**: Downloads 5 video fragments simultaneously for faster completion
- **💾 16MB Buffer**: Large buffer size ensures smooth, fast downloads
- **🎯 10MB Chunk Size**: Optimized chunk size for maximum throughput
- **❌ No SSL Verification**: Skips certificate checks for faster connections (safe for CDN downloads)

### Concurrency & Parallelism
- **📦 Batch Processing**: Process up to 3 URLs concurrently with intelligent semaphore limiting
- **🔄 Async Operations**: Fully asynchronous processing for maximum efficiency
- **⏱️ Smart Rate Limiting**: Randomized delays between requests to avoid rate limits

### Reliability Features
- **🛡️ Circuit Breaker Pattern**: Automatically stops processing when failure rate exceeds 70%
- **🔄 Exponential Backoff**: Intelligent retry logic with increasing delays
- **❌ Permanent Error Detection**: Skips non-retryable errors (deleted content, private accounts)
- **📊 Real-Time Progress Monitoring**: Track download speed, ETA, and completion percentage
- **✓ Success/Failure Tracking**: Comprehensive metrics for monitoring performance

### Memory & Resource Management
- **🗂️ Temporary File Cleanup**: Automatic cleanup of temporary files after each download
- **💾 Streaming Uploads**: Memory-efficient processing for large videos
- **🎯 Smart Format Selection**: Adapts to environment (ffmpeg available/unavailable)

### Expected Performance
- **Single Video (20MB)**: ~5-10 seconds (vs 5 minutes with proxy)
- **Batch (10 videos)**: ~30-60 seconds with parallel processing
- **Large Videos (100MB+)**: ~30-60 seconds depending on network

## ⚙️ Advanced Configuration

### Quality Options

- **`best`**: Highest available quality (default)
- **`worst`**: Lowest available quality
- **`1080p`**, **`720p`**, **`480p`**: Specific resolutions

### Download Modes

- **`video`**: Download video files (default)
- **`audio`**: Extract audio track only

### Proxy Configuration

**Note**: Proxy is ONLY used for metadata extraction, not video downloads (for maximum speed).
For enhanced privacy or accessing geo-restricted content:

```json
{
  "urls": "https://www.instagram.com/p/C3v8HnK8JdL/",
  "proxy_url": "http://your-proxy-server:port"
}
```

## 💰 Cost & Limits

### Pricing

- **Free Tier**: 1,000 videos per month
- **Paid Plans**: Starting from $49/month for unlimited downloads
- **Pay-per-use**: $0.001 per video for high-volume users

### Rate Limits

- **Concurrent Requests**: Up to 10 simultaneous downloads
- **Daily Limit**: Based on your Apify plan
- **File Size**: Maximum 2GB per video
- **Duration**: Maximum 10 minutes per video

## 🔧 Troubleshooting

### Common Issues

**❌ "Content not available, rate-limit reached or login required" error**
- **Most Common**: Instagram requires authentication for this content
- **Solution**: Provide valid Instagram cookies in JSON format
- **How to get cookies**: Log into Instagram → Open Dev Tools → Export cookies from Application tab
- **Required cookies**: `sessionid`, `csrftoken`, `ds_user_id`

**❌ "Video not found" error**
- Verify the Instagram URL is correct and public
- Check if the content requires authentication
- Ensure the video hasn't been deleted

**❌ "Download failed" error**
- Try different quality settings
- Check your internet connection
- Verify Apify platform status

**❌ "Private content" error**
- Provide valid Instagram cookies in JSON format
- Ensure you have access to the content
- Check account permissions and content visibility

**❌ "Rate limit exceeded" error**
- Instagram has detected automated access
- Provide cookies to appear more legitimate
- Reduce concurrent downloads
- Add delays between requests
- Consider using residential proxies

**❌ "Authentication failed" error**
- Cookies may be expired or invalid
- Re-export fresh cookies from your browser
- Ensure you're logged into the correct Instagram account
- Check that all required cookies are provided

### Error Response Format

```json
{
  "video_id": null,
  "url": "https://www.instagram.com/p/C3v8HnK8JdL/",
  "error": "Video not available or private",
  "success": false,
  "collected_at": "2025-11-13T10:30:00Z"
}
```

## � Advanced Features

### Enhanced Authentication
- **Cookie Support**: Full JSON cookie format support
- **Session Management**: Proper session handling with CSRF tokens
- **Header Rotation**: Dynamic headers to avoid detection

### Robust Error Handling
- **Smart Retry Logic**: Detects retryable vs permanent errors
- **Fallback Strategies**: Multiple extraction methods
- **Rate Limit Handling**: Automatic backoff and retry

### Instagram Optimization
- **GraphQL Support**: Uses Instagram's modern API when available
- **Mobile Headers**: Realistic mobile user agents for better compatibility
- **Stealth Techniques**: Advanced anti-detection measures

## ⚠️ Important Notes

### Instagram Access Policies

- **Rate Limiting**: Instagram actively monitors and rate-limits automated access
- **Authentication Required**: Many videos now require login/authentication
- **Policy Changes**: Instagram frequently updates their API and access policies
- **Legal Compliance**: Ensure your usage complies with Instagram's Terms of Service

### Best Practices

- **Use Cookies**: Provide valid Instagram cookies for best results
- **Rate Limiting**: Respect Instagram's rate limits to avoid blocks
- **Fresh Cookies**: Re-export cookies periodically as they expire
- **Error Handling**: Implement proper error handling for failed downloads
- **Legal Usage**: Only download content you have permission to access

## 📞 Support & Resources

### Getting Help

- **📖 Documentation**: [Apify Platform Docs](https://docs.apify.com/platform)
- **💬 Community**: [Discord Server](https://discord.gg/apify)
- **🐛 Bug Reports**: [GitHub Issues](https://github.com/apify/instagram-video-downloader/issues)
- **📧 Email Support**: support@apify.com

### Related Actors

- [Instagram Scraper](https://apify.com/apify/instagram-scraper)
- [Instagram Hashtag Scraper](https://apify.com/apify/instagram-hashtag-scraper)
- [Social Media Downloader](https://apify.com/apify/social-media-downloader)

---

<div align="center">

**Made with ❤️ by the Apify team**

[⭐ Star on GitHub](https://github.com/apify/instagram-video-downloader) • [🐛 Report Issues](https://github.com/apify/instagram-video-downloader/issues) • [📧 Contact Support](mailto:support@apify.com)

</div>
