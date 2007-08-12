from xml.dom.minidom import parse

userPattern = {0: 1, 1: 0, 2: 1, 3: 0,
               4: 0, 5: 1, 6: 0, 7: 1}

def savePatternToXml(userPattern, patternLength, fileobject, debug=False):
    """
    Open the Hydrogen song template, write the new beats,
    and save the resulting XML into a new file.
    
    @param dict pattern
    @param int patternLength
    @param string filename
    """
    song = parse("/home/huddlej/workspace/research/sample0.h2song")
    pattern = song.getElementsByTagName("pattern")[0]
    
    instrumentValue = -1
    size = int(pattern.getElementsByTagName("size")[0].childNodes[0].nodeValue)
    increment = size / patternLength
    
    for i in range(userPattern.numgenes):
        if(i % patternLength == 0):
            """
            At the beginning of a new pattern line, increment the instrument
            and select the next note list.
            """
            instrumentValue += 1
            noteList = pattern.getElementsByTagName("noteList")[instrumentValue]
            
        if(userPattern[i] == 0):
            """
            Don't add notes for silence
            """
            continue
    
        positionValue = (i % patternLength) * increment
        note = song.createElement("note")
    
        position = song.createElement("position")
        position.appendChild(song.createTextNode(str(positionValue)))
        note.appendChild(position)
        
        velocity = song.createElement("velocity")
        velocity.appendChild(song.createTextNode("0.8"))
        note.appendChild(velocity)
        
        pan_L = song.createElement("pan_L")
        pan_L.appendChild(song.createTextNode("1"))
        note.appendChild(pan_L)
        
        pan_R = song.createElement("pan_R")
        pan_R.appendChild(song.createTextNode("1"))
        note.appendChild(pan_R)
    
        pitch = song.createElement("pitch")
        pitch.appendChild(song.createTextNode("0"))
        note.appendChild(pitch)
    
        length = song.createElement("length")
        length.appendChild(song.createTextNode("-1"))
        note.appendChild(length)
    
        instrument = song.createElement("instrument")
        instrument.appendChild(song.createTextNode(str(instrumentValue)))
        note.appendChild(instrument)
        
        noteList.appendChild(note)
        
    if debug:
        print song.toprettyxml()
    else:
        song.writexml(fileobject)
