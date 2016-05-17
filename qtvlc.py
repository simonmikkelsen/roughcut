#! /usr/bin/python

#
# Qt example for VLC Python bindings
# Copyright (C) 2009-2010 the VideoLAN team
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston MA 02110-1301, USA.
#
# This version has since been forked and developed into
# Quick Home Video by Simon Mikkelsen (http://mikkelsen.tv/simon/).
# The license remains unchanged.
# 

import sys
import os.path
import vlc
import json
from PyQt4 import QtGui, QtCore

class Player(QtGui.QMainWindow):
    """A simple Media Player using VLC and Qt
    """
    def __init__(self, master=None):
        QtGui.QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")

        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.createUI()
        self.isPaused = False
        self.frameRate = -1

    def keyPressEvent(self, e):
        if self.keyListener == None:
            return

        mediaTime = self.mediaplayer.get_time()
        if mediaTime < 0:
            return

        framerate = self.getFrameRate()
        frameNo = int(mediaTime * framerate / 1000)
        self.keyListener.keyPressed(e.text(), frameNo)

    def getFrameRate(self):
        if self.frameRate < 0:
            tracks = self.media.tracks_get()
            num = tracks[0][0][0].u.video[0].frame_rate_num
            den = tracks[0][0][0].u.video[0].frame_rate_den
            if int(den) > 0:
                self.frameRate = int(num)/int(den)
        return self.frameRate 

    def addKeyListener(self, keyListener):
        self.keyListener = keyListener

    def createUI(self):
        """Set up the user interface, signals & slots
        """
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if sys.platform == "darwin": # for MacOS
            self.videoframe = QtGui.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtGui.QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor (QtGui.QPalette.Window,
                               QtGui.QColor(0,0,0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.positionslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setMaximum(1000)
        self.connect(self.positionslider,
                     QtCore.SIGNAL("sliderMoved(int)"), self.setPosition)

        self.hbuttonbox = QtGui.QHBoxLayout()
        self.playbutton = QtGui.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        self.timebutton = QtGui.QPushButton("Time")
        self.hbuttonbox.addWidget(self.timebutton)
        self.connect(self.timebutton, QtCore.SIGNAL("clicked()"),
                     self.PrintTime)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtGui.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip("Volume")
        self.hbuttonbox.addWidget(self.volumeslider)
        self.connect(self.volumeslider,
                     QtCore.SIGNAL("valueChanged(int)"),
                     self.setVolume)

        self.vboxlayout = QtGui.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.widget.setLayout(self.vboxlayout)

        open = QtGui.QAction("&Open", self)
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFile)
        exit = QtGui.QAction("&Exit", self)
        self.connect(exit, QtCore.SIGNAL("triggered()"), sys.exit)
        menubar = self.menuBar()
        filemenu = menubar.addMenu("&File")
        filemenu.addAction(open)
        filemenu.addSeparator()
        filemenu.addAction(exit)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(200)
        self.connect(self.timer, QtCore.SIGNAL("timeout()"),
                     self.updateUI)

    def PrintTime(self):
        time = self.mediaplayer.get_time()
        print "Time: "+str(time)

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("Play")

    def OpenFile(self, filename=None):
        """Open a media file in a MediaPlayer
        """
        if filename is None:
            filename = QtGui.QFileDialog.getOpenFileName(self, "Open File", os.path.expanduser('~'))
        if not filename:
            return

        # create the media
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # parse the metadata of the file
        self.media.parse()
        # set the title of the track as window title
        self.setWindowTitle(self.media.get_meta(0))

        # the media player has to be 'connected' to the QFrame
        # (otherwise a video would be displayed in it's own window)
        # this is platform specific!
        # you have to give the id of the QFrame (or similar object) to
        # vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.videoframe.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.videoframe.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(self.videoframe.winId())
        self.PlayPause()

    def setVolume(self, Volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(Volume)

    def setPosition(self, position):
        """Set the position
        """
        # setting the position to where the slider was dragged
        self.mediaplayer.set_position(position / 1000.0)
        # the vlc MediaPlayer needs a float value between 0 and 1, Qt
        # uses integer variables, so you need a factor; the higher the
        # factor, the more precise are the results
        # (1000 should be enough)

    def updateUI(self):
        """updates the user interface"""
        # setting the slider to the desired position
        self.positionslider.setValue(self.mediaplayer.get_position() * 1000)

        if not self.mediaplayer.is_playing():
            # no need to call this function if nothing is played
            self.timer.stop()
            if not self.isPaused:
                # after the video finished, the play button stills shows
                # "Pause", not the desired behavior of a media player
                # this will fix it
                self.Stop()
class RatingEventKeyAdapter:
    def __init__(self, receiver):
        self.receiver = receiver
    def keyPressed(self, key, frameno):
        if key == "1":
            self.receiver.setRating(frameno, 1)
        elif key == "2":
            self.receiver.setRating(frameno, 2)
        elif key == "3":
            self.receiver.setRating(frameno, 3)
        elif key == "4":
            self.receiver.setRating(frameno, 4)
        elif key == "5":
            self.receiver.setRating(frameno, 5)
        elif key == "0":
            self.receiver.setRating(frameno, 0)
        elif key == "m":
            self.receiver.subtractFramesFromLatest(12)
        # Ignore other key events.

class ClipInfoManager:
    def __init__(self, filename, clipInfoFile):
        self.filename = filename 
        self.clipInfoFile = clipInfoFile
    def setRating(self, frameNo, rating):
        self.clipInfoFile.addInfo(frameNo, rating)
    def subtractFramesFromLatest(self, frames):
        self.clipInfoFile.subtractFramesFromLatest(frames)

class ClipInfoJsonFile:
    def __init__(self, basename):
        self.filename = basename+".qhv.meta"
        self.basename = basename
        if os.path.isfile(self.filename):
            fp = open(self.filename, "r")
            info = json.load(fp)
            fp.close()
            self.frames = info["frames"]
        else: 
            self.frames = []
    def addInfo(self, frameno, rating):
        self.frames.append({"frameno" : frameno, "rating" : rating})
        self.write()
    def getFinalDatastructure(self):
        return {"filename":self.basename, "frames":self.frames}
    def subtractFramesFromLatest(self, frames):
        self.frames[-1]["frameno"] = self.frames[-1]["frameno"] - frames
        self.write()
    def write(self):
        fp = open(self.filename, "w")
        json.dump(self.getFinalDatastructure(), fp)
        fp.close()

if __name__ == "__main__":
    filename = sys.argv[1]
    clipInfoFile = ClipInfoJsonFile(filename)
    clipInfoManager = ClipInfoManager(filename, clipInfoFile)
    ratingAdapter = RatingEventKeyAdapter(clipInfoManager)

    app = QtGui.QApplication(sys.argv)
    player = Player()
    player.addKeyListener(ratingAdapter)
    player.show()
    player.resize(640, 480)
    if os.path.isfile(filename):
        player.OpenFile(filename)
    sys.exit(app.exec_())
