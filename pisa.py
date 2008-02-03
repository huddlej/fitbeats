"""Lower level method to support the PISA variator interface."""

files = {
         "configuration": "cfg", 
         "initial_population": "ini",
         "archive": "arc",
         "sample": "sel", 
         "offspring": "var",
         "state": "sta"
         }

STATE_0 = 0
STATE_1 = 1
STATE_2 = 2
STATE_3 = 3
STATE_4 = 4
STATE_5 = 5
STATE_6 = 6

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

        data = None
        for line in lines:
            values = line.split()
            index = int(values.pop(0))
            if len(values) == 0:
                # No more values means this is an index file.
                if data is None:
                    data = []
                try:
                    value = int(index)
                except:
                    value = float(index)
                data.append(value)
            else:
                # More values means this is a fitness value file.
                if data is None:
                    data = {}
                try:
                    values = map(int, values)
                except:
                    values = map(float, values)
                data[index] = values
        f.close()
        f = open(filename, "w")
        f.write("0")

        return data
    finally:
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
                index = values[0]
                try:
                    value = int(values[1])
                except:
                    value = float(values[1])
                data[index] = value

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

def write_file(filename, data, dimensions=0):
    f = open(filename, "w")
    try:
        if isinstance(data, list) or isinstance(data, tuple):
            elements = len(data) * (dimensions + 1)
            f.write("%i\n" % elements)
            for value in data:
                if isinstance(value, list) or isinstance(value, tuple):
                    f.write(" ".join(map(str, value)))
                else:
                    f.write(str(value))
                f.write("\n")
            f.write("END")
        elif isinstance(data, dict):
            elements = len(data) * (dimensions + 1)
            f.write("%i\n" % elements)
            for key, values in data.items():
                line = [key] + list(values)
                f.write(" ".join(map(str, line)))
                f.write("\n")
            f.write("END")
        else:
            f.write(str(data))
            f.write("\n")
    finally:
        f.close()
