class ParsedData:

    def __init__(self):
        self.buses = []
        self.loads = []
        self.generators = []
        self.branches = []
        self.bus_names = {}

        self.bus_voltage = {}
        self.bus_angle = {}
        
        self.transformers = []

def parse_raw(lines):

    data = ParsedData()

    # ---------------- BUS ----------------
    for line in lines[2:]:

        if "END OF BUS DATA" in line.upper():
            break

        parts = line.split(",")

        try:

            bus_no = int(parts[0].strip())
            ide = int(parts[3].strip())

            bus_name = parts[1].replace("'", "").strip()

            vm = float(parts[7].strip())
            va = float(parts[8].strip())

            data.buses.append(bus_no)

            data.bus_names[bus_no] = bus_name
            data.bus_voltage[bus_no] = vm
            data.bus_angle[bus_no] = va

            if not hasattr(data, "bus_types"):
                data.bus_types = {}

            data.bus_types[bus_no] = ide

        except:
            pass
    # ---------------- LOAD ----------------
    load_start = None
    load_end = None

    for i, line in enumerate(lines):

        if "END OF BUS DATA" in line.upper():
            load_start = i + 1

        if "END OF LOAD DATA" in line.upper():
            load_end = i
            break

    for line in lines[load_start:load_end]:

        parts = line.split(",")

        try:
            bus_no = int(parts[0].strip())
            data.loads.append(bus_no)

        except:
            pass

    # ---------------- GENERATOR ----------------
    gen_start = None
    gen_end = None

    for i, line in enumerate(lines):

        if "END OF LOAD DATA" in line.upper():
            gen_start = i + 1

        if "END OF GENERATOR DATA" in line.upper():
            gen_end = i
            break

    for line in lines[gen_start:gen_end]:

        parts = line.split(",")

        try:
            bus_no = int(parts[0].strip())
            data.generators.append(bus_no)

        except:
            pass

    # ---------------- BRANCH ----------------
    branch_start = None
    branch_end = None

    for i, line in enumerate(lines):

        if "END OF GENERATOR DATA" in line.upper():
            branch_start = i + 1

        if "END OF BRANCH DATA" in line.upper():
            branch_end = i
            break

    for line in lines[branch_start:branch_end]:

        parts = line.split(",")

        try:
            from_bus = int(parts[0].strip())
            to_bus = int(parts[1].strip())

            r = float(parts[3].strip())
            x = float(parts[4].strip())

            data.branches.append(
                (from_bus, to_bus, r, x)
            )
        except:
            pass
    # ---------------- TRANSFORMER ----------------
    trafo_start = None
    trafo_end = None

    for i, line in enumerate(lines):

        if "END OF BRANCH DATA" in line.upper():
            trafo_start = i + 1

        if "END OF TRANSFORMER DATA" in line.upper():
            trafo_end = i
            break

    if trafo_start and trafo_end:

        for line in lines[trafo_start:trafo_end]:

            parts = line.split(",")

            try:
                from_bus = int(parts[0].strip())
                to_bus = int(parts[1].strip())

                data.transformers.append((from_bus, to_bus))

            except:
                pass
    return data
