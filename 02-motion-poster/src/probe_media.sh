#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 INPUT_VIDEO [OUTPUT_DIR]" >&2
  exit 2
fi

INPUT="$1"
OUTPUT_DIR="${2:-$(dirname "$INPUT")/media_analysis}"
mkdir -p "$OUTPUT_DIR"
BASE="$(basename "$INPUT")"
STEM="${BASE%.*}"
TECH="$OUTPUT_DIR/${STEM}_technical.txt"
AUDIO="$OUTPUT_DIR/${STEM}_audio.wav"
AUDIO_ANALYSIS="$OUTPUT_DIR/${STEM}_audio_analysis.txt"
CONTACT="$OUTPUT_DIR/${STEM}_contact_sheet.jpg"

ffprobe -v error \
  -show_entries format=duration:stream=index,codec_name,codec_type,sample_rate,channels,width,height,r_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 "$INPUT" > "$TECH"

ffmpeg -y -i "$INPUT" -vn -ac 1 -ar 44100 "$AUDIO" >/dev/null 2>&1

ANALYZER="${SERTAI_AUDIO_ANALYZER:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/analyze_audio.py}"
if [[ -f "$ANALYZER" ]] && python3 "$ANALYZER" "$AUDIO" > "$AUDIO_ANALYSIS" 2>&1; then
  :
else
  printf '%s\n' "Audio analysis could not be completed; inspect the error below." >> "$AUDIO_ANALYSIS"
fi

ffmpeg -y -i "$INPUT" \
  -vf "fps=1/10,scale=360:-1,tile=4x2:padding=8:margin=8" \
  -frames:v 1 "$CONTACT" >/dev/null 2>&1

printf 'Technical report: %s\nAudio file: %s\nAudio analysis: %s\nContact sheet: %s\n' \
  "$TECH" "$AUDIO" "$AUDIO_ANALYSIS" "$CONTACT"
