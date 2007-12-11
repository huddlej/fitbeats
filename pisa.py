"""Lower level method to support the PISA variator interface."""

class CorruptedDataException(Exception):
    pass

def read_data_file(filename):
    f = open(filename)
    try:
        lines = f.readlines()
        if len(lines) <= 2:
            raise CorruptedDataException("File %s is empty or improperly \
                                          formatted." % filename)

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
            if len(values) > 0:
                index = values.pop(0)
                data[index] = values or None

        if len(data) == 0:
            raise CorruptedDataException("Configuraton file %s is empty." % filename)
        return data
    finally:
        f.close()

def read_state_file(filename):
    f = open(filename)
    try:
        state = f.readline()
        if len(state) == 0:
            raise CorruptedDataException("State file %s is empty." % filename)
        try:
            state = int(state)
            return state
        except ValueError:
            raise CorruptedDataException("State file %s contains invalid state data." % filename)
    finally:
        f.close()

def write_file(filename, data):
    f = open(filename, "w")
    try:
        f.write(str(data))
    finally:
        f.close()
