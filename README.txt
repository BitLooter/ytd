== NOTICE ==
This script is now obsolete. youtube-dl can now do everything this will,
and better. I recommend you use it instead. This repository will be kept
here for historical/educational purposes.

You can duplicate this script's functionality in youtube-dl with the
following command line:

youtube-dl <video URL or ID> -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]' --add-metadata --xattrs --embed-subs --embed-thumbnail --all-subs -o '%(title)s.%(ext)s'

youtube-dl can also add metadata to an existing video, use the above command
line but leave out the -f switch and set -o to the existing video file.

== Old readme ==
Downloads a video from YouTube and relevant metadata - tags, subs, thumbnail,
etc. Also gets the highest quality DASH streams and muxes them together.
Requires pafy (Python library), youtube-dl, MP4Box, and AtomicParsley to be
installed on your system and in your path.
