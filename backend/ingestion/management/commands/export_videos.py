import os
import csv
import re
from pathlib import Path
from collections import Counter
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def parse_iso8601_duration(duration_str):
    if not duration_str:
        return 0
    pattern = re.compile(r'PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?')
    match = pattern.match(duration_str)
    if not match:
        return 0
    parts = match.groupdict()
    hours = int(parts['hours'] or 0)
    minutes = int(parts['minutes'] or 0)
    seconds = int(parts['seconds'] or 0)
    return hours * 3600 + minutes * 60 + seconds

class Command(BaseCommand):
    help = 'Export YouTube videos and playlists from channel to CSV files'

    def add_arguments(self, parser):
        parser.add_argument('--channel-id', type=str, default=None, help='YouTube Channel ID')
        parser.add_argument('--api-key', type=str, default=None, help='YouTube Data API Key')
        parser.add_argument('--output-dir', type=str, default=None, help='Output directory for CSV files')

    def handle(self, *args, **options):
        api_key = options.get('api_key') or getattr(settings, 'YOUTUBE_API_KEY', '') or os.environ.get('YOUTUBE_API_KEY', '')
        channel_id = options.get('channel_id') or getattr(settings, 'YOUTUBE_CHANNEL_ID', '') or os.environ.get('YOUTUBE_CHANNEL_ID', 'UCSJbobMuvnvZR-7UKBzxsLg')
        
        root_dir = Path(settings.BASE_DIR).parent
        output_dir = Path(options['output_dir']) if options.get('output_dir') else root_dir / 'data'
        output_dir.mkdir(parents=True, exist_ok=True)

        videos_csv_path = output_dir / 'adept_videos.csv'
        playlists_csv_path = output_dir / 'adept_playlists.csv'

        if not api_key:
            self.stderr.write(self.style.ERROR("ERROR: YOUTUBE_API_KEY is not configured in backend/.env or environment."))
            self.stderr.write(self.style.WARNING("Please provide a valid YouTube Data API key to fetch live channel data."))
            raise CommandError("YOUTUBE_API_KEY missing")

        self.stdout.write(f"Connecting to YouTube API for channel ID: {channel_id}...")

        youtube = build('youtube', 'v3', developerKey=api_key)

        # 1. Fetch channel details to get Uploads playlist ID
        try:
            channel_response = youtube.channels().list(
                part='contentDetails,snippet',
                id=channel_id
            ).execute()
        except HttpError as e:
            self.stderr.write(self.style.ERROR(f"YouTube API HttpError: {e}"))
            raise CommandError(f"YouTube API call failed: {e}")

        items = channel_response.get('items', [])
        if not items:
            # Try fetching by handle if ID failed
            try:
                channel_response = youtube.channels().list(
                    part='contentDetails,snippet',
                    forHandle='adepteduverse'
                ).execute()
                items = channel_response.get('items', [])
            except HttpError as e:
                pass

        if not items:
            raise CommandError(f"Channel not found for ID '{channel_id}' or handle 'adepteduverse'")

        uploads_playlist_id = items[0]['contentDetails']['relatedPlaylists']['uploads']
        channel_title = items[0]['snippet']['title']
        self.stdout.write(self.style.SUCCESS(f"Found Channel: '{channel_title}' (Uploads Playlist: {uploads_playlist_id})"))

        # 2. Fetch video IDs from Uploads playlist
        video_ids = []
        next_page_token = None

        self.stdout.write("Fetching video list from uploads playlist...")
        while True:
            playlist_req = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            )
            playlist_res = playlist_req.execute()

            for item in playlist_res.get('items', []):
                vid = item['contentDetails']['videoId']
                if vid:
                    video_ids.append(vid)

            next_page_token = playlist_res.get('nextPageToken')
            if not next_page_token:
                break

        self.stdout.write(self.style.SUCCESS(f"Total videos identified: {len(video_ids)}"))

        # 3. Fetch detailed video information in batches of 50
        videos_data = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            v_req = youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=','.join(batch_ids)
            )
            v_res = v_req.execute()

            for item in v_res.get('items', []):
                v_id = item['id']
                snippet = item.get('snippet', {})
                content_details = item.get('contentDetails', {})

                title = snippet.get('title', '')
                description = snippet.get('description', '')
                published_at = snippet.get('publishedAt', '')
                duration_str = content_details.get('duration', '')
                duration_sec = parse_iso8601_duration(duration_str)
                is_short = duration_sec <= 180

                thumbnails = snippet.get('thumbnails', {})
                thumbnail_url = (
                    thumbnails.get('maxres', {}).get('url') or
                    thumbnails.get('high', {}).get('url') or
                    thumbnails.get('medium', {}).get('url') or
                    thumbnails.get('default', {}).get('url') or
                    ''
                )

                tags_list = snippet.get('tags', [])
                tags = '|'.join(tags_list) if tags_list else ''

                videos_data.append({
                    'video_id': v_id,
                    'title': title,
                    'description': description,
                    'published_at': published_at,
                    'duration_sec': duration_sec,
                    'is_short': is_short,
                    'thumbnail_url': thumbnail_url,
                    'tags': tags
                })

        # Write adept_videos.csv
        with open(videos_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'video_id', 'title', 'description', 'published_at',
                'duration_sec', 'is_short', 'thumbnail_url', 'tags'
            ])
            writer.writeheader()
            writer.writerows(videos_data)

        self.stdout.write(self.style.SUCCESS(f"Saved {len(videos_data)} video records to {videos_csv_path}"))

        # 4. Export Playlists
        self.stdout.write("Fetching channel playlists...")
        playlists_data = []
        next_pl_page_token = None
        while True:
            pl_req = youtube.playlists().list(
                part='snippet,contentDetails',
                channelId=channel_id,
                maxResults=50,
                pageToken=next_pl_page_token
            )
            pl_res = pl_req.execute()
            for pl in pl_res.get('items', []):
                playlists_data.append({
                    'playlist_id': pl['id'],
                    'title': pl['snippet']['title'],
                    'item_count': pl['contentDetails']['itemCount']
                })
            next_pl_page_token = pl_res.get('nextPageToken')
            if not next_pl_page_token:
                break

        with open(playlists_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['playlist_id', 'title', 'item_count'])
            writer.writeheader()
            writer.writerows(playlists_data)

        self.stdout.write(self.style.SUCCESS(f"Saved {len(playlists_data)} playlist records to {playlists_csv_path}"))

        # 5. Analysis
        total_count = len(videos_data)
        shorts_count = sum(1 for v in videos_data if v['is_short'])
        long_count = total_count - shorts_count
        missing_desc_count = sum(1 for v in videos_data if not v['description'] or not v['description'].strip())

        # Top 20 title words analysis
        stop_words = {
            'a', 'an', 'the', 'and', 'or', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'for', 'from', 'as', 'it',
            'this', 'that', 'jee', 'maths', 'mathematics', 'class', 'video', 'part', 'ep', 'episode', '&', '-', '|', ':'
        }

        all_words = []
        for v in videos_data:
            words = re.findall(r'\w+', v['title'].lower())
            filtered = [w for w in words if len(w) > 1 and w not in stop_words and not w.isdigit()]
            all_words.extend(filtered)

        word_counts = Counter(all_words).most_common(20)

        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("PHASE 0 EXPORT ANALYSIS REPORT"))
        self.stdout.write("="*50)
        self.stdout.write(f"Total Videos: {total_count}")
        self.stdout.write(f"Shorts (<= 180s): {shorts_count}")
        self.stdout.write(f"Long Videos (> 180s): {long_count}")
        self.stdout.write(f"Missing Descriptions: {missing_desc_count}")
        self.stdout.write("\nTop 20 Title Words:")
        for rank, (word, count) in enumerate(word_counts, 1):
            self.stdout.write(f"  {rank:2d}. {word}: {count}")
        self.stdout.write("="*50 + "\n")
