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
        self.currentFileNo = -1

        self.ratingAdapter = RatingEventKeyAdapter()
        self.ratingAdapter.setPlayer(self)
        self.setKeyListener(self.ratingAdapter)

    def keyPressEvent(self, e):
        if self.keyListener == None:
            return

        mediaTime = self.mediaplayer.get_time()
        if mediaTime < 0:
            return

        # Calculate the frame number from the framerate and time.
        framerate = self.getFrameRate()
        frameNo = int(mediaTime * framerate / 1000)
        self.keyListener.keyPressed(e.text(), frameNo, framerate)

    def getFrameRate(self):
        """Extracts the information to calculate a frame rate from the media."""
        if self.frameRate < 0:
            tracks = self.media.tracks_get()
            num = tracks[0][0][0].u.video[0].frame_rate_num
            den = tracks[0][0][0].u.video[0].frame_rate_den
            if int(den) > 0:
                self.frameRate = int(num)/int(den)
        return self.frameRate 

    def setKeyListener(self, keyListener):
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

        self.prevbutton = QtGui.QPushButton("P&revious video")
        self.hbuttonbox.addWidget(self.prevbutton)
        self.connect(self.prevbutton, QtCore.SIGNAL("clicked()"),
                     self.prevVideo)

        self.playbutton = QtGui.QPushButton("&Play")
        self.hbuttonbox.addWidget(self.playbutton)
        self.connect(self.playbutton, QtCore.SIGNAL("clicked()"),
                     self.PlayPause)

        self.stopbutton = QtGui.QPushButton("&Stop")
        self.hbuttonbox.addWidget(self.stopbutton)
        self.connect(self.stopbutton, QtCore.SIGNAL("clicked()"),
                     self.Stop)

        self.nextbutton = QtGui.QPushButton("&Next video")
        self.hbuttonbox.addWidget(self.nextbutton)
        self.connect(self.nextbutton, QtCore.SIGNAL("clicked()"),
                     self.nextVideo)

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
        self.connect(open, QtCore.SIGNAL("triggered()"), self.OpenFiles)
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

    def PlayPause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText("&Play")
            self.isPaused = True
        else:
            if self.mediaplayer.play() == -1:
                self.OpenFile()
                return
            self.mediaplayer.play()
            self.playbutton.setText("&Pause")
            self.timer.start()
            self.isPaused = False

    def Stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setText("&Play")

    def updateEnablements(self):
        if self.currentFileNo + 1 >= len(self.filenames):
            self.nextbutton.setEnabled(False)
        else:
            self.nextbutton.setEnabled(True)

        if self.currentFileNo - 1 < 0:
            self.prevbutton.setEnabled(False)
        else:
            self.prevbutton.setEnabled(True)

    def nextVideo(self):
        self.currentFileNo = self.currentFileNo + 1
        self.updateEnablements()
        self.setFile(self.filenames[self.currentFileNo])

    def prevVideo(self):
        self.currentFileNo = self.currentFileNo - 1
        self.updateEnablements()
        if self.currentFileNo < 0:
            self.currentFileNo = len(self.filenames) - 1
        self.setFile(self.filenames[self.currentFileNo])

    def OpenFiles(self):
        """Open a media file in a MediaPlayer
        """
        filenames = QtGui.QFileDialog.getOpenFileNames(self, "Open Files", os.path.expanduser('~'), "Videos (*.MP4 *.MOV *.AVI *.MTS *.OGV *.mp4 *.mov *.avi *.mts *.ogv);;All (*.*)")
        self.setFiles(filenames)

    def setFiles(self, filenames):
        self.filenames = filenames
        if self.filenames == None or len(self.filenames) == 0:
            return
        self.nextVideo()
        
    def setFile(self, filename):
        # create the media
        if sys.version < '3':
            filename = unicode(filename)
        self.media = self.instance.media_new(filename)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)

        # setup keylisteners
        clipInfoFile = ClipInfoJsonFile(filename)
        self.ratingAdapter.setReceiver(clipInfoFile)
       
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

    def moveRelative(self, seconds):
        # Get media time in ms.
        mediaTime = self.mediaplayer.get_time()
        if mediaTime < 0:
            return
        newTime = int(mediaTime + (seconds * 1000))
        self.mediaplayer.set_time(newTime)
        self.updateUI()

    def setPosition(self, position):
        """Set the position of the video but not the slider.
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
    """Receives keyboard events and translates them to the proper method calls."""
    def __init__(self, receiver = None):
        self.receiver = receiver
        self.player = None

    def setReceiver(self, receiver):
        if self.receiver != None:
            self.receiver.close()
        self.receiver = receiver
    def setPlayer(self, player):
        self.player = player

    def keyPressed(self, key, frameno, framerate):
        """Called when a key is pressed.
        - key the ASCII representation of the key that is called.
        - frameno the framenumber the key was pressed on."""
        if self.receiver == None:
            return

        self.receiver.setFrameRate(framerate)

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
        elif key == "l":
            self.receiver.subtractFramesFromLatest(12)
        elif key == "m":
            self.receiver.moveRating(frameno)
        elif key == "b":
            if self.player != None:
                self.player.moveRelative(-3)
        elif key == "f":
            if self.player != None:
                self.player.moveRelative(3)
        elif key == "d":
            self.receiver.deleteLatest()
        # Ignore other key events.

class ClipInfoJsonFile:
    def __init__(self, basename):
        self.filename = basename+".rcut"
        self.basename = basename
        if os.path.isfile(self.filename):
            fp = open(self.filename, "r")
            info = json.load(fp)
            fp.close()
            self.frames = info["frames"]
        else: 
            self.frames = []
    def setRating(self, frameno, rating):
        self.frames.append({"frameno" : frameno, "rating" : rating})
        self.write()
    def setFrameRate(self, framerate):
        self.framerate = framerate
    def close(self):
        """Makes it possible for future implementations to save and clean up when info file is changed."""
        pass
    def getFinalDatastructure(self):
        return {"filename":self.basename, "framerate":str(self.framerate), "frames":self.frames}
    def subtractFramesFromLatest(self, frames):
        self.frames[-1]["frameno"] = self.frames[-1]["frameno"] - frames
        self.write()
    def deleteLatest(self):
        del self.frames[-1]
        self.write()
    def moveRating(self, frameno):
        self.frames[-1]["frameno"] = frameno
        self.write()
    def write(self):
        fp = open(self.filename, "w")
        json.dump(self.getFinalDatastructure(), fp)
        fp.close()

if __name__ == "__main__":
    filenames = []
    if len(sys.argv) > 1:
        filenames = sys.argv[1:]

    app = QtGui.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(640, 480)
    player.setFiles(filenames)
    sys.exit(app.exec_())
