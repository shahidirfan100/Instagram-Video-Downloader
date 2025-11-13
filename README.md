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

The **Instagram Video Downloader** is a powerful Apify actor designed to download videos from Instagram with comprehensive metadata extraction. Whether you need to download single videos, multiple posts, reels, or entire profiles, this actor provides reliable extraction with direct download links for easy access.

### ✨ Key Features

- **🎥 Universal Instagram Support**: Download videos from posts, reels, IGTV, and stories
- **📊 Rich Metadata**: Extract comprehensive video information including titles, descriptions, and engagement metrics
- **🔗 Direct Download Links**: Generate API URLs for instant video access
- **📈 Batch Processing**: Handle multiple URLs simultaneously for efficient bulk downloads
- **🛡️ Error Handling**: Robust retry mechanisms and fallback options for maximum reliability
- **⚡ High Performance**: Optimized for speed with concurrent processing capabilities
- **🔒 Privacy Focused**: Secure handling of content with proper access controls
- **📱 Cross-Platform**: Works with all Instagram content types and formats

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
| `cookies` | `string` | - | Instagram cookies for accessing private content |
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
  "urls": "https://www.instagram.com/p/C3v8HnK8JdL/",
  "cookies": "sessionid=your_session_id_here; csrftoken=your_csrf_token_here"
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

## ⚙️ Advanced Configuration

### Quality Options

- **`best`**: Highest available quality (default)
- **`worst`**: Lowest available quality
- **`1080p`**, **`720p`**, **`480p`**: Specific resolutions

### Download Modes

- **`video`**: Download video files (default)
- **`audio`**: Extract audio track only

### Proxy Configuration

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

**❌ "Video not found" error**
- Verify the Instagram URL is correct and public
- Check if the content requires authentication
- Ensure the video hasn't been deleted

**❌ "Download failed" error**
- Try different quality settings
- Check your internet connection
- Verify Apify platform status

**❌ "Private content" error**
- Provide valid Instagram cookies
- Ensure you have access to the content
- Check account permissions

**❌ "Rate limit exceeded" error**
- Reduce concurrent downloads
- Add delays between requests
- Upgrade your Apify plan

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

## 📊 Performance Tips

- **Batch Processing**: Process multiple URLs together for better efficiency
- **Quality Selection**: Choose appropriate quality to balance speed and file size
- **Concurrent Limits**: Respect rate limits to avoid temporary blocks
- **Error Handling**: Implement retry logic for failed downloads
- **Storage Planning**: Monitor key-value store usage for large downloads

## 🔒 Privacy & Security

- All downloads are processed securely within Apify's infrastructure
- No Instagram credentials are stored permanently
- Content is accessible only through your Apify account
- GDPR and privacy regulations compliant
- Secure API endpoints with authentication

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
