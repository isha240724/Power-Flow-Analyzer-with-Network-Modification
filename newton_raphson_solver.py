import numpy as np
import sys
import os

if len(sys.argv) > 1:

    raw_file = sys.argv[1]

else:

    raw_file = input(
        "Enter RAW file path: "
    ).strip().replace('"', '')

json_file = os.path.splitext(raw_file)[0] + "_nr_results.json"
line_loss_file = os.path.splitext(raw_file)[0] + "_line_loss.json"
print("JSON WILL BE SAVED AS =", json_file)
with open(raw_file, "r", encoding="utf-8", errors="ignore") as f:
    lines = [line.strip() for line in f]

bus_info = {}

for line in lines:

    data = [x.strip() for x in line.split(",")]

    try:
        bus_no = int(data[0])

        if len(data) < 9:
            continue

        ide = int(data[3])

        vm = float(data[7])
        va = float(data[8])

        if ide == 1:
            bus_type = "PQ"
        elif ide == 2:
            bus_type = "PV"
        elif ide == 3:
            bus_type = "SLACK"
        else:
            bus_type = "UNKNOWN"

        bus_info[bus_no] = {
            "type": bus_type,
            "V": vm,
            "delta": va
        }

    except:
        pass

    if "END OF BUS DATA" in line:
        break

    try:    

        data = [x.strip() for x in line.split(",")]

        bus_no = int(data[0])

##        if bus_no <= 3:
##            print("\nBUS RAW DATA:")
##            print(data)

        ide = int(data[3])

        vm = float(data[7])
        if vm == 0:
            vm = 1.0
        va = float(data[8])

        if ide == 1:
            bus_type = "PQ"
        elif ide == 2:
            bus_type = "PV"
        elif ide == 3:
            bus_type = "SLACK"
        else:
            bus_type = "UNKNOWN"

        bus_info[bus_no] = {
            "type": bus_type,
            "V": vm,
            "delta": va
        }

    except:
        pass

PG = {}
QG = {}

gen_start = False

for line in lines:

    if "BEGIN GENERATOR DATA" in line:
        gen_start = True
        continue

    if "END OF GENERATOR DATA" in line:
        break

    if not gen_start:
        continue

    try:

        data = [x.strip() for x in line.split(",")]

        bus = int(data[0])

        PG[bus] = PG.get(bus, 0) + float(data[2])
        QG[bus] = QG.get(bus, 0) + float(data[3])

    except:
        pass

PL = {}
QL = {}

load_start = False

for line in lines:

    if "BEGIN LOAD DATA" in line:
        load_start = True
        continue

    if "END OF LOAD DATA" in line:
        break

    if not load_start:
        continue

    try:

        data = [x.strip() for x in line.split(",")]

        bus = int(data[0])

        PL[bus] = PL.get(bus, 0) + float(data[5])
        QL[bus] = QL.get(bus, 0) + float(data[6])

    except:
        pass

##print("\nBUS SUMMARY\n")
##
##for bus in sorted(bus_info):
##
##    pspec = PG.get(bus, 0) - PL.get(bus, 0)
##    qspec = QG.get(bus, 0) - QL.get(bus, 0)
##
##    print(
##        f"Bus {bus:2d} | "
##        f"{bus_info[bus]['type']:5s} | "
##        f"V={bus_info[bus]['V']:.4f} | "
##        f"d={bus_info[bus]['delta']:.4f} | "
##        f"Pspec={pspec:.4f} | "
##        f"Qspec={qspec:.4f}"
##    )

V = np.array([bus_info[b]["V"] for b in sorted(bus_info)], dtype=float)
V[V == 0] = 1.0

# Degree se radian me convert
delta = np.radians(
    np.array([bus_info[b]["delta"] for b in sorted(bus_info)], dtype=float)
)

##print("\nVoltage Vector:")
##print(V)
##
##print("\nAngle Vector:")
##print(delta)

import numpy as np

bus_numbers = sorted(bus_info.keys())

bus_map = {bus: i for i, bus in enumerate(bus_numbers)}

nbus = len(bus_numbers)

Ybus = np.zeros((nbus, nbus), dtype=complex)
branch_data = []



branch_start = False

for line in lines:

    if "BEGIN BRANCH DATA" in line:
        branch_start = True
        continue

    if "END OF BRANCH DATA" in line:
        break

    if not branch_start:
        continue

    try:

        data = [x.strip() for x in line.split(",")]

        fb = int(data[0])
        tb = int(data[1])

        R = float(data[3])
        X = float(data[4])
        B = float(data[5])
        branch_data.append(
            (fb, tb, R, X, B)
        )

        y = 1 / complex(R, X)

        i = bus_map[fb]
        j = bus_map[tb]

        Ybus[i, j] -= y
        Ybus[j, i] -= y

        Ybus[i, i] += y + 1j * (B / 2)
        Ybus[j, j] += y + 1j * (B / 2)

    except:
        pass

for k in range(len(lines)):

    if "BEGIN TRANSFORMER DATA" in lines[k]:

        t = k + 5

        while t < len(lines):

            if "END OF TRANSFORMER DATA" in lines[t]:
                break

            try:

                line1 = [x.strip() for x in lines[t].split(",")]
                line2 = [x.strip() for x in lines[t + 1].split(",")]
                line3 = [x.strip() for x in lines[t + 2].split(",")]

                fb = int(line1[0])
                tb = int(line1[1])

                R = float(line2[0])
                X = float(line2[1])

                tap = float(line3[0])

                if tap == 0:
                    tap = 1.0

                y = 1 / complex(R, X)

                i = bus_map[fb]
                j = bus_map[tb]

                Ybus[i, i] += y / (tap * tap)
                Ybus[j, j] += y

                Ybus[i, j] -= y / tap
                Ybus[j, i] -= y / tap

                t += 4

            except:
                t += 1

        break

print("\nY-BUS SIZE =", Ybus.shape)

print("\nFIRST 5 x 5 Y-BUS BLOCK\n")

##for row in Ybus[:5, :5]:
##    print(["{:.4f}{:+.4f}j".format(z.real, z.imag) for z in row])
print("\nVoltage Vector Before NR(pu):")
print(V)

print("\nBus Types:")
for b in sorted(bus_info):
    print(f"{b}, {bus_info[b]["type"]}, {bus_info[b]["V"]}pu")
print("\nSTARTING NEWTON RAPHSON\n")

slack_buses = []
pv_buses = []
pq_buses = []

for bus in sorted(bus_info):

    btype = bus_info[bus]["type"]

    if btype == "SLACK":
        slack_buses.append(bus)

    elif btype == "PV":
        pv_buses.append(bus)

    elif btype == "PQ":
        pq_buses.append(bus)
print("\n===== SYSTEM SUMMARY =====")

print("Total Buses =", nbus)
print("Slack Buses =", len(slack_buses))
print("PV Buses    =", len(pv_buses))
print("PQ Buses    =", len(pq_buses))
print("Ybus Size   =", Ybus.shape)

##print("\nSLACK BUSES :", slack_buses)
##print("PV BUSES    :", pv_buses)
##print("PQ BUSES    :", pq_buses)
##
##print("\nCounts")
##print("Slack =", len(slack_buses))
##print("PV    =", len(pv_buses))
##print("PQ    =", len(pq_buses))

##for itr in range(max_iter):
##
##    G = Ybus.real
##    B = Ybus.imag


max_iter = 20
tol = 1e-6

for itr in range(max_iter):

##    print(f"Iteration {itr+1} | Max Mismatch = {max_mismatch:.8f}")

    G = Ybus.real
    B = Ybus.imag

    Pcalc = np.zeros(nbus)
    Qcalc = np.zeros(nbus)

    for i in range(nbus):

        for j in range(nbus):

            theta = delta[i] - delta[j]

            Pcalc[i] += (
                V[i] * V[j] *
                (
                    G[i, j] * np.cos(theta)
                    +
                    B[i, j] * np.sin(theta)
                )
            )

            Qcalc[i] += (
                V[i] * V[j] *
                (
                    G[i, j] * np.sin(theta)
                    -
                    B[i, j] * np.cos(theta)
                )
            )

##    print("\nPcalc\n")
##
##    for i in range(nbus):
##        print(f"Bus {i+1:2d} : {Pcalc[i]:.6f}")

##    print("\nQcalc\n")
##
##    for i in range(nbus):
##        print(f"Bus {i+1:2d} : {Qcalc[i]:.6f}")
##
    Pspec = np.zeros(nbus)
    Qspec = np.zeros(nbus)

    for bus in bus_numbers:

        idx = bus_map[bus]

        BASE_MVA = 100.0

        Pspec[idx] = (PG.get(bus, 0) - PL.get(bus, 0)) / BASE_MVA
        Qspec[idx] = (QG.get(bus, 0) - QL.get(bus, 0)) / BASE_MVA

    dP = Pspec - Pcalc
    dQ = Qspec - Qcalc

##    print("\nDELTA P\n")
##
##    for i in range(nbus):
##        print(f"Bus {i+1:2d} : {dP[i]:.6f}")

##    print("\nDELTA Q\n")
##
##    for i in range(nbus):
##        print(f"Bus {i+1:2d} : {dQ[i]:.6f}")
##

##    slack_buses = []
##    pv_buses = []
##    pq_buses = []
##
##    for bus in sorted(bus_info):
##
##        btype = bus_info[bus]["type"]
##
##        if btype == "SLACK":
##            slack_buses.append(bus)
##
##        elif btype == "PV":
##            pv_buses.append(bus)
##
##        elif btype == "PQ":
##            pq_buses.append(bus)
##            
##    print("\nSLACK BUSES :", slack_buses)
##    print("PV BUSES    :", pv_buses)
##    print("PQ BUSES    :", pq_buses)
##
##    print("\nCounts")
##    print("Slack =", len(slack_buses))
##    print("PV    =", len(pv_buses))
##    print("PQ    =", len(pq_buses))


    angle_buses = pv_buses + pq_buses
    pq_buses_only = pq_buses

    angle_idx = [bus_map[b] for b in angle_buses]
    pq_idx = [bus_map[b] for b in pq_buses_only]

    n_angle = len(angle_idx)
    n_voltage = len(pq_idx)

##    print("\nAngle Indices =", angle_idx)
##    print("PQ Indices    =", pq_idx)
##
##    print("\n===== SYSTEM SUMMARY =====")
##
##    print("Total Buses =", nbus)
##    print("Slack Buses =", len(slack_buses))
##    print("PV Buses    =", len(pv_buses))
##    print("PQ Buses    =", len(pq_buses))
##    print("Ybus Size   =", Ybus.shape)
    angle_buses = pv_buses + pq_buses
##
##    n_angle = len(angle_buses)
##    n_voltage = len(pq_buses)
##
##    print("\nANGLE BUSES :", angle_buses)
##    print("PQ BUSES    :", pq_buses)
##
##    print("\nUnknown Angles =", n_angle)
##    print("Unknown Voltages =", n_voltage)
##
##    jacobian_size = n_angle + n_voltage
##
##    print("\nJacobian Size =",
##          jacobian_size, "x", jacobian_size)


    J1 = np.zeros((n_angle, n_angle))

    for r, i in enumerate(angle_idx):

        for c, j in enumerate(angle_idx):

            if i == j:

                J1[r, c] = -Qcalc[i] - (B[i, i] * V[i] * V[i])

            else:

                theta = delta[i] - delta[j]

                J1[r, c] = (
                    V[i] * V[j] *
                    (
                        G[i, j] * np.sin(theta)
                        -
                        B[i, j] * np.cos(theta)
                    )
                )

##    print("\nJ1 SIZE =", J1.shape)
##
##    print("\nFIRST 5 x 5 BLOCK OF J1\n")
##
##    for row in J1[:5, :5]:
##        print(["{:.4f}".format(x) for x in row])


    J2 = np.zeros((n_angle, n_voltage))

    for r, i in enumerate(angle_idx):

        for c, j in enumerate(pq_idx):

            if i == j:

                J2[r, c] = (
                    (Pcalc[i] / V[i])
                    +
                    G[i, i] * V[i]
                )

            else:

                theta = delta[i] - delta[j]

                J2[r, c] = (
                    V[i] *
                    (
                        G[i, j] * np.cos(theta)
                        +
                        B[i, j] * np.sin(theta)
                    )
                )

##    print("\nJ2 SIZE =", J2.shape)
##
##    print("\nFIRST 5 x 5 BLOCK OF J2\n")
##
##    for row in J2[:5, :5]:
##        print(["{:.4f}".format(x) for x in row])


    J3 = np.zeros((n_voltage, n_angle))

    for r, i in enumerate(pq_idx):

        for c, j in enumerate(angle_idx):

            if i == j:

                J3[r, c] = (
                    Pcalc[i]
                    -
                    G[i, i] * V[i] * V[i]
                )

            else:

                theta = delta[i] - delta[j]

                J3[r, c] = (
                    -V[i] * V[j] *
                    (
                        G[i, j] * np.cos(theta)
                        +
                        B[i, j] * np.sin(theta)
                    )
                )

##    print("\nJ3 SIZE =", J3.shape)
##
##    print("\nFIRST 5 x 5 BLOCK OF J3\n")
##
##    for row in J3[:5, :5]:
##        print(["{:.4f}".format(x) for x in row])


    J4 = np.zeros((n_voltage, n_voltage))

    for r, i in enumerate(pq_idx):

        for c, j in enumerate(pq_idx):

            if i == j:

                J4[r, c] = (
                    (Qcalc[i] / V[i])
                    -
                    B[i, i] * V[i]
                )

            else:

                theta = delta[i] - delta[j]

                J4[r, c] = (
                    V[i] *
                    (
                        G[i, j] * np.sin(theta)
                        -
                        B[i, j] * np.cos(theta)
                    )
                )

##    print("\nJ4 SIZE =", J4.shape)
##
##    print("\nFIRST 5 x 5 BLOCK OF J4\n")
##
##    for row in J4[:5, :5]:
##        print(["{:.4f}".format(x) for x in row])


    J = np.block([
        [J1, J2],
        [J3, J4]
    ])

##    print("\nFULL JACOBIAN SIZE =", J.shape)

    dP_red = []

    for idx in angle_idx:
        dP_red.append(dP[idx])

    dQ_red = []

    for idx in pq_idx:
        dQ_red.append(dQ[idx])

    mismatch = np.concatenate([
        np.array(dP_red),
        np.array(dQ_red)
    ])

    max_mismatch = max(
        np.max(np.abs(dP_red)),
        np.max(np.abs(dQ_red))
    )
    print(f"Iteration {itr+1} | Max Mismatch = {max_mismatch:.8f}pu")

##    print("\nMAX MISMATCH =", max_mismatch)

    if max_mismatch < 1e-6:
        print("\nCONVERGED SUCCESSFULLY")
        break

##    print("\nMismatch Vector Size =", mismatch.shape)
##
##    print("\n===== DEBUG =====")
##    print("Determinant =", np.linalg.det(J))
##    print("Rank =", np.linalg.matrix_rank(J))
##    print("Shape =", J.shape)
##    print("=================\n")

    # input("STOP HERE")
    print("J SHAPE =", J.shape)
    print("J RANK =", np.linalg.matrix_rank(J))
    try:

        dx = np.linalg.solve(J, mismatch)

    except Exception as e:

        print("NR SOLVER ERROR =", e)

        import sys
        sys.exit()

##    print("\nDX SIZE =", dx.shape)
##
##    print("\nFIRST 10 ELEMENTS OF DX\n")
##
##    for x in dx[:10]:
##        print(round(x, 6))
##    print("\nAngle Index Count =", len(angle_idx))
##    print("PQ Index Count =", len(pq_idx))
##
##    print("\nUnique Angle Indices =", len(set(angle_idx)))
##    print("Unique PQ Indices =", len(set(pq_idx)))

##    print("\nRank J1 =", np.linalg.matrix_rank(J1))
##    print("Rank J2 =", np.linalg.matrix_rank(J2))
##    print("Rank J3 =", np.linalg.matrix_rank(J3))
##    print("Rank J4 =", np.linalg.matrix_rank(J4))

    d_delta = dx[:len(angle_idx)]
    d_V = dx[len(angle_idx):]

    for k, idx in enumerate(angle_idx):
        delta[idx] += d_delta[k]

    for k, idx in enumerate(pq_idx):
        V[idx] += d_V[k]
##    print(f"\nIteration {itr+1} completed")

##print("\nUPDATED VOLTAGES\n")
##
##for i in range(nbus):
##    print(f"Bus {i+1:2d} : {V[i]:.6f}")

##print("\nUPDATED ANGLES (RAD)\n")
##
##for i in range(nbus):
##    print(f"Bus {i+1:2d} : {delta[i]:.6f}")
##
##print("\nMAX DELTA P =", np.max(np.abs(dP)))
##print("MAX DELTA Q =", np.max(np.abs(dQ)))
        
print("\nTOTAL BRANCHES =", len(branch_data))
print("\nFINAL VOLTAGE PROFILE\n")
print("\nPQ BUS VALIDATION\n")

for bus in pq_buses:

    i = bus_map[bus]

    Vi = V[i] * np.exp(1j * delta[i])

    Ii = 0 + 0j

    for j in range(nbus):

        Vj = V[j] * np.exp(1j * delta[j])

        Ii += Ybus[i, j] * Vj

    Si = Vi * np.conj(Ii)

    Pinj = Si.real * BASE_MVA
    Qinj = Si.imag * BASE_MVA

    print(
        f"Bus {bus} | "
        f"Pinj = {Pinj:.6f} MW | "
        f"Qinj = {Qinj:.6f} MVAR"
    )
print("\nPQ BUS POWER BALANCE CHECK\n")

for bus in pq_buses:

    idx = bus_map[bus]

    Pinj = Pcalc[idx] * BASE_MVA

    Pspec_bus = (PG.get(bus,0)-PL.get(bus,0))

    print(
        f"Bus {bus} | "
        f"Pspec={Pspec_bus:.6f} MW | "
        f"Pcalc={Pinj:.6f} MW | "
        f"Error={Pspec_bus-Pinj:.8f}"
    )    

for i in range(nbus):
    print(
        f"Bus {bus_numbers[i]:3d} | "
        f"V = {V[i]:.6f} pu | "
        f"Angle = {np.degrees(delta[i]):.6f} deg"
    )
    BASE_MVA = 100.0
import json

nr_results = {}

print("\nBUS INJECTION POWER\n")

for i in range(nbus):

    Pinj = Pcalc[i] * BASE_MVA
    Qinj = Qcalc[i] * BASE_MVA

    nr_results[str(bus_numbers[i])] = {

        "V": float(V[i]),
        "angle": float(np.degrees(delta[i])),
        "Pinj": float(Pinj),
        "Qinj": float(Qinj),
        "Pspec": float(Pspec[i] * BASE_MVA),
        "Qspec": float(Qspec[i] * BASE_MVA),
        "dP": float(dP[i] * BASE_MVA),
        "dQ": float(dQ[i] * BASE_MVA),
        "type": bus_info[bus_numbers[i]]["type"]

    }

    print(
        f"Bus {bus_numbers[i]:3d} | "
        f"Pinj = {Pinj:10.4f} MW | "
        f"Qinj = {Qinj:10.4f} MVAR"
    )
print("TOTAL NR RESULTS =", len(nr_results))

with open(json_file, "w") as f:
    json.dump(nr_results, f, indent=4)
print("JSON SAVED TO =", json_file)
print("NR Results Saved")
print("\nLINE POWER FLOWS\n")
line_loss = {}

print("\nTOTAL BRANCHES IN SOLVER =", len(branch_data))

for x in branch_data:
    print(x)

    print("\n========================")
    print("TOTAL BRANCHES =", len(branch_data))
    for b in branch_data:
        print(b)
    print("========================\n")
for fb, tb, R, X, B in branch_data:

    i = bus_map[fb]
    j = bus_map[tb]

    Vi = V[i] * np.exp(1j * delta[i])
    Vj = V[j] * np.exp(1j * delta[j])

    y = 1 / complex(R, X)

    Iij = (Vi - Vj) * y + Vi * (1j * B / 2)

    Sij = Vi * np.conj(Iij) * BASE_MVA

    Pij = Sij.real
    Qij = Sij.imag
    Iji = (Vj - Vi) * y + Vj * (1j * B / 2)

    Sji = Vj * np.conj(Iji) * BASE_MVA

    Ploss = Sij.real + Sji.real
    Qloss = Sij.imag + Sji.imag

    line_loss[f"{fb}-{tb}"] = {
        "PLOSS": float(Ploss),
        "QLOSS": float(Qloss)
    }

    print(
        f"{fb:3d} -> {tb:3d} | "
        f"P = {Pij:10.4f} MW | "
        f"Q = {Qij:10.4f} MVAR"
    )

    with open(line_loss_file, "w") as f:
        json.dump(line_loss, f, indent=4)

    print("Line Loss Saved")
    print("LINE LOSS JSON =", line_loss_file)
    print("TOTAL JSON ENTRIES =", len(line_loss))
    print("LINE LOSS JSON =", line_loss_file)
    print("TOTAL JSON ENTRIES =", len(line_loss))
