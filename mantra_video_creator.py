#!/usr/bin/env python3
"""
Mantra Video Creator
Loops a video multiple times with count overlay (1/22, 2/22, etc.)
and optional running timer.

Usage:
    python mantra_video_creator.py input.mp4 -o output.mp4
    python mantra_video_creator.py input.mp4 -o output.mp4 --timer
    python mantra_video_creator.py "https://youtube.com/..." -o output.mp4 --loops 22
"""

import argparse
import subprocess
import os
import sys
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required tools are installed."""
    missing = []
    for tool in ['ffmpeg', 'ffprobe']:
        if not shutil.which(tool):
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing required tools: {', '.join(missing)}")
        print("Install with: sudo apt install ffmpeg")
        sys.exit(1)


def download_video(url: str, output_path: str) -> str:
    """Download video from YouTube or other sources."""
    try:
        subprocess.run(['yt-dlp', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Installing yt-dlp...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'yt-dlp', '-q'])
    
    print(f"📥 Downloading video from: {url}")
    output_file = output_path
    subprocess.run([
        'yt-dlp',
        '-f', 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
        '--merge-output-format', 'mp4',
        '-o', output_file,
        url
    ], check=True)
    
    return output_file


def get_video_duration(video_path: str) -> float:
    """Get video duration in seconds."""
    result = subprocess.run([
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'csv=p=0',
        video_path
    ], capture_output=True, text=True, check=True)
    
    return float(result.stdout.strip())


def create_looped_video(
    input_path: str,
    output_path: str,
    loops: int = 22,
    show_timer: bool = False,
    font_size: int = 72,
    font_color: str = 'gold',
    position: str = 'top'  # 'top' or 'bottom'
):
    """Create a looped video with count overlay."""
    
    check_dependencies()
    
    # Handle URL input
    if input_path.startswith(('http://', 'https://')):
        downloaded_path = '/tmp/mantra_source.mp4'
        input_path = download_video(input_path, downloaded_path)
    
    if not os.path.exists(input_path):
        print(f"❌ Input file not found: {input_path}")
        sys.exit(1)
    
    duration = get_video_duration(input_path)
    print(f"📹 Input video duration: {duration:.2f} seconds ({duration/60:.2f} min)")
    print(f"📹 Final video will be: {duration * loops / 60:.2f} minutes")
    
    temp_dir = Path('/tmp/mantra_parts')
    temp_dir.mkdir(exist_ok=True)
    
    # Clean up any previous temp files
    for f in temp_dir.glob('part_*.mp4'):
        f.unlink()
    
    y_position = '50' if position == 'top' else 'h-100'
    timer_y = '120' if position == 'top' else 'h-170'
    
    # Create each part with count overlay
    print(f"\n🔄 Creating {loops} parts with count overlay...")
    
    for i in range(1, loops + 1):
        print(f"   Processing part {i}/{loops}...", end=' ', flush=True)
        
        # Build filter string
        filters = [
            f"drawtext=text='{i} / {loops}':fontsize={font_size}:fontcolor={font_color}:"
            f"borderw=3:bordercolor=black:x=(w-text_w)/2:y={y_position}"
        ]
        
        if show_timer:
            # Calculate time offset for continuous timer
            time_offset = (i - 1) * duration
            filters.append(
                f"drawtext=text='%{{pts\\:hms}}':fontsize=48:fontcolor=white:"
                f"borderw=2:bordercolor=black:x=(w-text_w)/2:y={timer_y}:"
                f"start_number={time_offset}"
            )
        
        filter_str = ','.join(filters)
        
        part_output = temp_dir / f'part_{i:02d}.mp4'
        
        subprocess.run([
            'ffmpeg', '-y', '-i', input_path,
            '-vf', filter_str,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '192k',
            str(part_output)
        ], capture_output=True, check=True)
        
        print("✓")
    
    # Create concat list
    list_file = temp_dir / 'list.txt'
    with open(list_file, 'w') as f:
        for i in range(1, loops + 1):
            f.write(f"file 'part_{i:02d}.mp4'\n")
    
    # Concatenate all parts
    print(f"\n🔗 Concatenating {loops} parts...")
    subprocess.run([
        'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
        '-i', str(list_file),
        '-c', 'copy',
        output_path
    ], check=True)
    
    # Cleanup temp files
    print("🧹 Cleaning up temporary files...")
    shutil.rmtree(temp_dir)
    
    final_duration = get_video_duration(output_path)
    print(f"\n✅ Done! Output saved to: {output_path}")
    print(f"📹 Final duration: {final_duration/60:.2f} minutes")


def main():
    parser = argparse.ArgumentParser(
        description='Create a looped mantra video with count overlay',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.mp4 -o mantra_22x.mp4
  %(prog)s input.mp4 -o mantra_22x.mp4 --timer
  %(prog)s input.mp4 -o mantra_22x.mp4 --loops 21 --color white
  %(prog)s "https://youtube.com/watch?v=..." -o mantra_22x.mp4
        """
    )
    
    parser.add_argument('input', help='Input video file or YouTube URL')
    parser.add_argument('-o', '--output', default='output_looped.mp4',
                        help='Output video file (default: output_looped.mp4)')
    parser.add_argument('-l', '--loops', type=int, default=22,
                        help='Number of loops (default: 22)')
    parser.add_argument('--timer', action='store_true',
                        help='Show running timer')
    parser.add_argument('--font-size', type=int, default=72,
                        help='Font size for count (default: 72)')
    parser.add_argument('--color', default='gold',
                        help='Font color (default: gold)')
    parser.add_argument('--position', choices=['top', 'bottom'], default='top',
                        help='Position of count overlay (default: top)')
    
    args = parser.parse_args()
    
    create_looped_video(
        input_path=args.input,
        output_path=args.output,
        loops=args.loops,
        show_timer=args.timer,
        font_size=args.font_size,
        font_color=args.color,
        position=args.position
    )


if __name__ == '__main__':
    main()
