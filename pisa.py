"""File management methods."""

class CorruptedDataException(Exception):
    pass

def read_data_file(filename):
    f = open(filename)
    try:
        lines = f.readlines()
        if len(lines) <= 2:
            raise CorruptedDataException("File %s is empty or improperly formatted." % filename)

        expected_number_of_elements = int(lines.pop(0))
        end_of_file = lines.pop()
        actual_number_of_elements = len(lines)
        if actual_number_of_elements != expected_number_of_elements or end_of_file != "END":
            raise CorruptedDataException("File %s does not contain the expected number of values.  Expected %s values, found %s." % (filename, expected_number_of_elements, actual_number_of_elements))

        data = {}
        for line in lines:
            values = line.split()
            index = int(values.pop(0))
            data[index] = values or None
        return data
    finally:
        print "Finally!"
        f.close()

def read_configuration_file(filename):
    f = open(filename)
    try:
        lines = f.readlines()
        if len(lines) == 0:
            raise CorruptedDataException("File %s is empty." % filename)

        data = {}
        for line in lines:
            values = line.split()
            index = values.pop(0)
            data[index] = values or None
        return data
    finally:
        f.close()

def read_state_file(filename):
    f = open(filename)
    try:
        state = f.readline()
        if len(state) == 0:
            raise CorruptedDataException("State file %s is empty." % filename)
        return int(state)
    finally:
        f.close()
