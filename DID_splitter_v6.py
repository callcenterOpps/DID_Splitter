import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import re

# ─────────────────────────────────────────────────────────────
# Built-in area code → state mapping (350 codes, 53 states)
# ─────────────────────────────────────────────────────────────
AREACODE_STATE = {
    "201":"NJ","907":"AK","205":"AL","251":"AL","256":"AL","334":"AL","659":"AL","938":"AL",
    "479":"AR","501":"AR","870":"AR","480":"AZ","520":"AZ","602":"AZ","623":"AZ","928":"AZ",
    "209":"CA","213":"CA","279":"CA","310":"CA","323":"CA","341":"CA","369":"CA","408":"CA",
    "415":"CA","424":"CA","442":"CA","510":"CA","530":"CA","559":"CA","562":"CA","619":"CA",
    "626":"CA","627":"CA","628":"CA","650":"CA","657":"CA","661":"CA","669":"CA","707":"CA",
    "714":"CA","747":"CA","760":"CA","764":"CA","805":"CA","818":"CA","831":"CA","858":"CA",
    "909":"CA","916":"CA","925":"CA","935":"CA","949":"CA","951":"CA","840":"CA","738":"CA",
    "820":"CA","958":"CA","303":"CO","719":"CO","720":"CO","970":"CO","983":"CO",
    "203":"CT","475":"CT","860":"CT","959":"CT","202":"DC","302":"DE",
    "239":"FL","305":"FL","321":"FL","352":"FL","386":"FL","407":"FL","561":"FL","689":"FL",
    "727":"FL","754":"FL","772":"FL","786":"FL","813":"FL","850":"FL","863":"FL","904":"FL",
    "927":"FL","941":"FL","954":"FL","448":"FL","656":"FL",
    "229":"GA","404":"GA","470":"GA","478":"GA","678":"GA","706":"GA","762":"GA","770":"GA","912":"GA",
    "808":"HI","319":"IA","515":"IA","563":"IA","712":"IA","641":"IA","208":"ID","986":"ID",
    "217":"IL","224":"IL","309":"IL","312":"IL","331":"IL","464":"IL","618":"IL","630":"IL",
    "708":"IL","773":"IL","779":"IL","815":"IL","847":"IL","872":"IL","447":"IL",
    "219":"IN","260":"IN","317":"IN","463":"IN","574":"IN","765":"IN","812":"IN","930":"IN",
    "316":"KS","620":"KS","785":"KS","913":"KS",
    "270":"KY","502":"KY","606":"KY","859":"KY","364":"KY",
    "225":"LA","318":"LA","337":"LA","504":"LA","985":"LA",
    "339":"MA","351":"MA","413":"MA","508":"MA","617":"MA","774":"MA","781":"MA","857":"MA","978":"MA",
    "240":"MD","301":"MD","410":"MD","443":"MD","667":"MD","207":"ME",
    "231":"MI","248":"MI","269":"MI","278":"MI","313":"MI","517":"MI","586":"MI","616":"MI",
    "679":"MI","734":"MI","810":"MI","906":"MI","947":"MI","989":"MI",
    "218":"MN","320":"MN","507":"MN","612":"MN","651":"MN","763":"MN","952":"MN",
    "314":"MO","417":"MO","557":"MO","573":"MO","636":"MO","660":"MO","816":"MO","975":"MO",
    "228":"MS","601":"MS","662":"MS","769":"MS","406":"MT",
    "252":"NC","336":"NC","704":"NC","743":"NC","828":"NC","910":"NC","919":"NC","980":"NC","984":"NC",
    "701":"ND","308":"NE","402":"NE","531":"NE","603":"NH",
    "201":"NJ","551":"NJ","609":"NJ","732":"NJ","848":"NJ","856":"NJ","862":"NJ","908":"NJ","973":"NJ","640":"NJ",
    "505":"NM","575":"NM","957":"NM","702":"NV","725":"NV","775":"NV",
    "212":"NY","315":"NY","332":"NY","347":"NY","516":"NY","518":"NY","585":"NY","631":"NY",
    "646":"NY","716":"NY","718":"NY","845":"NY","914":"NY","917":"NY","929":"NY","680":"NY","838":"NY","934":"NY",
    "216":"OH","220":"OH","234":"OH","283":"OH","330":"OH","380":"OH","419":"OH","440":"OH",
    "513":"OH","567":"OH","614":"OH","740":"OH","937":"OH","326":"OH",
    "405":"OK","539":"OK","580":"OK","918":"OK","572":"OK",
    "458":"OR","503":"OR","541":"OR","971":"OR",
    "215":"PA","223":"PA","267":"PA","272":"PA","412":"PA","484":"PA","570":"PA","610":"PA",
    "717":"PA","724":"PA","814":"PA","835":"PA","878":"PA","445":"PA","582":"PA",
    "450":"QC","401":"RI",
    "803":"SC","843":"SC","864":"SC","839":"SC","854":"SC","605":"SD",
    "423":"TN","615":"TN","629":"TN","731":"TN","865":"TN","901":"TN","931":"TN",
    "210":"TX","214":"TX","254":"TX","281":"TX","325":"TX","346":"TX","361":"TX","409":"TX",
    "430":"TX","432":"TX","469":"TX","512":"TX","682":"TX","713":"TX","737":"TX","806":"TX",
    "817":"TX","830":"TX","832":"TX","903":"TX","915":"TX","936":"TX","940":"TX","956":"TX",
    "972":"TX","979":"TX","726":"TX","945":"TX",
    "385":"UT","435":"UT","801":"UT",
    "276":"VA","434":"VA","540":"VA","571":"VA","703":"VA","757":"VA","804":"VA","826":"VA","948":"VA",
    "802":"VT","340":"VI",
    "206":"WA","253":"WA","360":"WA","425":"WA","509":"WA","564":"WA",
    "262":"WI","414":"WI","608":"WI","715":"WI","920":"WI","534":"WI",
    "304":"WV","681":"WV","307":"WY"
}

ALL_STATES = sorted(set(AREACODE_STATE.values()))

# ─────────────────────────────────────────
# Colours / fonts
# ─────────────────────────────────────────
FONT_BOLD   = ("Arial", 10, "bold")
FONT_NORMAL = ("Arial", 10)
FONT_SMALL  = ("Arial", 9)
C_GREEN  = "#27ae60"
C_RED    = "#e74c3c"
C_BLUE   = "#2980b9"
C_ORANGE = "#e67e22"
C_GRAY   = "#95a5a6"
C_HDR    = "#dfe6e9"
C_DARK   = "#2c3e50"

# ─────────────────────────────────────────
# Root
# ─────────────────────────────────────────
root = tk.Tk()
root.title("DID Distribution Tool v5 – State-Aware Splitter")
root.geometry("1080x760")
root.resizable(True, True)

# ─────────────────────────────────────────
# Global data
# ─────────────────────────────────────────
cid_file_path = tk.StringVar()
stat_raw      = tk.IntVar(value=0)
stat_valid    = tk.IntVar(value=0)
stat_matched  = tk.IntVar(value=0)
stat_unknown  = tk.IntVar(value=0)

df_full    = None
state_pool = {}        # {state: int}  — populated after load
dialer_mgrs = []       # list of DialerManager instances


# ═══════════════════════════════════════════════════════════
# DialerManager – one instance per dialer panel
# ═══════════════════════════════════════════════════════════
class DialerManager:
    def __init__(self, parent_frame):
        self.state_rows = []   # list of StateRow instances
        self._build(parent_frame)
        dialer_mgrs.append(self)
        self.refresh()

    def _build(self, parent):
        self.panel = tk.LabelFrame(parent, font=FONT_BOLD, relief="ridge",
                                   bd=2, bg="white", text="  Dialer: (unnamed)  ")
        self.panel.pack(fill="x", padx=6, pady=6, ipadx=4, ipady=4)

        self.name_var  = tk.StringVar()
        self.total_var = tk.StringVar()
        self.name_var.trace_add("write",  lambda *a: self._on_name())
        self.total_var.trace_add("write", lambda *a: self.refresh())

        # ── header row ──
        hdr = tk.Frame(self.panel, bg="white")
        hdr.pack(fill="x", pady=(2,6))

        tk.Label(hdr, text="Dialer name:", font=FONT_BOLD, bg="white").pack(side="left", padx=(6,2))
        tk.Entry(hdr, textvariable=self.name_var, width=26,
                 font=FONT_NORMAL).pack(side="left", padx=(0,14))

        tk.Label(hdr, text="Total CIDs:", font=FONT_BOLD, bg="white").pack(side="left", padx=(0,2))
        tk.Entry(hdr, textvariable=self.total_var, width=12,
                 font=FONT_NORMAL, justify="center").pack(side="left", padx=(0,14))

        self.info_lbl = tk.Label(hdr, text="", font=FONT_SMALL, bg="white", fg=C_GRAY)
        self.info_lbl.pack(side="left", padx=4)

        tk.Button(hdr, text="✕ Remove Dialer", font=FONT_SMALL,
                  fg=C_RED, bg="white",
                  command=self._remove).pack(side="right", padx=6)

        # ── state table header ──
        tbl_wrap = tk.Frame(self.panel, bg="white")
        tbl_wrap.pack(fill="x", padx=8, pady=2)

        col_hdr = tk.Frame(tbl_wrap, bg=C_HDR)
        col_hdr.pack(fill="x")
        for txt, w in [("State",8),("Target CIDs",13),("Pool Available",15),("Status",22),("",4)]:
            tk.Label(col_hdr, text=txt, font=FONT_BOLD, bg=C_HDR,
                     width=w, anchor="w").pack(side="left", padx=2, pady=2)

        self.rows_frame = tk.Frame(tbl_wrap, bg="white")
        self.rows_frame.pack(fill="x")

        # ── quick-fill bar ──
        qf_wrap = tk.Frame(self.panel, bg="#eaf4fb", relief="flat", bd=1)
        qf_wrap.pack(fill="x", padx=8, pady=(4,2))

        tk.Label(qf_wrap, text="Quick-fill:", font=FONT_BOLD,
                 bg="#eaf4fb").pack(side="left", padx=(6,4), pady=4)

        self.quickfill_var = tk.StringVar(value="100")
        tk.Entry(qf_wrap, textvariable=self.quickfill_var, width=8,
                 font=FONT_NORMAL, justify="center").pack(side="left", padx=(0,4))

        tk.Label(qf_wrap, text="CIDs per state  →", font=FONT_SMALL,
                 bg="#eaf4fb", fg=C_GRAY).pack(side="left", padx=(0,6))

        tk.Button(qf_wrap, text="⚡ Fill All Available States",
                  font=FONT_SMALL, bg=C_GREEN, fg="white",
                  command=self._quickfill_all).pack(side="left", padx=(0,4))

        tk.Button(qf_wrap, text="Only States with Pool > 0",
                  font=FONT_SMALL, bg=C_BLUE, fg="white",
                  command=self._quickfill_nonzero).pack(side="left", padx=(0,4))

        tk.Button(qf_wrap, text="🗑 Clear All State Rows",
                  font=FONT_SMALL, bg=C_RED, fg="white",
                  command=self._clear_all_states).pack(side="left", padx=(0,6))

        # ── manual add state row button ──
        btn_wrap = tk.Frame(self.panel, bg="white")
        btn_wrap.pack(anchor="w", padx=8, pady=(2,4))
        tk.Button(btn_wrap, text="+ Add State Row", font=FONT_SMALL,
                  bg=C_BLUE, fg="white",
                  command=self.add_state_row).pack(side="left")

        # ── per-dialer summary ──
        self.summary_lbl = tk.Label(self.panel, text="", font=FONT_SMALL,
                                    fg=C_GRAY, bg="white", anchor="w")
        self.summary_lbl.pack(fill="x", padx=8, pady=(4,2))
        self.bar = ttk.Progressbar(self.panel, orient="horizontal",
                                   length=980, mode="determinate")
        self.bar.pack(fill="x", padx=8, pady=(0,4))

    def _on_name(self):
        n = self.name_var.get() or "(unnamed)"
        self.panel.config(text=f"  Dialer: {n}  ")
        refresh_global()

    def _remove(self):
        dialer_mgrs.remove(self)
        self.panel.destroy()
        refresh_global()

    def _get_quickfill_count(self):
        try:
            n = int(self.quickfill_var.get())
            if n <= 0: raise ValueError
            return n
        except ValueError:
            messagebox.showerror("Invalid Input",
                "Enter a positive whole number in the quick-fill box.")
            return None

    def _quickfill_all(self):
        """Add a row for every state in ALL_STATES with the quick-fill count."""
        n = self._get_quickfill_count()
        if n is None: return
        self._clear_all_states(confirm=False)
        for st in ALL_STATES:
            sr = StateRow(self.rows_frame, self, st, n)
            self.state_rows.append(sr)
        self.refresh()

    def _quickfill_nonzero(self):
        """Add a row only for states that have CIDs in the current pool."""
        n = self._get_quickfill_count()
        if n is None: return
        if not state_pool:
            messagebox.showwarning("No Pool",
                "Load a CID file first so the pool is known.")
            return
        self._clear_all_states(confirm=False)
        for st in sorted(state_pool.keys()):
            if state_pool[st] > 0:
                sr = StateRow(self.rows_frame, self, st, n)
                self.state_rows.append(sr)
        self.refresh()

    def _clear_all_states(self, confirm=True):
        if confirm and self.state_rows:
            if not messagebox.askyesno("Clear All",
                    f"Remove all {len(self.state_rows)} state rows for "
                    f"'{self.get_name() or 'this dialer'}'?"):
                return
        for sr in list(self.state_rows):
            sr.frame.destroy()
        self.state_rows.clear()
        self.refresh()

    def add_state_row(self, st="", cnt=0):
        sr = StateRow(self.rows_frame, self, st, cnt)
        self.state_rows.append(sr)
        self.refresh()

    def remove_state_row(self, sr):
        self.state_rows.remove(sr)
        sr.frame.destroy()
        self.refresh()

    def get_total(self):
        try:    return int(self.total_var.get())
        except: return 0

    def get_name(self):
        return self.name_var.get().strip()

    def get_state_targets(self):
        out = {}
        for sr in self.state_rows:
            st  = sr.state_var.get().strip().upper()
            try:    cnt = int(sr.count_var.get())
            except: cnt = 0
            if st and cnt > 0:
                out[st] = out.get(st, 0) + cnt
        return out

    def refresh(self):
        total     = self.get_total()
        state_sum = 0

        for sr in self.state_rows:
            st  = sr.state_var.get().strip().upper()
            try:    cnt = int(sr.count_var.get())
            except: cnt = 0

            avail = state_pool.get(st, 0) if st else 0
            sr.avail_lbl.config(text=f"{avail:,}" if st else "—")

            if not st:
                sr.status_lbl.config(text="", fg=C_GRAY)
            elif avail == 0:
                sr.status_lbl.config(text="⚠ Not in pool", fg=C_RED)
            elif cnt > avail:
                sr.status_lbl.config(text=f"⚠ Short by {cnt-avail:,}", fg=C_ORANGE)
            elif cnt > 0:
                sr.status_lbl.config(text="✓ OK", fg=C_GREEN)
            else:
                sr.status_lbl.config(text="", fg=C_GRAY)

            if cnt > 0:
                state_sum += cnt

        if total > 0:
            self.bar["value"] = min(state_sum / total * 100, 100)
            overflow = total - state_sum
            if state_sum > total:
                self.summary_lbl.config(
                    text=f"⚠ State targets ({state_sum:,}) EXCEED dialer total ({total:,}) by {state_sum-total:,}",
                    fg=C_RED)
            elif overflow > 0:
                self.summary_lbl.config(
                    text=f"State targets: {state_sum:,}  |  Total: {total:,}  |  Overflow fill: {overflow:,}",
                    fg=C_ORANGE)
            else:
                self.summary_lbl.config(
                    text=f"State targets: {state_sum:,}  |  Total: {total:,}  ✓ Fully assigned",
                    fg=C_GREEN)
        else:
            self.bar["value"] = 0
            self.summary_lbl.config(text="Set a Total CIDs count above.", fg=C_GRAY)

        refresh_global()


class StateRow:
    def __init__(self, parent, dialer_mgr, st="", cnt=0):
        self.dialer_mgr = dialer_mgr
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="x", pady=1)

        self.state_var = tk.StringVar(value=st.upper() if st else "")
        self.count_var = tk.StringVar(value=str(cnt) if cnt else "")

        self.state_var.trace_add("write",  lambda *a: self.dialer_mgr.refresh())
        self.count_var.trace_add("write",  lambda *a: self.dialer_mgr.refresh())

        ttk.Combobox(self.frame, textvariable=self.state_var,
                     values=ALL_STATES, width=7,
                     font=FONT_NORMAL, state="normal").pack(side="left", padx=2)

        tk.Entry(self.frame, textvariable=self.count_var, width=13,
                 font=FONT_NORMAL, justify="center").pack(side="left", padx=2)

        self.avail_lbl  = tk.Label(self.frame, text="—", width=15,
                                   font=FONT_SMALL, anchor="center", bg="white")
        self.status_lbl = tk.Label(self.frame, text="",  width=22,
                                   font=FONT_SMALL, anchor="w",      bg="white")
        self.avail_lbl.pack(side="left",  padx=2)
        self.status_lbl.pack(side="left", padx=2)

        tk.Button(self.frame, text="✕", fg=C_RED, bg="white",
                  font=FONT_SMALL, width=3,
                  command=lambda: self.dialer_mgr.remove_state_row(self)
                  ).pack(side="left", padx=2)


# ═══════════════════════════════════════════════════════════
# Notebook / Tabs
# ═══════════════════════════════════════════════════════════
nb = ttk.Notebook(root)
tab_load    = ttk.Frame(nb)
tab_dialers = ttk.Frame(nb)
tab_gen     = ttk.Frame(nb)
nb.add(tab_load,    text="  1. Load CID File  ")
nb.add(tab_dialers, text="  2. Dialers & States  ")
nb.add(tab_gen,     text="  3. Generate  ")
nb.pack(fill="both", expand=True, padx=8, pady=8)


# ═══════════════════════════════════════════════════════════
# TAB 1 – LOAD
# ═══════════════════════════════════════════════════════════
tk.Label(tab_load,
    text="Load your CID file (single column of 10-digit numbers). "
         "States are tagged automatically via built-in area code map.",
    font=FONT_BOLD, wraplength=800, justify="left"
).pack(anchor="w", padx=15, pady=(14,6))

rf = tk.Frame(tab_load)
rf.pack(fill="x", padx=15)
tk.Entry(rf, textvariable=cid_file_path, width=68, font=FONT_NORMAL).pack(side="left", padx=(0,6))
tk.Button(rf, text="Browse…", font=FONT_NORMAL,
          command=lambda: [cid_file_path.set(
              filedialog.askopenfilename(
                  filetypes=[("CSV","*.csv"),("Excel","*.xlsx *.xls"),("All","*.*")])
              or cid_file_path.get()
          )]).pack(side="left")
tk.Button(rf, text="  Load & Tag States  ", bg=C_BLUE, fg="white",
          font=FONT_BOLD, command=lambda: load_file()).pack(side="left", padx=10)

sf = tk.LabelFrame(tab_load, text="Load Summary", font=FONT_BOLD)
sf.pack(fill="x", padx=15, pady=8)
for i, (lbl, var) in enumerate([
    ("Rows in file:",        stat_raw),
    ("Valid 10-digit:",      stat_valid),
    ("Matched to state:",    stat_matched),
    ("Unknown area code:",   stat_unknown),
]):
    tk.Label(sf, text=lbl, font=FONT_BOLD).grid(row=i, column=0, sticky="w", padx=10, pady=2)
    tk.Label(sf, textvariable=var, font=FONT_NORMAL).grid(row=i, column=1, sticky="w")

tk.Label(tab_load, text="State Pool after tagging:", font=FONT_BOLD
         ).pack(anchor="w", padx=15, pady=(4,2))
pool_wrap = tk.Frame(tab_load)
pool_wrap.pack(fill="both", expand=True, padx=15, pady=(0,10))
pool_tree = ttk.Treeview(pool_wrap,
    columns=("state","count","pct"), show="headings", height=13)
pool_tree.heading("state", text="State")
pool_tree.heading("count", text="Available CIDs")
pool_tree.heading("pct",   text="% of Matched")
pool_tree.column("state", width=90,  anchor="center")
pool_tree.column("count", width=140, anchor="center")
pool_tree.column("pct",   width=120, anchor="center")
psb = ttk.Scrollbar(pool_wrap, orient="vertical", command=pool_tree.yview)
pool_tree.configure(yscrollcommand=psb.set)
pool_tree.pack(side="left", fill="both", expand=True)
psb.pack(side="right", fill="y")


def _clean(series):
    s = series.astype(str).apply(lambda x: re.sub(r'\D','',x))
    s = s.apply(lambda x: x[1:] if len(x)==11 and x.startswith('1') else x)
    return s[s.str.len()==10]


def load_file():
    global df_full, state_pool
    path = cid_file_path.get().strip()
    if not path:
        messagebox.showerror("Error","Select a file first."); return
    try:
        df_raw = (pd.read_csv(path, header=None, dtype=str)
                  if path.lower().endswith(".csv")
                  else pd.read_excel(path, header=None, dtype=str))
        stat_raw.set(len(df_raw))

        phones = _clean(df_raw.iloc[:,0].dropna()).drop_duplicates()
        stat_valid.set(len(phones))

        df = pd.DataFrame({"phone": phones.values})
        df["area_code"] = df["phone"].str[:3]
        df["state"]     = df["area_code"].map(AREACODE_STATE)

        matched   = df[df["state"].notna()]
        unmatched = df[df["state"].isna()]
        stat_matched.set(len(matched))
        stat_unknown.set(len(unmatched))

        df_full    = df.copy()
        state_pool = matched["state"].value_counts().to_dict()

        pool_tree.delete(*pool_tree.get_children())
        total_m = len(matched)
        for st, cnt in sorted(state_pool.items()):
            pct = f"{cnt/total_m*100:.1f}%" if total_m else "—"
            pool_tree.insert("","end", values=(st, f"{cnt:,}", pct))

        # refresh any existing dialers
        for dm in dialer_mgrs:
            dm.refresh()
        refresh_global()

        nb.select(tab_dialers)
        messagebox.showinfo("Loaded",
            f"Valid numbers:     {len(phones):,}\n"
            f"Matched to state:  {len(matched):,}\n"
            f"Unknown:           {len(unmatched):,}\n"
            f"States found:      {len(state_pool)}")
    except Exception as e:
        messagebox.showerror("Load Error", str(e)); raise


# ═══════════════════════════════════════════════════════════
# TAB 2 – DIALERS
# ═══════════════════════════════════════════════════════════
top_d = tk.Frame(tab_dialers)
top_d.pack(fill="x", padx=15, pady=8)
tk.Label(top_d, text="Add dialers, set totals, and define per-state targets.",
         font=FONT_BOLD).pack(side="left")
tk.Button(top_d, text="  + Add Dialer  ", font=FONT_BOLD,
          bg=C_GREEN, fg="white",
          command=lambda: DialerManager(d_inner)).pack(side="right")

d_outer = tk.Frame(tab_dialers)
d_outer.pack(fill="both", expand=True, padx=15, pady=(0,4))

d_canvas = tk.Canvas(d_outer, bg="#f5f6fa")
d_sb     = ttk.Scrollbar(d_outer, orient="vertical", command=d_canvas.yview)
d_inner  = tk.Frame(d_canvas, bg="#f5f6fa")
d_inner.bind("<Configure>",
    lambda e: d_canvas.configure(scrollregion=d_canvas.bbox("all")))
d_canvas.create_window((0,0), window=d_inner, anchor="nw")
d_canvas.configure(yscrollcommand=d_sb.set)
d_canvas.pack(side="left", fill="both", expand=True)
d_sb.pack(side="right", fill="y")

def _wheel(e):
    d_canvas.yview_scroll(int(-1*(e.delta/120)), "units")
d_canvas.bind_all("<MouseWheel>", _wheel)

# global bar
g_bar_f = tk.Frame(tab_dialers, bg=C_DARK)
g_bar_f.pack(fill="x", padx=15, pady=(0,6))
g_str = tk.StringVar(value="  Load a file and add dialers to begin.")
tk.Label(g_bar_f, textvariable=g_str, font=FONT_BOLD,
         bg=C_DARK, fg="white").pack(anchor="w", padx=6, pady=2)
g_bar = ttk.Progressbar(g_bar_f, orient="horizontal",
                         length=1000, mode="determinate")
g_bar.pack(fill="x", padx=6, pady=(0,4))


def refresh_global():
    avail = stat_matched.get()
    alloc = sum(dm.get_total() for dm in dialer_mgrs)
    rem   = avail - alloc
    g_str.set(
        f"  Global:  Allocated {alloc:,}  /  Available {avail:,}  |  "
        f"{'Remaining' if rem >= 0 else '⚠ OVER by'}: {abs(rem):,}"
    )
    g_bar["value"] = min(alloc / avail * 100, 100) if avail else 0


# ═══════════════════════════════════════════════════════════
# TAB 3 – GENERATE
# ═══════════════════════════════════════════════════════════
tk.Label(tab_gen, text="Generate Output Files", font=FONT_BOLD
         ).pack(anchor="w", padx=15, pady=(12,4))

opt_f = tk.LabelFrame(tab_gen, text="Options", font=FONT_BOLD)
opt_f.pack(fill="x", padx=15, pady=4)
shuffle_v    = tk.BooleanVar(value=True)
inc_state_v  = tk.BooleanVar(value=True)
inc_header_v = tk.BooleanVar(value=True)
tk.Checkbutton(opt_f, text="Shuffle pool before splitting (recommended)",
               variable=shuffle_v,    font=FONT_NORMAL).pack(anchor="w", padx=8, pady=2)
tk.Checkbutton(opt_f, text="Include 'state' column in output CSVs",
               variable=inc_state_v,  font=FONT_NORMAL).pack(anchor="w", padx=8, pady=2)
tk.Checkbutton(opt_f, text="Include header row in output CSVs",
               variable=inc_header_v, font=FONT_NORMAL).pack(anchor="w", padx=8, pady=2)

tk.Label(tab_gen, text="Progress:", font=FONT_BOLD).pack(anchor="w", padx=15, pady=(8,2))
gen_bar    = ttk.Progressbar(tab_gen, orient="horizontal", length=900, mode="determinate")
gen_status = tk.Label(tab_gen, text="", font=FONT_SMALL, fg=C_BLUE, anchor="w")
gen_bar.pack(padx=15, fill="x")
gen_status.pack(anchor="w", padx=15, pady=2)

res_wrap = tk.Frame(tab_gen)
res_wrap.pack(fill="both", expand=True, padx=15, pady=4)
res_tree = ttk.Treeview(res_wrap,
    columns=("dialer","state","requested","written","note"),
    show="headings", height=13)
res_tree.heading("dialer",    text="Dialer")
res_tree.heading("state",     text="State")
res_tree.heading("requested", text="Requested")
res_tree.heading("written",   text="Written")
res_tree.heading("note",      text="Note / File")
res_tree.column("dialer",    width=150)
res_tree.column("state",     width=80,  anchor="center")
res_tree.column("requested", width=100, anchor="center")
res_tree.column("written",   width=100, anchor="center")
res_tree.column("note",      width=430)
res_sb2 = ttk.Scrollbar(res_wrap, orient="vertical", command=res_tree.yview)
res_tree.configure(yscrollcommand=res_sb2.set)
res_tree.pack(side="left", fill="both", expand=True)
res_sb2.pack(side="right", fill="y")

tk.Button(tab_gen,
    text="  ⬇  Select Output Folder & Generate Files  ",
    bg=C_GREEN, fg="white", font=("Arial",11,"bold"),
    command=lambda: generate()).pack(side="bottom", pady=10)


def generate():
    global df_full

    if df_full is None:
        messagebox.showerror("Error","No file loaded. Complete Tab 1 first."); return

    dialers = []
    for dm in dialer_mgrs:
        name  = dm.get_name()
        total = dm.get_total()
        if not name or total <= 0:
            continue
        dialers.append({"name": name, "total": total,
                         "states": dm.get_state_targets()})

    if not dialers:
        messagebox.showerror("Error","No valid dialers defined."); return

    save_dir = filedialog.askdirectory(title="Select output folder")
    if not save_dir: return

    matched_df   = df_full[df_full["state"].notna()].copy()
    unmatched_df = df_full[df_full["state"].isna()].copy()

    if shuffle_v.get():
        matched_df = matched_df.sample(frac=1, random_state=42).reset_index(drop=True)

    pool = {}
    for st, grp in matched_df.groupby("state"):
        pool[st] = list(grp["phone"])

    gen_bar["maximum"] = len(dialers)
    gen_bar["value"]   = 0
    res_tree.delete(*res_tree.get_children())

    for i, d in enumerate(dialers):
        gen_status.config(text=f"Processing: {d['name']}…")
        root.update_idletasks()

        allocated = []

        # Phase 1 – state-specific targets
        for st, target in d["states"].items():
            p     = pool.get(st, [])
            take  = min(target, len(p))
            allocated.extend((ph, st) for ph in p[:take])
            pool[st] = p[take:]
            note = "✓ OK" if take == target else f"⚠ Short by {target-take:,}"
            res_tree.insert("","end", values=(d["name"], st,
                f"{target:,}", f"{take:,}", note))

        # Phase 2 – overflow fill
        need = d["total"] - len(allocated)
        if need > 0:
            got = 0
            for st in sorted(pool.keys()):
                if need <= 0: break
                p    = pool[st]
                take = min(need, len(p))
                allocated.extend((ph, st) for ph in p[:take])
                pool[st] = p[take:]
                need -= take; got += take
            if got:
                res_tree.insert("","end", values=(d["name"], "(overflow)",
                    f"{d['total']-len(allocated)+got:,}",
                    f"{got:,}", "Filled from remaining pool"))

        # Write
        if allocated:
            out_df = pd.DataFrame(allocated, columns=["phone","state"])
            if not inc_state_v.get():
                out_df = out_df[["phone"]]
            safe = re.sub(r'[^\w\-]','_', d["name"])
            out_path = os.path.join(save_dir, f"{safe}_CIDs.csv")
            out_df.to_csv(out_path, index=False, header=inc_header_v.get())
            res_tree.insert("","end", values=(
                d["name"], "▶ TOTAL",
                f"{d['total']:,}", f"{len(allocated):,}", f"→ {out_path}"))
            res_tree.insert("","end", values=("","","","",""))

        gen_bar["value"] = i + 1
        root.update_idletasks()

    # Remainder
    leftover  = [(p, st) for st, pl in pool.items() for p in pl]
    unknowns  = [(r["phone"], "UNKNOWN") for _, r in unmatched_df.iterrows()]
    remainder = leftover + unknowns
    if remainder:
        rem_df = pd.DataFrame(remainder, columns=["phone","state"])
        if not inc_state_v.get():
            rem_df = rem_df[["phone"]]
        rem_path = os.path.join(save_dir, "REMAINDER_CIDs.csv")
        rem_df.to_csv(rem_path, index=False, header=inc_header_v.get())
        res_tree.insert("","end", values=("REMAINDER","ALL",
            f"{len(remainder):,}", f"{len(remainder):,}", f"→ {rem_path}"))

    gen_status.config(
        text=f"✓ Done — {len(dialers)} dialer file(s) + REMAINDER written.", fg=C_GREEN)
    messagebox.showinfo("Done",
        f"Files generated: {len(dialers)}\n"
        f"Remainder:       {len(remainder):,} numbers\n\n"
        f"Folder: {save_dir}")


root.mainloop()
