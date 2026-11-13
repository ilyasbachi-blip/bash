#!/usr/bin/env bash
# Export final Reels/TikTok : 1080x1920, 25 i/s, H.264 High, AAC 48 kHz,
# loudness -14 LUFS intégré / true peak -1 dBTP (loudnorm en deux passes).
#
# Usage : outils/export_reel.sh entree.(mov|mp4) sortie.mp4 [sous-titres.ass]
# L'entrée est le master du montage (déjà étalonné). Les rushs ne sont jamais touchés.
set -euo pipefail
IN="$1"; OUT="$2"; ASS="${3:-}"
[ -f "$IN" ] || { echo "entrée introuvable : $IN" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"

VF="scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=25,format=yuv420p"
if [ -n "$ASS" ]; then
  VF="$VF,ass='${ASS//\'/\\\'}'"
fi

# Passe 1 : mesure
STATS=$(ffmpeg -hide_banner -nostats -i "$IN" -vn \
  -af loudnorm=I=-14:TP=-1:LRA=11:print_format=json -f null - 2>&1 \
  | sed -n '/^{/,/^}/p')
get() { echo "$STATS" | python3 -c "import sys,json;print(json.load(sys.stdin)['$1'])"; }
MI=$(get input_i); MTP=$(get input_tp); MLRA=$(get input_lra); MT=$(get input_thresh); OFF=$(get target_offset)

# Passe 2 : rendu
ffmpeg -hide_banner -v warning -stats -y -i "$IN" \
  -vf "$VF" \
  -af "loudnorm=I=-14:TP=-1:LRA=11:measured_I=$MI:measured_TP=$MTP:measured_LRA=$MLRA:measured_thresh=$MT:offset=$OFF:linear=true,aresample=48000" \
  -c:v libx264 -profile:v high -level 4.1 -preset slow -crf 18 -maxrate 16M -bufsize 32M \
  -g 50 -bf 2 -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 256k -ar 48000 -ac 2 \
  -movflags +faststart "$OUT"

# Contrôle
ffmpeg -hide_banner -nostats -i "$OUT" -af ebur128=peak=true -f null - 2>&1 \
  | grep -E "^\s+(I:|Peak:)" | tail -2
