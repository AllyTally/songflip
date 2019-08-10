import sys
import random
import musiceditor as me
import io
import contextlib
import subprocess

def install(package):
    """Install a package using pip"""
    subprocess.call([sys.executable, "-m", "pip", "install", package])

cantinstall = """The modules required for SongFlip could not be installed automatically.

If you're on Windows, please reinstall Python and enable pip during installation.

If you're on Linux, please run "pip3 install pygame" and "pip3 install PySide2".
If pip3 doesn't exist, please install it through your package manager, which is most likely something like "apt install python3-pip".
"""

try:
    mdfe = ModuleNotFoundError
except NameError:
    mdfe = ImportError

try:
    with contextlib.redirect_stdout(None):
        import pygame
except (mdfe, ImportError):
    print("Pygame not installed. Installing...")
    install("pygame")
    try:
        with contextlib.redirect_stdout(None):
            import pygame
    except (mdfe, ImportError):
        print(cantinstall)
        sys.exit()

try:
    from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                                   QGridLayout, QWidget, QComboBox,
                                   QLineEdit, QFileDialog, QDialog,
                                   QPlainTextEdit)
    from PySide2.QtCore import Slot, Qt
    import PySide2.QtGui as QtGui
except (mdfe, ImportError):
    print("PySide2 not installed. Installing...")
    install("PySide2")
    try:
        from PySide2.QtWidgets import (QApplication, QLabel, QPushButton,
                                       QGridLayout, QWidget, QComboBox,
                                       QLineEdit, QFileDialog, QDialog,
                                       QPlainTextEdit)
        from PySide2.QtCore import Slot, Qt
        import PySide2.QtGui as QtGui
    except (mdfe, ImportError):
        print(cantinstall)
        sys.exit()

ver = "1.0.2"
print("SoundFlip " + ver)
fileloaded = None
playingsong = False
FREQ = 44100 
BITSIZE = -16
CHANNELS = 2
BUFFER = 1024
print("initializing sound system")
pygame.mixer.init(FREQ, BITSIZE, CHANNELS, BUFFER)
print("done")

class MainWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.replacewith = None
        self.pathtext = QLabel('"vvvvvvmusic.vvv" path')
        self.pathline = QLineEdit()
        self.choosefilebutton = QPushButton("Choose")
        self.newfilebutton = QPushButton("New")
        self.combotext = QLabel("In-game songs:")
        self.combobox = QComboBox()
        self.combobox.addItems([str(i) + ". " + x for i, x in enumerate(me.songnames)])
        self.replacetext = QLabel("Replace with:")
        self.replaceline = QLineEdit()
        self.choosereplacebutton = QPushButton("Choose")
        self.replacebutton = QPushButton("Replace Song")
        self.editsongbutton = QPushButton("Edit Song")
        self.genbutton = QPushButton("Generate Music File")
        self.extbutton = QPushButton("Extract Music")
        self.editfilebutton = QPushButton("Edit File Metadata")
        self.lastsong = QPushButton("Last Song")
        self.playsong = QPushButton("Play")
        self.nextsong = QPushButton("Next song")
        self.layout = QGridLayout()
        self.layout.addWidget(self.pathtext,0,0,1,3)         # "vvvvvvmusic.vvv" path
        self.layout.addWidget(self.pathline,1,0,1,2)         # path
        self.layout.addWidget(self.choosefilebutton,1,2)     # Choose
        self.layout.addWidget(self.newfilebutton,2,2)        # New
        self.layout.addWidget(self.combotext,2,0,1,2)        # In-game songs
        self.layout.addWidget(self.combobox,3,0,1,3)         # combobox
        self.layout.addWidget(self.replacetext,4,0,1,3)      # Replace with:
        self.layout.addWidget(self.replaceline,5,0,1,2)      # path
        self.layout.addWidget(self.choosereplacebutton,5,2)  # Choose
        self.layout.addWidget(self.replacebutton,6,0,1,3)    # Replace Song
        self.layout.addWidget(self.editsongbutton,7,0,1,3)   # Edit Song
        self.layout.addWidget(self.genbutton,8,0,1,3)        # Generate Music File
        self.layout.addWidget(self.extbutton,9,0,1,3)        # Extract Music
        self.layout.addWidget(self.editfilebutton,10,0,1,3)  # Edit File Metadata
        self.layout.addWidget(self.lastsong,11,0)            # Last Song
        self.layout.addWidget(self.playsong,11,1)            # Play Song
        self.layout.addWidget(self.nextsong,11,2)            # Next Song
        self.pathline.setEnabled(False)
        self.replaceline.setEnabled(False)
        self.replacebutton.setEnabled(False)
        self.editsongbutton.setEnabled(False)
        self.genbutton.setEnabled(False)
        self.extbutton.setEnabled(False)
        self.editfilebutton.setEnabled(False)
        self.lastsong.setEnabled(False)
        self.playsong.setEnabled(False)
        self.nextsong.setEnabled(False)
        self.layout.setColumnStretch(1,1)
        self.setLayout(self.layout)
        self.choosefilebutton.clicked.connect(self.choosefile)
        self.newfilebutton.clicked.connect(self.newfile)
        self.choosereplacebutton.clicked.connect(self.choosesongfile)
        self.replacebutton.clicked.connect(self.replacesong)
        self.editsongbutton.clicked.connect(self.editsong)
        self.genbutton.clicked.connect(self.genmusic)
        self.extbutton.clicked.connect(self.extractmusic)
        self.editfilebutton.clicked.connect(self.editfilemeta)
        self.lastsong.clicked.connect(self.indexback)
        self.playsong.clicked.connect(self.indexplay)
        self.nextsong.clicked.connect(self.indexforwards)

    @Slot()
    def choosefile(self):
        global fileloaded
        fname = QFileDialog.getOpenFileName(self, 'Open file', './',"VVVVVV Music files (*.vvv)")
        if not fname[0]:
            return
        self.pathline.setText(fname[0])
        fileloaded = me.load_music(fname[0])
        for x,i in enumerate(fileloaded.songs):
            self.combobox.setItemText(x,str(x) + ". " + i.name)
        self.enablemainbuttons()

    @Slot()
    def newfile(self):
        global fileloaded
        self.pathline.setText("new")
        fileloaded = me.load_music(None)
        for x in range(len(fileloaded.songs)):
            self.combobox.setItemText(x,str(x) + ". <blank>")
        self.enablemainbuttons()

    def enablemainbuttons(self):
        self.replacebutton.setEnabled(True)
        self.editsongbutton.setEnabled(True)
        self.genbutton.setEnabled(True)
        self.extbutton.setEnabled(True)
        self.editfilebutton.setEnabled(True)
        self.lastsong.setEnabled(True)
        self.playsong.setEnabled(True)
        self.nextsong.setEnabled(True)

    @Slot()
    def choosesongfile(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', './',"OGG files (*.ogg)")
        if not fname[0]:
            return
        self.replacewith = fname[0]
        self.replaceline.setText(fname[0])

    @Slot()
    def replacesong(self):
        if self.replacewith == None:
            return
        self.loadedsong = me.song_from_file(self.replacewith)
        self.editingsong = False
        self.editmeta()

    @Slot()
    def editsong(self):
        self.editingsong = True
        self.editmeta()

    def editmeta(self):
        self.childwindow = ChildWindow(self)
        self.childwindow.setModal(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.childwindow.setWindowIcon(icon)
        self.childwindow.setWindowTitle("Metadata Editor")
        self.childwindow.show()

    def editfilemeta(self):
        self.childwindow = FileChildWindow(self)
        self.childwindow.setModal(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.childwindow.setWindowIcon(icon)
        self.childwindow.setWindowTitle("File Metadata Editor")
        self.childwindow.show()

    def finishreplace(self):
        self.loadedsong.name = self.childwindow.songnameline.text()
        self.loadedsong.filename = self.childwindow.filenameline.text()
        self.loadedsong.notes = self.childwindow.notesarea.toPlainText()
        self.childwindow.close()
        fileloaded.replace(self.combobox.currentIndex(),self.loadedsong)
        self.combobox.setItemText(self.combobox.currentIndex(),str(self.combobox.currentIndex()) + ". " + self.loadedsong.name)

    def finishedit(self):
        fileloaded.get_song(self.combobox.currentIndex()).name = self.childwindow.songnameline.text()
        fileloaded.get_song(self.combobox.currentIndex()).filename = self.childwindow.filenameline.text()
        fileloaded.get_song(self.combobox.currentIndex()).notes = self.childwindow.notesarea.toPlainText()
        self.childwindow.close()
        fileloaded.replace(self.combobox.currentIndex(),fileloaded.get_song(self.combobox.currentIndex()))
        self.combobox.setItemText(self.combobox.currentIndex(),str(self.combobox.currentIndex()) + ". " + fileloaded.get_song(self.combobox.currentIndex()).name)

    def finishfileedit(self):
        fileloaded.album = self.childwindow.albumline.text()
        fileloaded.artist = self.childwindow.artistline.text()
        fileloaded.notes = self.childwindow.notesarea.toPlainText()
        self.childwindow.close()

    @Slot()
    def genmusic(self):
        global fileloaded
        fname = QFileDialog.getSaveFileName(self, 'Save file', './',"VVVVVV Music files (*.vvv)")
        if not fname[0]:
            return
        fileloaded.save(fname[0])

    @Slot()
    def extractmusic(self):
        fileloaded.extract(path="extracted/")

    @Slot()
    def indexplay(self):
        global playingsong
        global fileloaded
        playingsongindex = self.combobox.currentIndex()
        if not fileloaded:
            return
        if fileloaded.songs[playingsongindex].data == b'\x00':
            return
        if not playingsong:
            pygame.mixer.music.load(io.BytesIO(fileloaded.songs[playingsongindex].data))
            pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.stop()
        playingsong = not playingsong


    @Slot()
    def indexback(self):
        global playingsong
        playingsongindex = self.combobox.currentIndex()
        playingsongindex -= 1
        if playingsongindex < 0:
            playingsongindex = 15
        self.combobox.setCurrentIndex(playingsongindex)
        if playingsong:
            pygame.mixer.music.stop()
            playingsong = False

    @Slot()
    def indexforwards(self):
        global playingsong
        playingsongindex = self.combobox.currentIndex()
        playingsongindex += 1
        if playingsongindex > 15:
            playingsongindex = 0
        self.combobox.setCurrentIndex(playingsongindex)
        if playingsong:
            pygame.mixer.music.stop()
            playingsong = False


class ChildWindow(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        global fileloaded
        if parent.editingsong:
            self.song = fileloaded.get_song(parent.combobox.currentIndex())
        else:
            self.song = parent.loadedsong
        self.replacewith = None
        self.songname = QLabel('Song name:')
        self.songnameline = QLineEdit()
        self.songnameline.setText(self.song.name)
        self.filename = QLabel('File name:')
        self.filenameline = QLineEdit()
        self.filenameline.setText(self.song.filename)
        self.notes = QLabel('Notes:')
        self.notesarea = QPlainTextEdit()
        self.notesarea.setPlainText(self.song.notes)
        self.donebutton = QPushButton("Done")
        self.layout = QGridLayout()
        self.layout.addWidget(self.songname,0,0)
        self.layout.addWidget(self.songnameline,0,1)
        self.layout.addWidget(self.filename,1,0)
        self.layout.addWidget(self.filenameline,1,1)
        self.layout.addWidget(self.notes,2,0)
        self.layout.addWidget(self.notesarea,2,1)
        self.layout.addWidget(self.donebutton,3,0,1,2)
        self.setLayout(self.layout)
        if parent.editingsong:
            self.donebutton.clicked.connect(parent.finishedit)
        else:
            self.donebutton.clicked.connect(parent.finishreplace)

class FileChildWindow(QDialog):
    def __init__(self, parent):
        QDialog.__init__(self)
        global fileloaded
        self.album = QLabel('Album name:')
        self.albumline = QLineEdit()
        self.albumline.setText(fileloaded.album)
        self.artist = QLabel('Album artist:')
        self.artistline = QLineEdit()
        self.artistline.setText(fileloaded.artist)
        self.notes = QLabel('Album notes:')
        self.notesarea = QPlainTextEdit()
        self.notesarea.setPlainText(fileloaded.notes)
        self.donebutton = QPushButton("Done")
        self.layout = QGridLayout()
        self.layout.addWidget(self.album,0,0)
        self.layout.addWidget(self.albumline,0,1)
        self.layout.addWidget(self.artist,1,0)
        self.layout.addWidget(self.artistline,1,1)
        self.layout.addWidget(self.notes,2,0)
        self.layout.addWidget(self.notesarea,2,1)
        self.layout.addWidget(self.donebutton,3,0,1,2)
        self.setLayout(self.layout)
        self.donebutton.clicked.connect(parent.finishfileedit)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = MainWindow()
    icon = QtGui.QIcon()
    icon.addPixmap(QtGui.QPixmap("icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    widget.setWindowIcon(icon)
    widget.setWindowTitle("SongFlip")
    widget.resize(360,320)
    widget.show()

    sys.exit(app.exec_())