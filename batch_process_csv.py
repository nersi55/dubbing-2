"""
Batch processor for YouTube URLs from a CSV file.

Usage:
  python batch_process_csv.py --csv snaptales3_shorts.csv \
    --api-key <GOOGLE_API_KEY> [--youtube-api-key <YOUTUBE_API_KEY>] \
    [--method whisper|youtube] [--target Persian (FA)]

CSV format:
  - One URL per line, OR
  - With header containing a column named 'YouTube_Short_URL' or 'url'.
"""

import argparse
import csv
import os
import sys
import time
from pathlib import Path

from typing import List, Tuple

from dubbing_functions import VideoDubbingApp


def read_urls(csv_path: Path) -> List[str]:
    urls: List[str] = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Try CSV first
        try:
            reader = csv.DictReader(f)
            fieldnames = [fn.strip().lower() for fn in (reader.fieldnames or [])]
            candidate_cols = ['youtube_short_url', 'url', 'youtube_url']
            selected = None
            for c in candidate_cols:
                if c in fieldnames:
                    selected = c
                    break
            if selected:
                for row in reader:
                    val = row.get(selected) or row.get(selected.capitalize())
                    if val and val.strip():
                        urls.append(val.strip())
                return urls
        except Exception:
            f.seek(0)
            pass

    # Fallback: one URL per line (ignore empty lines)
    with open(csv_path, 'r', encoding='utf-8') as f2:
        for line in f2:
            line = line.strip()
            if not line or line.lower().startswith('http') is False:
                # Allow header row like 'YouTube_Short_URL'
                if line.lower() in ('youtube_short_url', 'url', 'youtube_url'):
                    continue
            if line and line.startswith('http'):
                urls.append(line)
    return urls


def process_url(app: VideoDubbingApp, url: str, extraction_method: str, target_language: str) -> Tuple[str, bool, str]:
    start_ts = time.time()
    try:
        ok = app.download_youtube_video(url)
        if not ok:
            return (url, False, 'download_failed')

        if extraction_method == 'youtube':
            ok = app.extract_transcript_from_youtube(url)
        else:
            ok = app.extract_audio_with_whisper()
        if not ok:
            return (url, False, 'transcript_failed')

        ok = app.translate_subtitles(target_language)
        if not ok:
            return (url, False, 'translate_failed')

        # Create video with subtitles using default configs inside the class
        output_path = app.create_subtitled_video()
        if not output_path or not os.path.exists(output_path):
            return (url, False, 'video_failed')

        dur = int(time.time() - start_ts)
        return (url, True, f'ok:{Path(output_path).name} ({dur}s)')

    except Exception as e:
        return (url, False, f'exception:{str(e)[:120]}')


def main():
    parser = argparse.ArgumentParser(description='Batch process YouTube URLs from CSV')
    parser.add_argument('--csv', required=True, help='Path to CSV file containing URLs')
    parser.add_argument('--api-key', default=os.getenv('GOOGLE_API_KEY', ''), help='Google API key')
    parser.add_argument('--youtube-api-key', default=os.getenv('YOUTUBE_API_KEY', ''), help='YouTube API key (optional)')
    parser.add_argument('--method', choices=['whisper', 'youtube'], default='whisper', help='Transcription method')
    parser.add_argument('--target', default='Persian (FA)', help='Target language for subtitles')
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"❌ CSV not found: {csv_path}")
        sys.exit(1)

    api_key = args.api_key
    if not api_key:
        print('❌ API key is required. Provide --api-key or set GOOGLE_API_KEY env variable.')
        sys.exit(1)

    urls = read_urls(csv_path)
    if not urls:
        print('❌ No URLs found in CSV')
        sys.exit(1)

    print(f"🗂️ Found {len(urls)} URLs. Starting batch...")
    app = VideoDubbingApp(api_key, args.youtube_api_key or None)

    report_lines: List[str] = []
    success_count = 0
    for idx, url in enumerate(urls, start=1):
        print(f"\n[{idx}/{len(urls)}] ▶️ {url}")
        url_result = process_url(app, url, args.method, args.target)
        status = 'SUCCESS' if url_result[1] else 'FAIL'
        print(f"   → {status} | {url_result[2]}")
        report_lines.append(f"{status},{url},{url_result[2]}")
        if url_result[1]:
            success_count += 1

    report_path = Path('dubbing_work') / f'batch_report_{int(time.time())}.csv'
    report_path.write_text('\n'.join(['status,url,detail'] + report_lines), encoding='utf-8')
    print(f"\n✅ Done. {success_count}/{len(urls)} succeeded. Report: {report_path}")


if __name__ == '__main__':
    main()


