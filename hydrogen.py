from xml.dom.minidom import parse
import Numeric

SONG_TEMPLATE_PATH = "/home/huddlej/fitbeats/song_template.h2song"

def savePatternToXml(pattern, fileobject, debug=False):
    """
    Open the Hydrogen song template, write the new beats,
    and save the resulting XML into a new file.
    
    @param PatternOrganism pattern
    @param string filename
    @param boolean debug whether if true, will print xml instead of saving to file
    """
    pattern_length = pattern.length
    instrument_length = pattern.instrument_length
    pattern_genes = pattern.genes.tolist()
    instruments = [i.sequence_number for i in pattern.instruments]
    
    song = parse(SONG_TEMPLATE_PATH)
    xml_pattern = song.getElementsByTagName("pattern")[0]
    
    size = int(xml_pattern.getElementsByTagName("size")[0].childNodes[0].nodeValue)
    increment = size / pattern_length

    for row in xrange(instrument_length):
        """
        At the beginning of a new pattern line, increment the instrument
        and select the next note list.
        """
        instrument_value = instruments[row]
        noteList = xml_pattern.getElementsByTagName("noteList")[instrument_value]

        for column in xrange(pattern_length):                
            if(pattern_genes[row][column] == 0):
                """
                Don't add notes for silence
                """
                continue
        
            position_value = column * increment
            note = song.createElement("note")
        
            position = song.createElement("position")
            position.appendChild(song.createTextNode(str(position_value)))
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
            instrument.appendChild(song.createTextNode(str(instrument_value)))
            note.appendChild(instrument)
            
            noteList.appendChild(note)
        
    if debug:
        print "Debug..."
        return song
    else:
        song.writexml(fileobject)
        
if __name__ == "__main__":
    class Instrument(object):
        def __init__(self, sequence_number):
            self.sequence_number = sequence_number

    class PatternOrganism(object):
        pass

    pattern = PatternOrganism()
    pattern.genes = Numeric.array([[1, 0, 1, 0], [0, 1, 0, 1]])
    pattern.length = Numeric.shape(pattern.genes)[1]
    pattern.instruments = [Instrument(1), Instrument(5)]
    pattern.instrument_length = len(pattern.instruments)

    fhandle = open("test.h2song", "w")
    savePatternToXml(pattern, fhandle)
    #savePatternToXml(pattern, None, True)
