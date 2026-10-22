import io
import os
import re
import zipfile
import pandas as pd
import streamlit as st

st.set_page_config(page_title="DID Distribution Tool v5", page_icon="📞", layout="wide")

# Built-in area code -> state mapping
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

def clean_numbers(series):
    values = series.dropna().astype(str).str.replace(r"\\D", "", regex=True)
    values = values.apply(lambda x: x[1:] if len(x) == 11 and x.startswith("1") else x)
    return values[values.str.len() == 10].drop_duplicates().reset_index(drop=True)

def read_input(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file, header=None, dtype=str)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file, header=None, dtype=str)
    raise ValueError("Upload a CSV, XLSX, or XLS file.")

def csv_bytes(frame, include_header):
    return frame.to_csv(index=False, header=include_header).encode("utf-8")

if "df_full" not in st.session_state:
    st.session_state.df_full = None
if "state_pool" not in st.session_state:
    st.session_state.state_pool = {}
if "dialers" not in st.session_state:
    st.session_state.dialers = []
if "generated_files" not in st.session_state:
    st.session_state.generated_files = {}

st.title("📞 DID Distribution Tool")
st.caption("State-aware CID/DID splitter • Upload a source file, define dialer targets, then generate downloadable CSVs.")

tab_load, tab_dialers, tab_generate = st.tabs(["1. Load CID File", "2. Dialers & States", "3. Generate"])

with tab_load:
    st.markdown("Upload a file with phone numbers in the **first column**. Numbers are cleaned to 10 digits and mapped using the built-in area-code table.")
    uploaded = st.file_uploader("Choose CID file", type=["csv", "xlsx", "xls"], key="cid_upload")
    if st.button("Load & Tag States", type="primary", disabled=uploaded is None):
        try:
            raw_df = read_input(uploaded)
            if raw_df.empty or raw_df.shape[1] == 0:
                st.error("The uploaded file is empty or has no columns.")
            else:
                phones = clean_numbers(raw_df.iloc[:, 0])
                df = pd.DataFrame({"phone": phones})
                df["area_code"] = df["phone"].str[:3]
                df["state"] = df["area_code"].map(AREACODE_STATE)
                matched = df[df["state"].notna()].copy()
                unmatched = df[df["state"].isna()].copy()
                st.session_state.df_full = df
                st.session_state.state_pool = matched["state"].value_counts().to_dict()
                st.session_state.load_stats = {
                    "Rows in file": len(raw_df),
                    "Valid unique 10-digit numbers": len(phones),
                    "Matched to state": len(matched),
                    "Unknown area code": len(unmatched),
                    "States found": len(st.session_state.state_pool),
                }
                st.success(f"Loaded {len(phones):,} valid unique phone numbers.")
        except Exception as exc:
            st.error(f"Could not load file: {exc}")

    if st.session_state.df_full is not None:
        df = st.session_state.df_full
        matched = df[df["state"].notna()]
        unmatched = df[df["state"].isna()]
        stats = st.session_state.get("load_stats", {})
        cols = st.columns(4)
        for col, label in zip(cols, ["Rows in file", "Valid unique 10-digit numbers", "Matched to state", "Unknown area code"]):
            col.metric(label, f"{stats.get(label, 0):,}")
        pool_df = (matched["state"].value_counts().rename_axis("State").reset_index(name="Available CIDs"))
        if not pool_df.empty:
            pool_df["% of Matched"] = (pool_df["Available CIDs"] / len(matched) * 100).map(lambda x: f"{x:.1f}%")
        st.subheader("State Pool after Tagging")
        st.dataframe(pool_df, use_container_width=True, hide_index=True)
        with st.expander("Unknown area-code numbers"):
            st.write(f"{len(unmatched):,} numbers have area codes not found in the built-in mapping.")

with tab_dialers:
    st.markdown("Add each dialer, set its total CID allocation, then specify state targets. State targets are assigned first; any remaining dialer capacity is filled from the remaining pool.")
    pool = st.session_state.state_pool
    if st.button("+ Add Dialer", type="primary"):
        st.session_state.dialers.append({
            "id": len(st.session_state.dialers) + 1,
            "name": f"Dialer {len(st.session_state.dialers) + 1}",
            "total": 0,
            "quickfill": 100,
            "states": {}
        })
    if not st.session_state.dialers:
        st.info("No dialers added yet. Click **+ Add Dialer** to begin.")
    for idx, dialer in enumerate(st.session_state.dialers):
        with st.expander(f"Dialer: {dialer['name'] or '(unnamed)'}", expanded=True):
            c1, c2, c3 = st.columns([2, 1, 1])
            dialer["name"] = c1.text_input("Dialer name", value=dialer["name"], key=f"name_{dialer['id']}")
            dialer["total"] = c2.number_input("Total CIDs", min_value=0, step=1, value=int(dialer["total"]), key=f"total_{dialer['id']}")
            dialer["quickfill"] = c3.number_input("Quick-fill per state", min_value=1, step=1, value=int(dialer["quickfill"]), key=f"qf_{dialer['id']}")
            state_options = [""] + ALL_STATES
            q1, q2, q3 = st.columns(3)
            if q1.button("⚡ Fill All States", key=f"all_{dialer['id']}"):
                dialer["states"] = {state: int(dialer["quickfill"]) for state in ALL_STATES}
            if q2.button("Only States with Pool > 0", key=f"nonzero_{dialer['id']}"):
                if not pool:
                    st.warning("Load a CID file first to populate the state pool.")
                else:
                    dialer["states"] = {state: int(dialer["quickfill"]) for state, count in pool.items() if count > 0}
            if q3.button("Clear All State Targets", key=f"clear_{dialer['id']}"):
                dialer["states"] = {}
            state_rows = list(dialer["states"].items())
            if state_rows:
                st.markdown("**State targets**")
                for row_idx, (state, count) in enumerate(state_rows):
                    r1, r2, r3, r4 = st.columns([1, 1, 1, 1])
                    selected = r1.selectbox("State", state_options[1:], index=state_options[1:].index(state) if state in state_options else 0, key=f"state_{dialer['id']}_{row_idx}")
                    amount = r2.number_input("Target CIDs", min_value=0, step=1, value=int(count), key=f"count_{dialer['id']}_{row_idx}")
                    available = int(pool.get(selected, 0))
                    r3.metric("Pool available", f"{available:,}")
                    if amount > available:
                        r4.warning(f"Short by {amount-available:,}")
                    else:
                        r4.caption("OK" if amount > 0 else "Target is 0")
                    dialer["states"][selected] = int(amount)
                if st.button("Apply State Row Changes", key=f"apply_{dialer['id']}"):
                    updated = {}
                    for row_idx in range(len(state_rows)):
                        selected = st.session_state.get(f"state_{dialer['id']}_{row_idx}", state_rows[row_idx][0])
                        amount = st.session_state.get(f"count_{dialer['id']}_{row_idx}", state_rows[row_idx][1])
                        updated[selected] = updated.get(selected, 0) + int(amount)
                    dialer["states"] = updated
                    st.success("State targets updated.")
            add1, add2, add3 = st.columns([1, 1, 2])
            add_state = add1.selectbox("Add state", ALL_STATES, key=f"addstate_{dialer['id']}")
            add_count = add2.number_input("Target", min_value=0, step=1, value=0, key=f"addcount_{dialer['id']}")
            if add3.button("Add / Update State Target", key=f"addrow_{dialer['id']}"):
                dialer["states"][add_state] = int(add_count)
                st.rerun()
            target_sum = sum(int(v) for v in dialer["states"].values())
            if dialer["total"] > 0:
                st.progress(min(target_sum / dialer["total"], 1.0))
            if target_sum > dialer["total"] and dialer["total"] > 0:
                st.error(f"State targets ({target_sum:,}) exceed dialer total ({dialer['total']:,}) by {target_sum-dialer['total']:,}.")
            elif dialer["total"] > target_sum:
                st.warning(f"State targets: {target_sum:,} / Total: {dialer['total']:,} • Overflow fill: {dialer['total']-target_sum:,}")
            else:
                st.success(f"State targets: {target_sum:,} / Total: {dialer['total']:,}")
            if st.button("Remove Dialer", key=f"remove_{dialer['id']}"):
                st.session_state.dialers.pop(idx)
                st.rerun()

    if st.session_state.dialers:
        allocation = sum(int(d["total"]) for d in st.session_state.dialers)
        available = sum(st.session_state.state_pool.values())
        remaining = available - allocation
        st.divider()
        st.subheader("Global Allocation")
        g1, g2, g3 = st.columns(3)
        g1.metric("Allocated", f"{allocation:,}")
        g2.metric("Matched pool available", f"{available:,}")
        g3.metric("Remaining" if remaining >= 0 else "Over-allocated", f"{abs(remaining):,}")
        st.progress(min(allocation / available, 1.0) if available else 0.0)

with tab_generate:
    st.subheader("Generate Output Files")
    if st.session_state.df_full is None:
        st.warning("Upload and load a CID file in Tab 1 first.")
    else:
        shuffle_pool = st.checkbox("Shuffle pool before splitting (recommended)", value=True)
        include_state = st.checkbox("Include state column in output CSVs", value=True)
        include_header = st.checkbox("Include header row in output CSVs", value=True)
        if st.button("Generate CSV Files", type="primary"):
            dialers = []
            for d in st.session_state.dialers:
                if d["name"].strip() and int(d["total"]) > 0:
                    dialers.append({"name": d["name"].strip(), "total": int(d["total"]), "states": {k: int(v) for k, v in d["states"].items() if int(v) > 0}})
            if not dialers:
                st.error("No valid dialers defined. Give each dialer a name and a Total CIDs value greater than zero.")
            else:
                try:
                    df_full = st.session_state.df_full.copy()
                    matched_df = df_full[df_full["state"].notna()].copy()
                    unmatched_df = df_full[df_full["state"].isna()].copy()
                    if shuffle_pool:
                        matched_df = matched_df.sample(frac=1).reset_index(drop=True)
                    pool = {state: list(group["phone"]) for state, group in matched_df.groupby("state")}
                    generated = {}
                    results = []
                    progress = st.progress(0.0)
                    status = st.empty()
                    for i, d in enumerate(dialers):
                        status.write(f"Processing: **{d['name']}**")
                        allocated = []
                        for state, target in d["states"].items():
                            available_numbers = pool.get(state, [])
                            take = min(target, len(available_numbers))
                            allocated.extend((phone, state) for phone in available_numbers[:take])
                            pool[state] = available_numbers[take:]
                            results.append({"Dialer": d["name"], "State": state, "Requested": target, "Written": take, "Note": "OK" if take == target else f"Short by {target-take:,}"})
                        need = max(0, d["total"] - len(allocated))
                        original_need = need
                        for state in sorted(pool.keys()):
                            if need <= 0:
                                break
                            available_numbers = pool[state]
                            take = min(need, len(available_numbers))
                            allocated.extend((phone, state) for phone in available_numbers[:take])
                            pool[state] = available_numbers[take:]
                            need -= take
                        overflow_written = original_need - need
                        if overflow_written:
                            results.append({"Dialer": d["name"], "State": "(overflow)", "Requested": original_need, "Written": overflow_written, "Note": "Filled from remaining pool"})
                        out_df = pd.DataFrame(allocated, columns=["phone", "state"])
                        if not include_state:
                            out_df = out_df[["phone"]]
                        safe = re.sub(r"[^\\w\\-]", "_", d["name"])
                        generated[f"{safe}_CIDs.csv"] = csv_bytes(out_df, include_header)
                        results.append({"Dialer": d["name"], "State": "TOTAL", "Requested": d["total"], "Written": len(allocated), "Note": f"{safe}_CIDs.csv"})
                        progress.progress((i + 1) / len(dialers))
                    leftover = [(phone, state) for state, numbers in pool.items() for phone in numbers]
                    unknowns = [(row["phone"], "UNKNOWN") for _, row in unmatched_df.iterrows()]
                    remainder = leftover + unknowns
                    if remainder:
                        rem_df = pd.DataFrame(remainder, columns=["phone", "state"])
                        if not include_state:
                            rem_df = rem_df[["phone"]]
                        generated["REMAINDER_CIDs.csv"] = csv_bytes(rem_df, include_header)
                    st.session_state.generated_files = generated
                    st.session_state.generation_results = results
                    st.session_state.remainder_count = len(remainder)
                    status.success(f"Finished: generated {len(dialers)} dialer file(s); {len(remainder):,} numbers remain.")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")

        if st.session_state.generated_files:
            st.subheader("Generation Results")
            st.dataframe(pd.DataFrame(st.session_state.get("generation_results", [])), use_container_width=True, hide_index=True)
            st.caption(f"Remainder numbers: {st.session_state.get('remainder_count', 0):,}")
            if len(st.session_state.generated_files) == 1:
                filename, data = next(iter(st.session_state.generated_files.items()))
                st.download_button(f"Download {filename}", data=data, file_name=filename, mime="text/csv")
            else:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                    for filename, data in st.session_state.generated_files.items():
                        zf.writestr(filename, data)
                st.download_button("⬇ Download All CSVs (ZIP)", data=zip_buffer.getvalue(), file_name="DID_Splitter_Output.zip", mime="application/zip")
