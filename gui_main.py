import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import matplotlib.pyplot as plt
from parser import parse_raw
class PowerFlowGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Power Flow Analyzer Engine")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()

        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)

        self.raw_file = ""
        self.original_raw = ""
        self.modified_raw = ""

        self.original_lines = []
        self.modified_lines = []
        title = tk.Label(
            root,
            text="POWER FLOW ANALYZER ENGINE",
            font=("Arial",16,"bold"),
            fg="navy"
        )

        title.pack(pady=15)

        # ---------------------------
        # STEP 1
        # ---------------------------

        tk.Label(
            root,
            text="Step 1 : Select RAW File",
            font=("Arial",11,"bold")
        ).pack()

        tk.Button(
            root,
            text="SELECT RAW FILE",
            bg="lightblue",
            width=20,
            command=self.select_raw
        ).pack(pady=5)

        self.file_label = tk.Label(
            root,
            text="No File Selected",
            fg="red"
        )

        self.file_label.pack()
        # NETWORK SUMMARY
        # --------------------------------

        tk.Label(
            root,
            text="\n📊 Network Summary",
            font=("Arial",11,"bold")
        ).pack()

        self.summary = tk.Label(

            root,

            text=
        """Total Buses        : -

        Total Branches     : -

        Total Generators   : -

        Total Loads        : -

        Total Transformers : -

        Slack Bus          : -
        """,

            justify="center",
            anchor="center",

            bg="lightyellow",

            relief="solid",

            width=36,

            height=12,

            font=("Consolas",10)

        )

        self.summary.pack(pady=5)
        # ---------------------------
        # STEP 2 + STEP 3
        # ---------------------------

        analysis_frame = tk.Frame(root)
        analysis_frame.pack(pady=10)

        # LEFT SIDE
        left_analysis = tk.Frame(analysis_frame)
        left_analysis.grid(row=0,column=0,padx=40)

        tk.Label(
            left_analysis,
            text="Step 2 : Network Analysis",
            font=("Arial",11,"bold")
        ).pack()

        tk.Button(
            left_analysis,
            text="RUN ANALYSIS",
            bg="lightgreen",
            width=20,
            command=self.run_analysis
        ).pack(pady=5)

        # RIGHT SIDE
        right_analysis = tk.Frame(analysis_frame)
        right_analysis.grid(row=0,column=1,padx=40)

        tk.Label(
            right_analysis,
            text="Network Modification",
            font=("Arial",11,"bold")
        ).pack()

        frame = tk.Frame(right_analysis)
        frame.pack(pady=5)

        tk.Label(
            frame,
            text="From Bus"
        ).grid(row=0,column=0,padx=5)

        self.from_bus = tk.Entry(
            frame,
            width=8
        )
        self.from_bus.grid(row=0,column=1)

        tk.Label(
            frame,
            text="To Bus"
        ).grid(row=0,column=2,padx=5)

        self.to_bus = tk.Entry(
            frame,
            width=8
        )
        self.to_bus.grid(row=0,column=3)

        btn_frame = tk.Frame(right_analysis)
        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="SEARCH",
            bg="lightblue",
            width=10,
            command=self.search_parallel_lines
        ).grid(row=0,column=0,padx=3)

        self.ckt_combo = ttk.Combobox(
            btn_frame,
            width=10,
            state="readonly"
        )

        self.ckt_combo.grid(
            row=0,
            column=1,
            padx=3
        )

        tk.Button(
            btn_frame,
            text="REMOVE",
            bg="orange",
            width=10,
            command=self.remove_line
        ).grid(row=0,column=2,padx=3)

        tk.Button(
            btn_frame,
            text="RESTORE",
            bg="lightgreen",
            width=10,
            command=self.restore_network
        ).grid(row=0,column=3,padx=3)

        tk.Button(
            btn_frame,
            text="SAVE RAW",
            bg="deepskyblue",
            width=10,
            command=self.save_modified_raw
        ).grid(row=0,column=4,padx=3)
        # ---------------------------
        # STEP 3
        # ---------------------------

##        tk.Label(
##            root,
##            text="\nNetwork Modification",
##            font=("Arial",11,"bold")
##        ).pack()
##
##        frame = tk.Frame(root)
##        frame.pack(pady=5)
##
##        tk.Label(
##            frame,
##            text="From Bus"
##        ).grid(row=0,column=0,padx=5)
##
##        self.from_bus = tk.Entry(
##            frame,
##            width=10
##        )
##
##        self.from_bus.grid(row=0,column=1)
##
##        tk.Label(
##            frame,
##            text="To Bus"
##        ).grid(row=0,column=2,padx=5)
##
##        self.to_bus = tk.Entry(
##            frame,
##            width=10
##        )
##
##        self.to_bus.grid(row=0,column=3)
##
##        btn_frame = tk.Frame(root)
##        btn_frame.pack(pady=5)
##
##        tk.Button(
##            btn_frame,
##            text="REMOVE LINE",
##            bg="orange",
##            width=15,
##            command=self.remove_line
##        ).grid(row=0,column=0,padx=5)
##
##        tk.Button(
##            btn_frame,
##            text="RESTORE",
##            bg="lightgreen",
##            width=15,
##            command=lambda:None
##        ).grid(row=0,column=1,padx=5)
        
        tk.Label(
            root,
            text="Status",
            font=("Arial",11,"bold")
        ).pack(pady=5)
        self.status = tk.Label(
            root,
            text="🟢 READY",
            fg="green",
            font=("Arial",10)
        )

        self.status.pack()
        tk.Button(
            root,
            text="SHOW NR JSON",
            bg="lightcyan",
            width=20,
            command=self.show_nr_json
        ).pack(pady=3)

        tk.Button(
            root,
            text="SHOW LINE LOSS",
            bg="lightcyan",
            width=20,
            command=self.show_line_loss
        ).pack(pady=3)
        tk.Button(
            root,
            text="VOLTAGE PROFILE",
            bg="skyblue",
            width=20,
            command=self.show_voltage_profile
        ).pack(pady=3)
        tk.Button(
            root,
            text="POWER LOSS SUMMARY",
            bg="khaki",
            width=20,
            command=self.show_power_loss_summary
        ).pack(pady=3)
        tk.Button(
            root,
            text="EXIT",
            bg="tomato",
            width=15,
            command=root.destroy
        ).pack(pady=25)

    # ===================================

    def select_raw(self):

        self.raw_file = filedialog.askopenfilename(
            filetypes=[("RAW Files","*.raw")]
        )

        if self.raw_file:
            self.original_raw = self.raw_file
            self.file_label.config(
                text=os.path.basename(self.raw_file),
                fg="green"
            )

            self.status.config(
                text="RAW FILE LOADED"
            )
            with open(self.raw_file, "r", encoding="utf-8", errors="ignore") as f:
                self.original_lines = f.readlines()

            self.modified_lines = self.original_lines.copy()

            data = parse_raw(self.modified_lines)
            self.update_network_summary()

            slack = "-"

            for bus, typ in data.bus_types.items():

                if typ == 3:
                    slack = bus
                    break

            self.summary.config(

            text=f"""

            Total Buses        : {len(data.buses)}

            Total Branches     : {len(data.branches)}

            Total Generators   : {len(data.generators)}

            Total Loads        : {len(data.loads)}

            Total Transformers : {len(data.transformers)}

            Slack Bus          : {slack}
            """
            )
##                self.summary.config(
##
##                    text=f"""Total Buses        : {buses}
##
##    Total Branches     : -
##
##    Total Generators   : -
##
##    Total Loads        : -
##
##    Total Transformers : -
##
##    Slack Bus          : {slack}
##    """
##                )
##
##            except:
##
##                pass
    # ===================================

    def run_analysis(self):

        if self.raw_file == "":

            messagebox.showerror(
                "Error",
                "Select RAW file first."
            )

            return

        self.status.config(
            text="Running Newton-Raphson..."
        )

        try:
            import os

            project_dir = os.path.dirname(os.path.abspath(__file__))
            temp_raw = os.path.join(
                project_dir,
                "temp_runtime.raw"
            )
            self.raw_file = temp_raw

            with open(
                temp_raw,
                "w",
                encoding="utf-8"
            ) as f:
                f.writelines(self.modified_lines)
                self.runtime_raw = temp_raw

            with open(
                temp_raw,
                "w",
                encoding="utf-8"
            ) as f:

                f.writelines(self.modified_lines)

            # ===== DELETE OLD JSON =====

            json1 = os.path.join(
                project_dir,
                "temp_runtime_line_loss.json"
            )

            json2 = os.path.join(
                project_dir,
                "temp_runtime_nr_results.json"
            )

            if os.path.exists(json1):
                os.remove(json1)

            if os.path.exists(json2):
                os.remove(json2)

            # ===========================

            subprocess.run(

                [
                    "python",
                    os.path.join(
                        project_dir,
                        "main.py"
                    ),
                    temp_raw
                ],

                cwd=project_dir
            )

            import os
            print("NR EXISTS =",
                  os.path.exists(
                      os.path.join(project_dir,
                      "temp_runtime_nr_results.json")
                  ))

            print("LOSS EXISTS =",
                  os.path.exists(
                      os.path.join(project_dir,
                      "temp_runtime_line_loss.json")
                  ))

            
            print("MAIN.PY FINISHED")
            
            self.status.config(
                text="Analysis Started ✅",
                fg="green"
            )
        except Exception as e:

            print(e)

            self.status.config(
                text=f"Analysis Failed : {e}"
            )
      
   
# =======================================
    def run_backend(self):

        project_dir = os.path.dirname(os.path.abspath(__file__))

        result = subprocess.run(
            [
                "python",
                os.path.join(project_dir, "main.py"),
                temp_raw
            ],
            cwd=project_dir,
            capture_output=True,
            text=True
        )

        print("RETURN CODE =", result.returncode)
        print("STDOUT =")
        print(result.stdout)
        print("STDERR =")
        print(result.stderr)

        import os

        print("MAIN RETURNED")
        print("NR JSON =", os.path.exists(os.path.join(project_dir, "temp_runtime_nr_results.json")))
        print("LOSS JSON =", os.path.exists(os.path.join(project_dir, "temp_runtime_line_loss.json")))

        self.status.config(
            text="Analysis Completed ✅",
            fg="green"
        )

    def update_network_summary(self):

        data = parse_raw(self.modified_lines)

        slack = "-"

        for bus, typ in data.bus_types.items():

            if typ == 3:

                slack = bus

                break

        self.summary.config(

            text=f"""

    Total Buses        : {len(data.buses)}

    Total Branches     : {len(data.branches)}

    Total Generators   : {len(data.generators)}

    Total Loads        : {len(data.loads)}

    Total Transformers : {len(data.transformers)}

    Slack Bus          : {slack}
    """
        )

    
    def show_nr_json(self):

        if self.raw_file == "":
            messagebox.showerror(
                "Error",
                "Select RAW file first."
            )
            return

        import json

        json_file = os.path.splitext(self.raw_file)[0] + "_nr_results.json"

        if not os.path.exists(json_file):
            messagebox.showerror(
                "Error",
                "NR JSON file not found."
            )
            return

        with open(json_file, "r") as f:
            data = json.load(f)

        win = tk.Toplevel(self.root)
        win.title("Newton-Raphson Results")
        win.geometry("900x600")

        
        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)
        
        
        tree = ttk.Treeview(frame)

        scroll_y = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        scroll_y.pack(
            side="right",
            fill="y"
        )

        tree.configure(
            yscrollcommand=scroll_y.set
        )

        tree.pack(
            side="left",
            fill="both",
            expand=True
        )
        

        first_key = list(data.keys())[0]

        columns = ["Bus"] + list(data[first_key].keys())

        tree["columns"] = columns
        tree["show"] = "headings"

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        for bus, values in data.items():

            row = [bus]

            for col in columns[1:]:
                row.append(values.get(col, ""))

            tree.insert("", "end", values=row)

    def show_line_loss(self):            
        

        if self.raw_file == "":
            messagebox.showerror(
                "Error",
                "Select RAW file first."
            )
            return

        import json

        json_file = os.path.splitext(
            self.raw_file
        )[0] + "_line_loss.json"

        if not os.path.exists(json_file):
            messagebox.showerror(
                "Error",
                "Line Loss JSON not found."
            )
            return

        with open(json_file, "r") as f:
            data = json.load(f)

        win = tk.Toplevel(self.root)
        win.title("Line Loss Results")
        win.geometry("700x500")

        frame = tk.Frame(win)
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame)

        scroll = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=tree.yview
        )

        scroll.pack(side="right", fill="y")

        tree.configure(yscrollcommand=scroll.set)

        tree.pack(side="left", fill="both", expand=True)

        tree["columns"] = ("From", "To", "PLOSS", "QLOSS")

        tree["show"] = "headings"

        tree.heading("From", text="From Bus")
        tree.heading("To", text="To Bus")
        tree.heading("PLOSS", text="P Loss (MW)")
        tree.heading("QLOSS", text="Q Loss (MVAR)")

        for key, value in data.items():

            fb, tb = key.split("-")

            tree.insert(
                "",
                "end",
                values=(
                    fb,
                    tb,
                    round(value["PLOSS"], 4),
                    round(value["QLOSS"], 4)
                )
            )

    def show_voltage_profile(self):

        if self.raw_file == "":

            messagebox.showerror(
                "Error",
                "Select RAW file first."
            )

            return

        import json
        import matplotlib.pyplot as plt

        json_file = os.path.splitext(
            self.raw_file
        )[0] + "_nr_results.json"

        if not os.path.exists(json_file):

            messagebox.showerror(
                "Error",
                "NR JSON file not found."
            )

            return

        with open(json_file, "r") as f:

            data = json.load(f)

        buses = []
        voltages = []

        for bus in sorted(data.keys(), key=int):

            buses.append(int(bus))
            voltages.append(data[bus]["V"])

        plt.figure(figsize=(10,5))

        plt.plot(
            buses,
            voltages,
            marker="o"
        )

        plt.title("Voltage Profile")

        plt.xlabel("Bus Number")

        plt.ylabel("Voltage (p.u.)")

        plt.grid(True)

        plt.show()
    def show_power_loss_summary(self):

        if self.raw_file == "":

            messagebox.showerror(
                "Error",
                "Select RAW file first."
            )

            return

        import json

        

        json_file = os.path.splitext(
            self.raw_file
        )[0] + "_line_loss.json"
        if not os.path.exists(json_file):

            messagebox.showerror(
                "Error",
                "Line Loss JSON not found."
            )

            return

        with open(json_file, "r") as f:

            data = json.load(f)

        total_p = 0
        total_q = 0

        max_line = ""
        max_ploss = -999999

        for line, values in data.items():

            p = values["PLOSS"]
            q = values["QLOSS"]

            total_p += p
            total_q += q

            if p > max_ploss:

                max_ploss = p
                max_line = line

        popup = tk.Toplevel(self.root)

        popup.title("Power Loss Summary")

        popup.resizable(False, False)

        self.root.update_idletasks()

        popup_width = 380
        popup_height = 340

        x = self.root.winfo_x() + 30
        y = self.root.winfo_y() + 150

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

        tk.Label(
            popup,
            text="⚡ POWER LOSS SUMMARY ⚡",
            font=("Arial",16,"bold"),
            fg="darkblue"
        ).pack(pady=10)

        summary = (
            f"Total Active Loss   : {round(total_p,4)} MW\n\n"
            f"Total Reactive Loss : {round(total_q,4)} MVAR\n\n"
            f"Highest Loss Line   : {max_line}\n\n"
            f"Highest P Loss      : {round(max_ploss,4)} MW\n\n"
            f"Total Lines         : {len(data)}"
        )

        tk.Label(
            popup,
            text=summary,
            font=("Consolas",11),
            justify="left",
            bg="lightyellow",
            relief="solid",
            padx=15,
            pady=10
        ).pack(pady=10)
        tk.Button(
            popup,
            text="CLOSE",
            bg="tomato",
            fg="white",
            width=15,
            font=("Arial",10,"bold"),
            command=popup.destroy
        ).pack(pady=10)

    def remove_line(self):

        if self.raw_file == "":

            messagebox.showerror(
                "Error",
                "Select RAW file first."
            )
            return

        fb = self.from_bus.get().strip()
        tb = self.to_bus.get().strip()
        ckt = self.ckt_combo.get().strip()

        if fb == "" or tb == "":

            messagebox.showerror(
                "Error",
                "Enter From Bus and To Bus."
            )
            return

        new_lines = []

        removed = False

        inside_branch = False

        for line in self.modified_lines:

            if "BEGIN BRANCH DATA" in line:

                inside_branch = True
                new_lines.append(line)
                continue

            if "END OF BRANCH DATA" in line:

                inside_branch = False
                new_lines.append(line)
                continue

            if not inside_branch:

                new_lines.append(line)
                continue

            parts = [x.strip() for x in line.split(",")]

            ckt_raw = (
                parts[2]
                .replace("'", "")
                .replace('"', "")
                .strip()
            )

            ckt_gui = (
                ckt
                .replace("'", "")
                .replace('"', "")
                .strip()
            )

            if (
                len(parts) >= 3
                and parts[0].strip() == fb
                and parts[1].strip() == tb
                and ckt_raw == ckt_gui
                and removed == False
            ):

                removed = True
                print("REMOVED =>", line)
                continue
                removed = True
                continue

            new_lines.append(line)

        self.modified_lines = new_lines
        self.update_network_summary()

        if removed:

            self.status.config(
                text=f"Line {fb}-{tb} removed (RAM)",
                fg="blue"
            )

            messagebox.showinfo(
                "Success",
                f"Line {fb}-{tb} removed from RAM."
            )

        else:

            messagebox.showwarning(
                "Not Found",
                "Line not found."
            )
    def restore_network(self):

        if self.original_raw == "":

            messagebox.showerror(
                "Error",
                "No original RAW file loaded."
            )
            return

        self.modified_lines = self.original_lines.copy()
        self.update_network_summary()

        self.status.config(
            text="Original Network Restored",
            fg="green"
        )

        messagebox.showinfo(
            "Restore",
            "Original network restored from RAM."
        )

    def save_modified_raw(self):

        from tkinter import filedialog

        if len(self.modified_lines) == 0:

            messagebox.showerror(
                "Error",
                "No modified network available."
            )
            return

        filename = filedialog.asksaveasfilename(
            title="Save Modified RAW",
            defaultextension=".raw",
            filetypes=[("RAW Files","*.raw")]
        )

        if filename == "":
            return

        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(self.modified_lines)

        messagebox.showinfo(
            "Saved",
            "Modified RAW file saved successfully."
        )

    def search_parallel_lines(self):

        fb = self.from_bus.get().strip()
        tb = self.to_bus.get().strip()

        if fb == "" or tb == "":

            messagebox.showerror(
                "Error",
                "Enter From Bus and To Bus."
            )

            return

        found = []

        text = ""

        for line in self.modified_lines:

            parts = [x.strip() for x in line.split(",")]

            try:

                if len(parts) >= 5 and parts[0] == fb and parts[1] == tb:

                    ckt = parts[2].replace("'", "").strip()

                    R = parts[3]

                    X = parts[4]

                    found.append(ckt)

                    text += (
                        f"{ckt:<6}"
                        f"{float(R):<15.6f}"
                        f"{float(X):<15.6f}\n"
                    )

            except:

                pass

        self.ckt_combo["values"] = found

        if len(found) > 0:

            self.ckt_combo.current(0)

            text = (
                "CKT    R(pu)         X(pu)\n"
                "-------------------------------\n"
            ) + text

            messagebox.showinfo(

                "Parallel Lines",

                text

            )

        else:

            messagebox.showinfo(

                "Search",

                "No parallel line found."

            )        

root = tk.Tk()

app = PowerFlowGUI(root)

root.mainloop()
