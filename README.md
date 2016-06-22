# Roughcut
Video editor that lets you cut a video by only watching each clip once. The result may be rough, but it is a very fast process, optimized for home videos or just rough cuts.

Making a video is a 2 step process:

Run:  
`roughcut.py`  
Use the file menu to select the videos to rate.
This will show the first video. Use the short cuts, especially 1-5 to rate the parts of the video
(1 is worst 5 is best). Press the next button to go to the next video.
This will crate a .qhv.meta file (name will change) for each video.

`makevideo.py out.mp4 video1.mp4.qhv.meta video2.qhv.meta [...]`
This will create the video. By default all parts rated 4 or 5 will be shown.
Specify `-p advanced` which will use the profile in `profiles/advanced`.
It sets a minimum and maximum size for individual clips as well as the video as a whole.
There is room for improovement, but it is optimized for home video on social media.
This "intelligent" filter is what needs to be expanded for Roughcut to show its full potential.


Shortcuts
---------
* m - Move the latest rating to now.
* l - Move the latest rating back 12 frames (roughly 0.5 second).
* f - Fast forward 3 seconds.
* b - Rewind the video 3 seconds.
* 1-5 - Rate the current part 1-5

Dependencies
------------
* `pyexiftool` - https://github.com/smarnach/pyexiftool
* `exiftool` - http://www.sno.phy.queensu.ca/~phil/exiftool/
* `vlc` - http://www.videolan.org/
* `mlt` - https://www.mltframework.org/
* `iso8601` - pip install iso8601

