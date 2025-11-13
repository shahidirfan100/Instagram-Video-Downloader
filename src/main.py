"""
Instagram Video Downloader
Stack: Python 3.10+ + Apify SDK + yt-dlp
"""

from __future__ import annotations
import asyncio
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from datetime import datetime, UTC

import random
import yt_dlp

# Apify SDK imports - only available in Apify environment
try:
    from apify import Actor  # type: ignore
except ImportError:
    # Fallback for local development
    class Actor:  # type: ignore
        class log:
            @staticmethod
            def info(msg: str) -> None:
                print(f"[INFO] {msg}")

            @staticmethod
            def warning(msg: str) -> None:
                print(f"[WARNING] {msg}")

            @staticmethod
            def error(msg: str) -> None:
                print(f"[ERROR] {msg}")

        @staticmethod
        async def get_input():
            return {}

        @staticmethod
        async def push_data(data):
            print(f"[DATA] {data}")

        @staticmethod
        async def set_value(key, value, **kwargs):
            print(f"[STORE] Set {key}")

        @staticmethod
        async def open_key_value_store():
            return None

        @staticmethod
        async def create_proxy_configuration(**kwargs):
            return None

# Realistic user agents for Instagram
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


def _get_random_user_agent() -> str:
    """Return a random user agent string."""
    return random.choice(USER_AGENTS)


def _get_stealth_headers(url: str = None) -> Dict[str, str]:
    """Generate comprehensive stealth headers for Instagram requests."""
    base_headers = {
        'User-Agent': _get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    if url and 'instagram.com' in url:
        base_headers['Referer'] = 'https://www.instagram.com/'

    return base_headers
try:
    import scrapling
    SCRAPLING_AVAILABLE = True
except Exception:
    scrapling = None
    SCRAPLING_AVAILABLE = False
    Actor.log.info("scrapling not available — proceeding without scrapling utilities.")  # type: ignore

try:
    import ffmpeg
    FFMPEG_AVAILABLE = True
except Exception:
    ffmpeg = None
    FFMPEG_AVAILABLE = False
    Actor.log.info("ffmpeg-python not available — post-processing disabled.")  # type: ignore


# Common extension lookups
VIDEO_FILE_EXTENSIONS = {'.mp4', '.mkv', '.webm', '.mov', '.m4v'}
AUDIO_FILE_EXTENSIONS = {'.mp3', '.m4a', '.aac', '.opus', '.ogg', '.wav', '.flac'}
MEDIA_FILE_EXTENSIONS = VIDEO_FILE_EXTENSIONS | AUDIO_FILE_EXTENSIONS

CONTENT_TYPE_BY_EXTENSION = {
    '.mp4': 'video/mp4',
    '.mkv': 'video/x-matroska',
    '.webm': 'video/webm',
    '.mov': 'video/quicktime',
    '.m4v': 'video/x-m4v',
    '.m4a': 'audio/mp4',
    '.aac': 'audio/aac',
    '.opus': 'audio/ogg',
    '.ogg': 'audio/ogg',
    '.wav': 'audio/wav',
    '.flac': 'audio/flac',
    '.mp3': 'audio/mpeg',
}


# ============================================================ #
#                        CONFIGURATION                         #
# ============================================================ #

# Base yt-dlp options optimized for Instagram
# Base yt-dlp options - will be modified based on ffmpeg availability
BASE_YDL_OPTS = {
    'quiet': True,
    'no_warnings': True,
    'extract_flat': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'no_color': True,
    'retries': 3,
    'fragment_retries': 5,
    # Instagram extractor specific options
    'extractor_args': {
        'instagram': {
            'api_dump': False,
            'sleep_interval': 1,
        }
    },
}

# Add ffmpeg-dependent options only if ffmpeg is available
if FFMPEG_AVAILABLE:
    BASE_YDL_OPTS.update({
        'merge_output_format': 'mp4',
        'format_sort': ['res', 'fps', 'vcodec:h264', 'acodec:m4a', 'ext:mp4:m4a'],
    })
else:
    BASE_YDL_OPTS.update({
        'format_sort': ['res', 'fps', 'ext:mp4:m4a'],
    })

# Quality labels retained for reference (fallback helper uses these)
QUALITY_FORMATS = {
    'best': 'best',
    '720p': 'best[height<=720]',
    '1080p': 'best[height<=1080]',
    'audio_only': 'bestaudio/best',
}


def _build_format_candidates(quality: str | None) -> List[str]:
    """Return ordered yt-dlp format strings with graceful fallbacks."""
    q = (quality or 'best').lower()

    if q in {'audio_only', 'audio'}:
        candidates = ['bestaudio/best', 'best']
    elif q in {'1080p', '1080'}:
        # Use formats that don't require merging if ffmpeg is not available
        if FFMPEG_AVAILABLE:
            candidates = [
                'bestvideo*[height<=1080][fps<=60]+bestaudio/best[height<=1080]',
                'bestvideo*[height<=1080]+bestaudio/best',
                'bestvideo[height<=1440]+bestaudio/best',
                'best',
            ]
        else:
            candidates = [
                'best[height<=1080]',
                'bestvideo[height<=1080]',
                'best',
            ]
    elif q in {'720p', '720'}:
        # Use formats that don't require merging if ffmpeg is not available
        if FFMPEG_AVAILABLE:
            candidates = [
                'bestvideo*[height<=720][fps<=60]+bestaudio/best[height<=720]',
                'bestvideo*[height<=720]+bestaudio/best',
                'bestvideo[height<=1080]+bestaudio/best',
                'best',
            ]
        else:
            candidates = [
                'best[height<=720]',
                'bestvideo[height<=720]',
                'best',
            ]
    else:
        # Use formats that don't require merging if ffmpeg is not available
        if FFMPEG_AVAILABLE:
            candidates = [
                'bestvideo*+bestaudio/best',
                'bestvideo+bestaudio/best',
                'best',
            ]
        else:
            candidates = [
                'best',
                'bestvideo',
                'bestaudio',
            ]

    # Deduplicate while preserving order
    seen: set[str] = set()
    ordered: List[str] = []
    for fmt in candidates:
        if fmt not in seen:
            ordered.append(fmt)
            seen.add(fmt)
    return ordered


def _is_retryable_error(error_msg: str) -> bool:
    """Check if an error is retryable based on Instagram-specific error patterns."""
    retryable_patterns = [
        # Rate limiting
        "rate limit exceeded",
        "too many requests",
        "http error 429",
        "temporarily unavailable",
        # Bot detection
        "sign in to confirm you're not a bot",
        "blocked",
        "bot",
        # Network issues
        "connection reset",
        "timeout",
        "network is unreachable",
        # Instagram specific
        "content not available",
        "video not available",
        "reel not available",
        "private account",
        "account is private",
        # Generic
        "try again later",
        "service unavailable",
    ]
    return any(pattern.lower() in error_msg.lower() for pattern in retryable_patterns)


async def _retry_with_backoff(func, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 30.0):
    """Execute a function with exponential backoff retry logic."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            try:
                error_msg = str(e)
            except Exception:
                error_msg = "Unknown error"
            if attempt == max_retries - 1 or not _is_retryable_error(error_msg):
                raise e

            # Calculate delay with exponential backoff and jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            # Add jitter to avoid thundering herd
            import random
            jitter = random.uniform(0.1, 1.0) * delay * 0.1
            total_delay = delay + jitter

            Actor.log.warning(f"Attempt {attempt + 1} failed: {error_msg[:100]}... Retrying in {total_delay:.1f}s")  # type: ignore
            await asyncio.sleep(total_delay)

    return None


def _clear_directory(directory: str) -> None:
    """Remove files created by previous download attempts in a temp directory."""
    for entry in Path(directory).iterdir():
        try:
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        except Exception:
            continue


def _validate_instagram_url(url: str) -> bool:
    """Validate if URL is a valid Instagram URL that can be processed."""
    if not url or not isinstance(url, str):
        return False

    url = url.strip().lower()

    # Check for basic Instagram domain
    if 'instagram.com' not in url:
        return False

    # Valid Instagram URL patterns
    valid_patterns = [
        '/p/',      # Posts
        '/reel/',   # Reels
        '/tv/',     # IGTV
        '/stories/', # Stories (though may not work for downloads)
    ]

    # Check if URL contains any valid pattern
    return any(pattern in url for pattern in valid_patterns)


def _normalize_instagram_url(url: str) -> str:
    """Normalize Instagram URL to ensure it has proper format."""
    url = url.strip()

    # Ensure https protocol
    if url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    elif not url.startswith('https://'):
        url = f'https://www.instagram.com{url}' if url.startswith('/') else f'https://www.instagram.com/{url}'

    # Ensure www prefix for consistency
    if url.startswith('https://instagram.com'):
        url = url.replace('https://instagram.com', 'https://www.instagram.com', 1)

    return url


def _find_downloaded_media(directory: str) -> Path | None:
    """Locate the most recent media file produced by yt-dlp."""
    candidates = []
    for entry in Path(directory).iterdir():
        if entry.is_file() and entry.suffix.lower() in MEDIA_FILE_EXTENSIONS:
            candidates.append(entry)

    if not candidates:
        return None

    candidates.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return candidates[0]


def _generate_safe_key(video_id: str, extension: str) -> str:
    """
    Generate a safe key for the key-value store.
    
    Args:
        video_id: The video ID
        extension: File extension
        
    Returns:
        Safe key string (max 256 chars, only allowed characters)
    """
    # Use video ID and extension for the key
    key = f"{video_id}.{extension}"
    
    # Ensure it's within length limits (Apify allows up to 256 chars)
    if len(key) > 256:
        # Truncate if necessary (unlikely for video IDs)
        key = key[:256]
        # Make sure we don't cut off in the middle of extension
        if not key.endswith(f".{extension}"):
            key = f"{video_id[:256-len(extension)-1]}.{extension}"
    
    return key


def _guess_content_type(extension: str | None) -> str:
    """Infer content type for storing files in the key-value store."""
    if not extension:
        return 'application/octet-stream'
    ext = extension.lower()
    if not ext.startswith('.'):
        ext = f'.{ext}'
    return CONTENT_TYPE_BY_EXTENSION.get(ext, 'application/octet-stream')

def get_ydl_opts(download_mode: str, quality: str, proxy_url: str = None, max_items: int = 0, cookies: str = None, url: str = None) -> Dict[str, Any]:
    """
    Build yt-dlp options based on input parameters.

    Args:
        download_mode: 'videos' or 'metadata_only'
        quality: Quality preference
        proxy_url: Optional proxy URL
        max_items: Maximum items to extract from playlists
        cookies: Optional cookies string
        url: The URL being processed (for referer header)

    Returns:
        yt-dlp options dictionary
    """
    opts = BASE_YDL_OPTS.copy()

        # Add referer header for Instagram URLs
    if url and 'instagram.com' in url:
        opts['http_headers'] = _get_stealth_headers(url)

    # For metadata extraction we never request specific formats to avoid validation issues.
    # Actual download format selection is handled by dedicated helpers.
    opts.pop('format', None)

    if download_mode == 'videos':
        opts['outtmpl'] = '%(id)s.%(ext)s'

    # Handle playlists/channels
    if max_items > 0:
        opts['playlistend'] = max_items
    opts['noplaylist'] = False  # Allow playlist processing

    # Only add proxy if explicitly provided
    if proxy_url:
        opts['proxy'] = proxy_url

    # Only add cookies if explicitly provided (handled by calling function)

    return opts


def _get_fallback_opts(original_opts: Dict[str, Any], cookies: str = None, temp_dir: str = None) -> Dict[str, Any]:
    """
    Generate fallback yt-dlp options with different anti-bot measures.
    
    Args:
        original_opts: Original yt-dlp options
        cookies: Optional cookies string
        temp_dir: Temp directory for cookie file
        
    Returns:
        Modified yt-dlp options for fallback attempt
    """
    fallback_opts = original_opts.copy()
    # Only modify cookies if provided
    if cookies and temp_dir:
        cookie_path = os.path.join(temp_dir, 'cookies.txt')
        if os.path.exists(cookie_path):
            fallback_opts['cookiefile'] = cookie_path
    return fallback_opts


def _get_format_fallback_opts(original_opts: Dict[str, Any], cookies: str = None, temp_dir: str = None) -> Dict[str, Any]:
    """
    Generate fallback yt-dlp options with best quality format (ignores requested quality).
    
    Args:
        original_opts: Original yt-dlp options
        cookies: Optional cookies string
        temp_dir: Temp directory for cookie file
        
    Returns:
        Modified yt-dlp options with best quality format
    """
    fallback_opts = original_opts.copy()
    # Force best quality regardless of requested quality
    fallback_opts['format'] = 'best'
    # Only modify cookies if provided
    if cookies and temp_dir:
        cookie_path = os.path.join(temp_dir, 'cookies.txt')
        if os.path.exists(cookie_path):
            fallback_opts['cookiefile'] = cookie_path
    return fallback_opts


def _convert_json_cookies_to_netscape(json_cookies: str) -> str:
    """
    Convert JSON cookies to Netscape format for yt-dlp.
    
    Args:
        json_cookies: Cookies in JSON format
        
    Returns:
        Cookies in Netscape format
    """
    if not json_cookies:
        return ''

    if "# Netscape HTTP Cookie File" in json_cookies:
        return json_cookies

    try:
        import json
        cookies_data = json.loads(json_cookies)
        
        # Netscape format header
        netscape_cookies = [
            "# Netscape HTTP Cookie File",
            "# https://curl.se/docs/http-cookies.html",
            "# This file was generated by Instagram Video Downloader Actor",
            ""
        ]
        
        # Handle different JSON formats
        if isinstance(cookies_data, list):
            # Array of cookie objects
            for cookie in cookies_data:
                if isinstance(cookie, dict):
                    netscape_line = _format_cookie_as_netscape(cookie)
                    if netscape_line:
                        netscape_cookies.append(netscape_line)
        elif isinstance(cookies_data, dict):
            # Single cookie object or object with domain keys
            if 'name' in cookies_data:
                # Single cookie
                netscape_line = _format_cookie_as_netscape(cookies_data)
                if netscape_line:
                    netscape_cookies.append(netscape_line)
            else:
                # Domain-keyed object
                for domain, domain_cookies in cookies_data.items():
                    if isinstance(domain_cookies, list):
                        for cookie in domain_cookies:
                            if isinstance(cookie, dict):
                                cookie['domain'] = domain
                                netscape_line = _format_cookie_as_netscape(cookie)
                                if netscape_line:
                                    netscape_cookies.append(netscape_line)
        
        return '\n'.join(netscape_cookies)
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        Actor.log.warning(f"Failed to parse JSON cookies: {e}. Assuming already Netscape format.")  # type: ignore
        return json_cookies


def _format_cookie_as_netscape(cookie: Dict[str, Any]) -> str:
    """
    Format a single cookie dict as Netscape format line.
    
    Args:
        cookie: Cookie dictionary
        
    Returns:
        Netscape format line or None if invalid
    """
    try:
        domain = cookie.get('domain') or '.instagram.com'
        host_only = cookie.get('hostOnly') or cookie.get('host_only')
        include_subdomains = 'FALSE' if host_only else 'TRUE'

        if include_subdomains == 'TRUE' and not domain.startswith('.'):
            domain = f'.{domain}'
        if include_subdomains == 'FALSE' and domain.startswith('.'):
            domain = domain.lstrip('.')

        path = cookie.get('path') or '/'
        secure_flag = 'TRUE' if cookie.get('secure', False) else 'FALSE'

        # Determine expiration: use far-future fallback if absent (session cookie)
        expires = cookie.get('expirationDate') or cookie.get('expires')
        if expires is None:
            expires = 2147483647
        else:
            try:
                expires = int(float(expires))
            except (ValueError, TypeError):
                expires = 2147483647

        http_only = cookie.get('httpOnly') or cookie.get('http_only')
        prefix = '#HttpOnly_' if http_only else ''

        name = cookie.get('name')
        value = cookie.get('value')
        if not name or value is None:
            return None

        return f"{prefix}{domain}\t{include_subdomains}\t{path}\t{secure_flag}\t{expires}\t{name}\t{value}"
        
    except Exception:
        return None


# ============================================================ #
#                        CORE FUNCTIONS                       #
# ============================================================ #

async def process_url(
    url: str,
    download_mode: str,
    quality: str,
    max_items: int,
    proxy_url: str | None = None,
    cookies: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Process a single Instagram URL (video, reel, or post) and extract metadata/videos.

    Args:
        url: Instagram URL (video, reel, or post)
        download_mode: 'videos' or 'metadata_only'
        quality: Quality preference
        max_items: Maximum items to process
        proxy_url: Optional proxy URL
        cookies: Optional cookies string

    Returns:
        List of metadata dictionaries for each processed item
    """
    try:
        Actor.log.info(f"Processing: {url}")  # type: ignore

        # Use scrapling to fetch the Instagram page HTML stealthily before yt-dlp
        page_html = None
        if SCRAPLING_AVAILABLE:
            try:
                # Try different scrapling APIs based on version
                if hasattr(scrapling, 'Browser'):
                    try:
                        browser = scrapling.Browser(stealth=True, headless=True)
                        page = browser.goto(url)
                        page_html = page.html
                        browser.close()
                    except Exception as e:
                        Actor.log.warning(f"Scrapling Browser failed: {e}")  # type: ignore
                elif hasattr(scrapling, 'Scraper'):
                    try:
                        scraper = scrapling.Scraper()
                        page_html = scraper.scrape(url).html
                    except Exception as e:
                        Actor.log.warning(f"Scrapling Scraper failed: {e}")  # type: ignore
                else:
                    Actor.log.warning("Scrapling version incompatible - Browser/Scraper not available")  # type: ignore
                if page_html:
                    Actor.log.info("Fetched Instagram page HTML with scrapling (stealth mode)")  # type: ignore
            except Exception as scrapling_error:
                Actor.log.warning(f"Scrapling failed: {scrapling_error}")  # type: ignore

        # Get yt-dlp options
        opts = get_ydl_opts(download_mode, quality, proxy_url, max_items, cookies, url)

        # Use temp directory for cookie file if provided
        temp_dir = None
        if cookies:
            temp_dir = tempfile.mkdtemp()
            cookie_path = os.path.join(temp_dir, 'cookies.txt')
            try:
                netscape_cookies = _convert_json_cookies_to_netscape(cookies)
                with open(cookie_path, 'w', encoding='utf-8') as cf:
                    cf.write(netscape_cookies)
                opts['cookiefile'] = cookie_path
                Actor.log.info('Using provided cookies for authenticated extraction')  # type: ignore
            except Exception as e:
                Actor.log.warning(f'Could not write cookies file: {e}')  # type: ignore

        # Extract info with retry logic
        async def extract_info():
            with yt_dlp.YoutubeDL(opts) as ydl:
                return ydl.extract_info(url, download=False)

        try:
            info = await _retry_with_backoff(extract_info, max_retries=3, base_delay=2.0)
        except Exception as e:
            # Try fallback options if initial extraction fails
            try:
                error_msg = str(e)
            except Exception:
                error_msg = "Unknown extraction error"
            Actor.log.warning(f"Initial extraction failed, trying fallback options: {error_msg[:100]}...")  # type: ignore
            fallback_opts = _get_fallback_opts(opts, cookies, temp_dir)
            async def extract_info_fallback():
                with yt_dlp.YoutubeDL(fallback_opts) as ydl:
                    return ydl.extract_info(url, download=False)

            try:
                info = await _retry_with_backoff(extract_info_fallback, max_retries=2, base_delay=3.0)
            except Exception as fallback_error:
                Actor.log.error(f"All extraction attempts failed for {url}")  # type: ignore
                raise fallback_error

        if not info:
            raise ValueError(f"Could not extract info for {url}")

        results = []

        if not info:
            raise ValueError(f"Could not extract info for {url}")

        # Handle different types of content
        if 'entries' in info:
            entries = info['entries']
            if entries is None:
                Actor.log.warning(f"No entries found in playlist/channel: {url}")  # type: ignore
                entries = []
            else:
                entries = [e for e in entries if e is not None]
                Actor.log.info(f"Found {len(entries)} valid items in playlist/channel")  # type: ignore

            for entry in entries:
                if entry:
                    metadata = await process_single_video(entry, download_mode, quality, proxy_url, cookies)
                    results.append(metadata)
        else:
            metadata = await process_single_video(info, download_mode, quality, proxy_url, cookies)
            results.append(metadata)

        return results

    except Exception as e:
        try:
            error_str = str(e)
        except Exception:
            error_str = "Unknown processing error"
        Actor.log.error(f"Failed to process {url}: {error_str}")  # type: ignore
        return [{
            'url': url,
            'error': error_str,
            'quality_requested': quality,
            'collected_at': datetime.now(UTC).isoformat(),
        }]

    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
            except Exception:
                pass


async def process_single_video(
    info: Dict[str, Any],
    download_mode: str,
    quality: str,
    proxy_url: str | None = None,
    cookies: str | None = None,
) -> Dict[str, Any]:
    """
    Process a single video's metadata and optionally download it.

    Args:
        info: yt-dlp extracted info for the video
        download_mode: 'videos' or 'metadata_only'
        quality: Quality preference
        proxy_url: Optional proxy URL

    Returns:
        Metadata dictionary
    """
    try:
        # Extract metadata
        metadata = {
            'video_id': info.get('id'),
            'title': info.get('title'),
            'author': info.get('uploader'),
            'publish_date': info.get('upload_date'),
            'duration': info.get('duration'),
            'view_count': info.get('view_count'),
            'like_count': info.get('like_count'),
            'description': info.get('description'),
            'thumbnail': info.get('thumbnail'),
            'url': info.get('webpage_url') or info.get('url'),
            'collected_at': datetime.now(UTC).isoformat(),
            'quality_requested': quality,
        }

        # Download video if requested
        if download_mode == 'videos':
            video_data, extension, filename, used_format = await download_video_file(info, quality, proxy_url, cookies)
            
            # Generate safe key for storage
            key = _generate_safe_key(info.get('id', 'unknown'), extension)
            
            metadata.update({
                'file_size': len(video_data),
                'file_extension': extension,
                'file_path': key,  # Use the safe key instead of filename
                'downloaded_format': used_format,
            })

            # Store video in key-value store
            content_type = _guess_content_type(extension)
            await Actor.set_value(key, video_data, content_type=content_type)  # type: ignore

            # Generate direct API download URL so users can fetch without visiting the KV UI
            store = await Actor.open_key_value_store()  # type: ignore
            store_id = getattr(store, 'id', None)
            if store_id:
                download_url = f"https://api.apify.com/v2/key-value-stores/{store_id}/records/{key}?raw=1"
                metadata['download_url'] = download_url
                Actor.log.info(f"Download URL: {download_url}")  # type: ignore
            else:
                metadata['download_url'] = None
                Actor.log.warning("Key-value store ID unavailable, download_url set to None")  # type: ignore
        else:
            metadata.update({
                'file_size': None,
                'file_extension': None,
                'file_path': None,
                'downloaded_format': None,
                'download_url': None,
            })

        return metadata

    except Exception as e:
        try:
            error_str = str(e)
        except Exception:
            error_str = "Unknown video processing error"
        Actor.log.error(f"Failed to process video {info.get('id')}: {error_str}")  # type: ignore
        return {
            'video_id': info.get('id'),
            'url': info.get('webpage_url') or info.get('url'),
            'error': error_str,
            'quality_requested': quality,
            'downloaded_format': None,
            'download_url': None,
            'collected_at': datetime.now(UTC).isoformat(),
        }


async def download_video_file(
    info: Dict[str, Any],
    quality: str,
    proxy_url: str | None = None,
    cookies: str | None = None,
) -> tuple[bytes, str, str, str]:
    """Download the video (or audio) and return its bytes, extension, filename, and format used."""

    url = info.get('webpage_url') or info.get('url')
    if not url:
        raise ValueError('Video URL missing from info dict')

    quality = quality or 'best'

    # Select best format matching user preference
    format_candidates = _build_format_candidates(quality)

    # Use the first format candidate - yt-dlp will handle fallbacks internally
    selected_format = format_candidates[0] if format_candidates else 'best'

    with tempfile.TemporaryDirectory() as temp_dir:
        opts = get_ydl_opts('videos', quality, proxy_url, 0, cookies, url)
        opts['outtmpl'] = os.path.join(temp_dir, '%(id)s.%(ext)s')
        opts['format'] = selected_format

        cookie_path = None
        if cookies:
            cookie_path = os.path.join(temp_dir, 'cookies.txt')
            try:
                netscape_cookies = _convert_json_cookies_to_netscape(cookies)
                with open(cookie_path, 'w', encoding='utf-8') as cf:
                    cf.write(netscape_cookies)
                Actor.log.info('Using provided cookies for authenticated download')  # type: ignore
            except Exception as e:
                Actor.log.warning(f'Could not write cookies file: {e}')  # type: ignore
                cookie_path = None
        if cookie_path:
            opts['cookiefile'] = cookie_path

        # When we are extracting audio-only and ffmpeg is available, convert to mp3 for convenience
        if quality.lower() == 'audio_only' and FFMPEG_AVAILABLE:
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
            opts['keepvideo'] = False
            opts['merge_output_format'] = 'mp3'

        _clear_directory(temp_dir)

        Actor.log.info(f"Download using format '{opts['format']}'")

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([url])

            media_path = _find_downloaded_media(temp_dir)
            if not media_path:
                raise FileNotFoundError('Download completed but no media file was produced')

            with media_path.open('rb') as f:
                data = f.read()

            extension = media_path.suffix.lstrip('.').lower()
            filename = media_path.name

            Actor.log.info(f"Download succeeded with format '{opts['format']}' → {filename}")
            return data, extension, filename, opts['format']

        except Exception as e:
            Actor.log.error(f"Download failed for {url} with format '{opts['format']}': {e}")
            raise


async def process_urls(
    urls: List[str],
    download_mode: str,
    quality: str,
    max_items: int,
    proxy_url: str | None = None,
    proxy_configuration: Any | None = None,
    cookies: str | None = None,
) -> None:
    """
    Process a list of Instagram URLs.

    Args:
        urls: List of Instagram URLs (videos, reels, posts)
        download_mode: 'videos' or 'metadata_only'
        quality: Quality preference
        max_items: Maximum items to process
        proxy_url: Optional proxy URL to use for downloading
        proxy_configuration: Optional Apify ProxyConfiguration object for rotating proxies
    """
    total_processed = 0
    total_success = 0

    for i, url in enumerate(urls):
        active_proxy_url = proxy_url
        if proxy_configuration is not None:
            try:
                fresh_url = await proxy_configuration.new_url()
                active_proxy_url = str(fresh_url) if fresh_url else proxy_url
            except Exception as proxy_error:
                Actor.log.warning(f"Unable to obtain fresh proxy URL: {proxy_error}")
                active_proxy_url = proxy_url

        try:
            # Process URL (may return multiple items for playlists/channels)
            results = await process_url(url, download_mode, quality, max_items, active_proxy_url, cookies)

            # Push each result to dataset
            for metadata in results:
                await Actor.push_data(metadata)
                if 'error' not in metadata:  # Count successful items
                    total_success += 1

            Actor.log.info(f"Processed {len(results)} items from {url}")

        except Exception as e:
            try:
                error_str = str(e)
            except Exception:
                error_str = "Unknown processing error"
            Actor.log.error(f"Failed to process {url}: {error_str}")
            # Still push error info to dataset
            error_data = {
                'url': url,
                'error': error_str,
                'quality_requested': quality,
                'collected_at': datetime.now(UTC).isoformat(),
            }
            await Actor.push_data(error_data)

        total_processed += 1

        # Intelligent rate limiting: longer delays for more URLs, random jitter
        if i < len(urls) - 1:  # Don't delay after last URL
            base_delay = min(2.0 + (len(urls) * 0.5), 10.0)  # Scale with URL count
            jitter = random.uniform(0.5, 2.0)  # Random multiplier
            delay = base_delay * jitter
            Actor.log.info(f"Rate limiting: waiting {delay:.1f}s before next URL")
            await asyncio.sleep(delay)

    Actor.log.info(f"Processing complete! Successfully processed {total_success} items")


# ============================================================ #
#                            MAIN                              #
# ============================================================ #

async def main() -> None:
    """
    Main actor function.
    """
    start_time = datetime.now(UTC)
    Actor.log.info(f"Instagram Video Downloader started at {start_time.isoformat()}")

    async with Actor:
        # Get input
        inp = await Actor.get_input() or {}

        # Handle input: can be single URL string, a JSON array string, or list of URLs
        urls_input = inp.get('urls', '')
        urls = []
        if isinstance(urls_input, list):
            urls = urls_input
        elif isinstance(urls_input, str):
            s = urls_input.strip()
            if not s:
                urls = []
            else:
                # Try to parse as JSON first
                try:
                    import json
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        urls = parsed
                    elif isinstance(parsed, str):
                        urls = [parsed]
                    else:
                        urls = [str(parsed)]
                except Exception:
                    # Not JSON, try splitting by newlines or commas
                    lines = [line.strip() for line in s.split('\n') if line.strip()]
                    if len(lines) > 1:
                        urls = lines
                    else:
                        # Try comma separated
                        parts = [p.strip() for p in s.split(',') if p.strip()]
                        if len(parts) > 1:
                            urls = parts
                        else:
                            urls = [s]
        else:
            urls = []

        if not urls:
            Actor.log.error("No URLs provided in input. Expected 'urls' field with string or list of Instagram URLs.")
            return

        # Extract proxy configuration
        proxy_url: str | None = None
        proxy_configuration = None
        proxy_input = inp.get("proxyConfiguration") or {}

        if proxy_input.get("proxyUrls"):
            proxy_url = proxy_input["proxyUrls"][0]
            Actor.log.info("Using custom proxy URL provided in input")
        else:
            try:
                if proxy_input:
                    # Filter out invalid parameters that the SDK doesn't accept
                    valid_proxy_params = {k: v for k, v in proxy_input.items() 
                                        if k not in ['useApifyProxy', 'apifyProxyGroups', 'apifyProxyCountry']}
                    if valid_proxy_params:
                        proxy_configuration = await Actor.create_proxy_configuration(**valid_proxy_params)
                    else:
                        proxy_configuration = await Actor.create_proxy_configuration()
                else:
                    proxy_configuration = await Actor.create_proxy_configuration()
                if proxy_configuration:
                    fresh_proxy_url = await proxy_configuration.new_url()
                    proxy_url = str(fresh_proxy_url) if fresh_proxy_url else None
                    Actor.log.info("Using Apify proxy configuration")
            except Exception as proxy_error:
                Actor.log.warning(f"Unable to initialize proxy configuration: {proxy_error}")
                proxy_configuration = None
                proxy_url = None

        # Extract additional parameters
        download_mode = inp.get('downloadMode', 'videos')
        quality = inp.get('quality', 'best')
        max_items = int(inp.get('maxItems', 10))

        Actor.log.info(f"Download mode: {download_mode}, Quality: {quality}, Max items: {max_items}")

        # Validate URLs (comprehensive Instagram URL validation)
        valid_urls = []
        for url in urls:
            normalized_url = _normalize_instagram_url(url)
            if _validate_instagram_url(normalized_url):
                valid_urls.append(normalized_url)
            else:
                Actor.log.warning(f"Skipping invalid or unsupported Instagram URL: {url}")

        if not valid_urls:
            Actor.log.error("No valid Instagram URLs found. Supported formats: posts (/p/), reels (/reel/), IGTV (/tv/)")
            return

        # Extract cookies if provided
        cookies = inp.get('cookies')
        if cookies:
            Actor.log.info('Cookies provided in input — will use for authenticated downloads')

        # Process the URLs
        await process_urls(
            valid_urls,
            download_mode,
            quality,
            max_items,
            proxy_url,
            proxy_configuration,
            cookies,
        )

        # Performance metrics
        end_time = datetime.now(UTC)
        duration = (end_time - start_time).total_seconds()
        Actor.log.info(f"Instagram Video Downloader completed at {end_time.isoformat()}")
        Actor.log.info(f"Total execution time: {duration:.2f} seconds")
        Actor.log.info(f"Processed {len(valid_urls)} URLs successfully")


if __name__ == "__main__":
    asyncio.run(main())
