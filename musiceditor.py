import os
import math
import time
import ntpath
import argparse

metaver = [1,0]

songnames = [
    "Level Complete!",
    "Pushing Onwards",
    "Positive Force",
    "Potential For Anything",
    "Passion For Exploring",
    "Pause",
    "Presenting VVVVVV",
    "Plenary",
    "Predestined Fate",
    "ecroF evitisoP",
    "Popular Potpourri",
    "Pipe Dream",
    "Pressure Cooker",
    "Paced Energy",
    "Piercing The Sky",
    "Predestined Fate Remix"
]

files = [
    "0levelcomplete",
    "1pushingonwards",
    "2positiveforce",
    "3potentialforanything",
    "4passionforexploring",
    "5intermission",
    "6presentingvvvvvv",
    "7gamecomplete",
    "8predestinedfate",
    "9positiveforcereversed",
    "10popularpotpourri",
    "11pipedream",
    "12pressurecooker",
    "13pacedenergy",
    "14piercingthesky",
    "predestinedfatefinallevel",
]

def createHeaderSector(sid,meta):
    """Creates a header section for the start of music files."""
    if sid == None:
        a = '\x00'*48
        filelength = b'\x00'*4
    else:
        a = "data/music/" + files[sid.id] + ".ogg"
        filelength = len(sid.data).to_bytes(4, byteorder='little')
    builder  = b''
    builder += a.ljust(48,'\x00').encode()
    if meta == None:
        builder += b'\x00'*4
    else:
        builder += meta.to_bytes(4, byteorder='little')
    builder += filelength
    if sid == None:
        builder += b'\x00'*4
    else:
        builder += b'\x01'*4
    return builder

def createSizeHeader(filemeta,mdlength):
    """Creates the last header section, but this time to support metadata."""
    builder  = b''
    builder += b'\x00' * 48                                    # filename
    builder += filemeta.to_bytes(4, byteorder='little')        # start
    builder += mdlength.to_bytes(4, byteorder='little')        # length
    builder += b'\x00' * 4                                     # valid
    return builder

def song_from_bytes(bytes,filename=False):
    """Creates a song object from bytes."""
    return Song(bytes,-1,filename.title() if filename else "",filename + ".ogg" if filename else "","")

def song_from_file(filename):
    """Creates a song object from a filename. Internally calls `song_from_bytes`."""
    with open(filename, "rb") as f:
        return song_from_bytes(f.read(),filename=os.path.splitext(ntpath.basename(filename))[0])

class Song():
    """A song object. This represents one of the 16 songs in a VVVVVV music file."""
    def __init__(self,data,id,name,filename,notes):
        self.data = data
        self.id = id
        self.name = name
        self.filename = filename
        self.notes = notes
    def save(self,filename):
        """Save the song to a file."""
        try:
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        except FileNotFoundError:
            filename = "./" + filename
        with open(filename + ".ogg", "wb") as outfile:
            outfile.write(self.data)
    def generate_meta(self):
        """Generates song metadata from the data it contains."""
        builder  = b''
        builder += self.name.encode()
        builder += b'\x00'
        builder += self.filename.encode()
        builder += b'\x00'
        builder += self.notes.encode()
        builder += b'\x00'
        return builder

class MusicFile():
    """A music object. This represents a VVVVVV music file."""
    def __init__(self,songdata,timestamp,album,artist,notes,validmeta,songmeta,major,minor):
        self.songs = []
        self.timestamp = timestamp
        self.album = album
        self.artist = artist
        self.notes = notes
        self.validmeta = validmeta
        self.metaver = [major,minor]
        if songmeta == None:
            for x,i in enumerate(songdata):
                self.songs.append(Song(i,x,songnames[x],files[x] + ".ogg",""))
        elif songmeta == "empty":
            for x,i in enumerate(songdata):
                self.songs.append(Song(i,x,"","",""))
        else:
            for x,i in enumerate(songdata):
                if i != b'\x00':
                    self.songs.append(Song(i,x,songmeta[x][0],songmeta[x][1],songmeta[x][2]))
                else:
                    self.songs.append(Song(i,x,"","",""))
    def get_song(self,song):
        """Get a song from the array. This is the same as `self.songs[index]`."""
        if song in range(0,15):
            return self.songs[song]
        raise IndexError("song must be 0 - 15")
    def extract(self,filenames=files,path=None):
        """This extracts all songs to a folder. This is the same as looping through all songs and running `Song.save()`."""
        if path != None:
            path = path + "/"
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        for x,i in enumerate(self.songs):
            i.save((path if path else "") + filenames[x])
        return
    def replace(self,id,song):
        """Replace a song in the music file."""
        self.songs[id] = song
        self.songs[id].id = id
    def save(self,filename):
        """This generates the vvvvvvmusic.vvv file."""
        builder = b''
        metabuilder = b''
        for i in range(0,16):
            songmeta = self.songs[i].generate_meta()
            builder += createHeaderSector(self.songs[i],len(songmeta))
            metabuilder += songmeta
        for i in range(0,111):
            builder += createHeaderSector(None,None)
        generatedmeta = self.generate_meta()
        builder += createSizeHeader(len(generatedmeta),len(generatedmeta) + len(metabuilder))
        for i in self.songs:
            builder += i.data
        builder += generatedmeta
        builder += metabuilder
        with open(filename, "wb") as outfile:
            outfile.write(builder)
    def generate_meta(self):
        """This generates file metadata."""
        self.validmeta = True
        builder  = b''
        builder += metaver[1].to_bytes(1, byteorder='little')
        builder += metaver[0].to_bytes(1, byteorder='little')
        builder += b"\x00\x00"
        builder += math.floor(time.time()).to_bytes(4, byteorder='little')
        builder += self.album.encode()
        builder += b"\x00"
        builder += self.artist.encode()
        builder += b"\x00"
        builder += self.notes.encode()
        builder += b"\x00"
        return builder

def load_music(filename):
    """This function creates a MusicFile object from a filename."""
    songdata = []
    if not filename:
        for i in range(0,16):
            songdata.append(b'\x00')
        return MusicFile(songdata,"","","","",False,"empty",metaver[0],metaver[1])
    with open(filename, "rb") as f:
        a = f.read()
    lengthlist = []
    for i in range(0,16):
        lengthlist.append(int.from_bytes(a[52+(i*60):56+(i*60)],'little'))
    buildinglength = 0
    for i in lengthlist:
        extractedsong = a[7680+buildinglength:7680+buildinglength+i]
        songdata.append(extractedsong)
        buildinglength += i
    exminorver = int.from_bytes(a[7680+buildinglength:7680+buildinglength+1],'little')
    exmajorver = int.from_bytes(a[7680+buildinglength+1:7680+buildinglength+2],'little')
    buildinglength += 4
    filemetalength = int.from_bytes(a[7668:7672],'little')
    allmetalength = int.from_bytes(a[7672:7676],'little')
    metalengthlist = []
    for i in range(0,16):
        metalengthlist.append(int.from_bytes(a[48+(i*60):52+(i*60)],'little'))
    addtogether = filemetalength
    for i in metalengthlist:
        addtogether += i
    validmeta = addtogether == allmetalength
    if validmeta:
        extractedfilemeta = a[7680+buildinglength:7680+buildinglength+filemetalength-4]
        splitmeta = extractedfilemeta[4:].split(b'\x00')
        timestamp = int.from_bytes(extractedfilemeta[:4],'little')
        metadata = [None]*16
        metabuildinglength = 0
        buildinglength -= 4
        for aaa,i in enumerate(metalengthlist):
            extractedmeta = a[7680+buildinglength+filemetalength+metabuildinglength:7680+buildinglength+filemetalength+metabuildinglength+i]
            metadata[aaa] = [x.decode(errors='ignore') for x in extractedmeta.split(b'\x00')][:-1]
            metabuildinglength += i
        return MusicFile(songdata,timestamp,splitmeta[0].decode(),splitmeta[1].decode(),splitmeta[2].decode(),True,metadata,exmajorver,exminorver)
    return MusicFile(songdata,0,"","","",False,None,0,0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Edits VVVVVV music files.')
    parser.add_argument('-i', '--input', metavar='input', type=str, help='the music file to edit. empty for a new file')
    parser.add_argument('-r', '--replace', metavar=('song','filename'), nargs=2, type=str, help='replace a song with a file')
    parser.add_argument('-t', '--time', action='store_true', help='get the time the file was created')
    parser.add_argument('-n', '--name', metavar='name', nargs='?', type=str, help='edit the files name metadata, missing argument prints it', default=False)
    parser.add_argument('-a', '--artist', metavar='artist', nargs='?', type=str, help='edit the files artist metadata, missing argument prints it', default=False)
    parser.add_argument('-no', '--notes', metavar='notes', nargs='?', type=str, help='edit the files notes metadata, missing argument prints it', default=False)
    parser.add_argument('-sn', '--songname', metavar=('song','name'), nargs='+', type=str, help='edit a songs name metadata, missing second argument prints it')
    parser.add_argument('-x', '--extract', metavar=('song','filename'), nargs=2, type=str, help='extract a song')
    parser.add_argument('-X', '--extractall', metavar='path', type=str, help='extract all songs')
    parser.add_argument('-ss', '--songsize', metavar='song', type=int, help='get a songs length')
    parser.add_argument('-sf', '--songfile', metavar=('song','filename'), nargs='+', type=str, help='edit a songs filename metadata, missing second argument prints it')
    parser.add_argument('-sno', '--songnotes', metavar=('song','notes'), nargs='+', type=str, help='edit a songs notes metadata, missing second argument prints it')
    parser.add_argument('-o', '--output', metavar='output', type=str, help='what to save the file as')
    args = parser.parse_args()
    musicfile = load_music(args.input)
    if args.name != False:
        if args.name != None:
            musicfile.album = args.name
        else:
            print(musicfile.album)
    if args.artist != False:
        if args.artist != None:
            musicfile.artist = args.artist
        else:
            print(musicfile.artist)
    if args.notes != False:
        if args.notes != None:
            musicfile.notes = args.notes
        else:
            print(musicfile.notes)
    if args.time:
        print(musicfile.timestamp)
    if args.extract:
        musicfile.songs[int(args.extract[0])].save(filename=args.extract[1])
    if args.extractall:
        musicfile.extract(path=args.extractall)
    if args.songname != None:
        if len(args.songname) != 1:
            musicfile.songs[int(args.songname[0])].name = args.songname[1]
        else:
            print(musicfile.songs[int(args.songname[0])].name)
    if args.songfile != None:
        if len(args.songfile) != 1:
            musicfile.songs[int(args.songfile[0])].filename = args.songfile[1]
        else:
            print(musicfile.songs[int(args.songfile[0])].filename)
    if args.songnotes != None:
        if len(args.songnotes) != 1:
            musicfile.songs[int(args.songnotes[0])].notes = args.songnotes[1]
        else:
            print(musicfile.songs[int(args.songnotes[0])].notes)
    if args.songsize != None:
        print(len(musicfile.songs[args.songsize].data))
    if args.output != None:
        musicfile.save(args.output)