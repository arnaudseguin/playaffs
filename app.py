import streamlit as st
import json
import os
import hashlib

st.set_page_config(page_title="PLAYAFFS", layout="wide")

# --- DATA & HELPERS ---
THEMES = {
    "Colorado": ("#6F263D", "#FFFFFF", "#236192"), "Los Angeles": ("#111111", "#FFFFFF", "#A2AAAD"),
    "Dallas": ("#006436", "#FFFFFF", "#8E9090"), "Minnesota": ("#154734", "#FFFFFF", "#A6192E"),
    "Vegas": ("#B4975A", "#FFFFFF", "#333F48"), "Utah": ("#62B5E5", "#FFFFFF", "#000000"),
    "Edmonton": ("#041E42", "#FFFFFF", "#FF4C00"), "Anaheim": ("#F47A38", "#FFFFFF", "#B09862"),
    "Buffalo": ("#002654", "#FFFFFF", "#FCB514"), "Boston": ("#FFB81C", "#000000", "#000000"),
    "Tampa Bay": ("#002868", "#FFFFFF", "#FFFFFF"), "Montreal": ("#AF1E2D", "#FFFFFF", "#192168"),
    "Carolina": ("#CE1126", "#FFFFFF", "#000000"), "Ottawa": ("#C52032", "#FFFFFF", "#000000"),
    "Pittsburgh": ("#000000", "#FFB81C", "#FFB81C"), "Philadelphia": ("#F74902", "#FFFFFF", "#000000"),
    "---": ("#262626", "#888888", "#444444")
}

# Superficial stats for now
TEAM_DATA = {
    "Colorado": {"pts": "121", "gpg": "3.70", "gapg": "2.50"},
    "Los Angeles": {"pts": "90", "gpg": "2.70", "gapg": "3.00"},
    "Dallas": {"pts": "112", "gpg": "3.40", "gapg": "2.80"},
    "Minnesota": {"pts": "104", "gpg": "3.30", "gapg": "2.90"},
    "Vegas": {"pts": "95", "gpg": "3.30", "gapg": "3.00"},
    "Utah": {"pts": "92", "gpg": "3.30", "gapg": "3.00"},
    "Edmonton": {"pts": "93", "gpg": "3.50", "gapg": "3.30"},
    "Anaheim": {"pts": "92", "gpg": "3.30", "gapg": "3.60"},
    "Buffalo": {"pts": "109", "gpg": "3.50", "gapg": "3.00"},
    "Boston": {"pts": "100", "gpg": "3.30", "gapg": "3.10"},
    "Tampa Bay": {"pts": "106", "gpg": "3.50", "gapg": "2.80"},
    "Montreal": {"pts": "106", "gpg": "3.50", "gapg": "3.10"},
    "Carolina": {"pts": "113", "gpg": "3.60", "gapg": "2.90"},
    "Ottawa": {"pts": "99", "gpg": "3.40", "gapg": "3.00"},
    "Pittsburgh": {"pts": "98", "gpg": "3.60", "gapg": "3.20"},
    "Philadelphia": {"pts": "98", "gpg": "3.00", "gapg": "3.00"},
    "---": {"pts": "0", "gpg": "0.00", "gapg": "0.00"}
}

# Core roster definition (names only)
ROSTERS = {
    "Colorado": (["MacKinnon", "Necas"], ["Makar"], ["Wedgewood"]),
    "Los Angeles": (["Panarin", "Kempe"], ["Clarke"], ["Kuemper"]),
    "Dallas": (["Robertson", "Johnston"], ["Heiskanen"], ["Oettinger"]),
    "Minnesota": (["Kaprizov", "Boldy"], ["Hughes"], ["Gustavsson"]),
    "Vegas": (["Eichel", "Marner"], ["Andersson"], ["Schmid"]),
    "Utah": (["Keller", "Schmaltz"], ["Sergachev"], ["Vejmelka"]),
    "Edmonton": (["McDavid", "Draisaitl"], ["Bouchard"], ["Jarry"]),
    "Anaheim": (["Gauthier", "Carlsson"], ["Carlson"], ["Dostal"]),
    "Buffalo": (["Thompson", "Tuch"], ["Dahlin"], ["Luukkonen"]),
    "Boston": (["Pastrnak", "Geekie"], ["McAvoy"], ["Swayman"]),
    "Tampa Bay": (["Kucherov", "Guentzel"], ["Raddysh"], ["Vasilevskiy"]),
    "Montreal": (["Suzuki", "Caufield"], ["Hutson"], ["Dobes"]),
    "Carolina": (["Aho", "Ehlers"], ["Gostisbehere"], ["Bussi"]),
    "Ottawa": (["Stutzle", "Tkachuk"], ["Sanderson"], ["Ullmark"]),
    "Pittsburgh": (["Crosby", "Malkin"], ["Karlsson"], ["Skinner"]),
    "Philadelphia": (["Konecny", "Zegras"], ["Sanheim"], ["Vladar"])
}

ABBR = {"Colorado": "COL", "Los Angeles": "LAK", "Dallas": "DAL", "Minnesota": "MIN", "Vegas": "VGK", "Utah": "UTA", "Edmonton": "EDM", "Anaheim": "ANA", "Buffalo": "BUF", "Boston": "BOS", "Tampa Bay": "TBL", "Montreal": "MTL", "Carolina": "CAR", "Ottawa": "OTT", "Pittsburgh": "PIT", "Philadelphia": "PHI"}

WEST_R1 = [("Colorado", "Los Angeles"), ("Dallas", "Minnesota"), ("Vegas", "Utah"), ("Edmonton", "Anaheim")]
EAST_R1 = [("Buffalo", "Boston"), ("Tampa Bay", "Montreal"), ("Carolina", "Ottawa"), ("Pittsburgh", "Philadelphia")]

def load_json(p):
    if not os.path.exists(p): return {}
    with open(p, "r") as f:
        return json.load(f)

def save_json(p, d):
    with open(p, "w") as f:
        json.dump(d, f)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Sync user from URL to session state to persist through reloads
if "user" in st.query_params:
    st.session_state.user = st.query_params["user"]
elif 'user' not in st.session_state:
    st.session_state.user = ""

# --- CSS ---
st.markdown("""
<style>
    a, a * { text-decoration: none !important; color: inherit !important; }
    .round-title { text-align: center; width: 100%; font-weight: bold; margin-bottom: 10px; font-size: 1em; }
    .floating-menu { margin: 0 auto; max-width: 600px; background: #111; border: 4px solid #555; border-radius: 12px; padding: 30px; position: relative; }
    .close-x { position: absolute; top: -18px; right: -18px; width: 42px; height: 42px; background: #444; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; color: white !important; border: 4px solid #111; z-index: 1000; cursor: pointer; }
    .stat-row { display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid #333; font-size: 14px; font-family: monospace; }
    
    /* Mobile Scaling */
    @media (max-width: 800px) {
        [data-testid="column"] { min-width: 120px !important; }
        .round-title { font-size: 0.8em; }
        div[style*="font-size:12px"] { font-size: 10px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- STATE SYNC ---
# We prioritize the URL for the source of truth to prevent the "instantly switching back" bug
query_params = st.query_params
if "edit" in query_params:
    st.session_state.edit_mode = query_params["edit"] == "true"
elif 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if "page" in query_params:
    st.session_state.page = query_params["page"]
elif 'page' not in st.session_state:
    st.session_state.page = "rules"

# Initialize Results Data
if not os.path.exists("results.json"):
    save_json("results.json", {"locked": False, "winners": {}, "series_games": {}})
results_data = load_json("results.json")

if not os.path.exists("players_stats.json"):
    init_stats = {}
    for t, (fs, ds, gs) in ROSTERS.items():
        for p in fs + ds: init_stats[p] = {"gp": 0, "pts": 0}
        for p in gs: init_stats[p] = {"sv_list": [0.900]}
    save_json("players_stats.json", init_stats)
player_stats = load_json("players_stats.json")

is_locked = results_data.get("locked", False)

# --- PRE-CALCULATE PLAYER RANKINGS & POINTS ---
all_f_rank, all_d_rank, all_g_rank = [], [], []
for t, (fs, ds, gs) in ROSTERS.items():
    for p in fs: 
        s = player_stats.get(p, {"gp":0, "pts":0})
        all_f_rank.append({"p":p, "v": s['pts']/s['gp'] if s['gp'] > 0 else 0})
    for p in ds: 
        s = player_stats.get(p, {"gp":0, "pts":0})
        all_d_rank.append({"p":p, "v": s['pts']/s['gp'] if s['gp'] > 0 else 0})
    for p in gs:
        d = player_stats.get(p, {})
        svl = d.get("sv_list", [d.get("sv", 0.900)])
        all_g_rank.append({"p":p, "v": sum(svl)/len(svl) if svl else 0.0})

def get_rank_pts(sorted_list, depth, step):
    pts_map = {}
    for i, entry in enumerate(sorted_list):
        val = 8 - (i * step)
        pts_map[entry['p']] = max(step, val) if i < depth else 0
    return pts_map

f_pts_map = get_rank_pts(sorted(all_f_rank, key=lambda x: x['v'], reverse=True), 16, 0.5)
d_pts_map = get_rank_pts(sorted(all_d_rank, key=lambda x: x['v'], reverse=True), 8, 1.0)
g_pts_map = get_rank_pts(sorted(all_g_rank, key=lambda x: x['v'], reverse=True), 8, 1.0)

# Roster Popularity for DF
all_brackets = load_json("brackets.json")
all_roster_selections = [b.get(slot) for b in all_brackets.values() for slot in ["f1", "f2", "f3", "d1", "d2", "g"] if b.get(slot) != "---"]
total_users = max(1, len(all_brackets))
roster_pop = {p: all_roster_selections.count(p)/total_users for p in set(all_roster_selections)}

# Handle Pick logic via URL parameter
if "view_serie" in query_params and st.session_state.user and ("pick" in query_params or "games" in query_params):
    s_id = query_params["view_serie"]
    all_p = load_json("brackets.json")
    u_p = all_p.get(st.session_state.user, {})

    if "pick" in query_params:
        winner = query_params["pick"]
        old = u_p.get(s_id)
        u_p[s_id] = winner
        if old != winner:
            for k in list(u_p.keys()):
                if any(x in k for x in ["wr2","wr3","er2","er3","final"]) and u_p[k] == old: u_p[k] = "---"
    
    if "games" in query_params:
        u_p[f"games_{s_id}"] = int(query_params["games"])

    all_p[st.session_state.user] = u_p
    save_json("brackets.json", all_p)
    st.query_params.clear()
    st.query_params["user"] = st.session_state.user
    st.query_params["edit"] = str(st.session_state.edit_mode).lower()
    st.query_params["page"] = "bracket"
    st.query_params["view_serie"] = s_id
    if "view_user" in query_params: st.query_params["view_user"] = query_params["view_user"]
    st.rerun()

# --- SIDEBAR LOGIC ---
if not st.session_state.user:
    st.title("PLAYAFFS")
    st.error("⚠️ **IMPORTANT SECURITY WARNING** ⚠️")
    st.warning("Please **DO NOT** use a real password that you use for your email, bank, or other sensitive services. This site is for fun; please use a **disposable** or **simple** password specifically for this bracket challenge.")
    st.warning("👤 **Username Requirement**: Please use your **real name** as your username so everyone in the league can recognize you!")

    login_tab, reg_tab = st.tabs(["Log in", "Create an account"])
    
    with login_tab:
        u_log = st.text_input("Username", key="login_u")
        p_log = st.text_input("Password", type="password", key="login_p")
        if st.button("Log in", use_container_width=True):
            all_b = load_json("brackets.json")
            if u_log in all_b:
                saved_p = all_b[u_log].get("password")
                hashed_p = hash_password(p_log)
                
                if not saved_p or saved_p == hashed_p:
                    if not saved_p and p_log:
                        all_b[u_log]["password"] = hashed_p
                        save_json("brackets.json", all_b)
                    st.session_state.user = u_log
                    st.query_params["user"] = u_log
                    st.query_params["page"] = "bracket"
                    st.rerun()
                else:
                    st.error("Incorrect password.")
            else:
                st.error("Username not found. Please create an account.")

    with reg_tab:
        u_reg = st.text_input("Username", key="reg_u")
        p_reg = st.text_input("Password", type="password", key="reg_p")
        if st.button("Create Account", use_container_width=True):
            all_b = load_json("brackets.json")
            if u_reg in all_b:
                st.error("Username already taken.")
            elif not u_reg or not p_reg:
                st.error("Please fill in both fields.")
            else:
                all_b[u_reg] = {"password": hash_password(p_reg), "f1": "---", "f2": "---", "f3": "---", "d1": "---", "d2": "---", "g": "---"}
                save_json("brackets.json", all_b)
                st.session_state.user = u_reg
                st.query_params["user"] = u_reg
                st.query_params["page"] = "bracket"
                st.rerun()
else:
    st.sidebar.title("PLAYAFFS")
    st.sidebar.write(f"Logged in as: **{st.session_state.user}**")
    st.sidebar.divider()

    # --- NAVIGATION ---
    st.sidebar.subheader("Navigation")
    if st.sidebar.button("RULES", use_container_width=True):
        st.query_params["page"] = "rules"
        st.rerun()

    if st.sidebar.button("MY BRACKET", use_container_width=True):
        st.query_params["page"] = "bracket"
        st.query_params.pop("view_user", None)
        st.rerun()

    if st.sidebar.button("MY TEAM", use_container_width=True):
        st.query_params["page"] = "my_team"
        st.query_params.pop("view_user", None)
        st.rerun()

    if st.sidebar.button("PLAYERS STATS", use_container_width=True):
        st.query_params["page"] = "player_stats"
        st.rerun()

    if st.sidebar.button("LEAGUE", use_container_width=True):
        st.query_params["page"] = "leagues"
        st.rerun()

    # --- ADMIN SECTION ---
    if st.session_state.user == "arnseg":
        st.sidebar.divider()
        st.sidebar.subheader("Admin Control")
        if st.sidebar.button("ADMIN PANEL", use_container_width=True):
            st.query_params["page"] = "admin"
            st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("LOG OUT", use_container_width=True):
        st.query_params.clear()
        st.session_state.user = ""
        st.rerun()

    # --- MAIN CONTENT ---
    if st.session_state.page == "rules":
        st.title("Tournament Rules")
        st.markdown("""
        Welcome to **PLAYAFFS**! Here is how the scoring and features work:

        ### 🏒 Brackets
        Predict the winner of each series to earn base points: **4** (R1), **8** (R2), **16** (R3), and **32** (Finals).
        - **Games Bonus**: If you correctly predict the number of games in the series, you get a **1.5x bonus** on that pick.

        ### 👕 My Team
        Draft a unique 6-player roster (3 Forwards, 2 Defensemen, 1 Goalie).
        - Points are awarded based on how your players rank in the league (PPG for skaters, SV% for goalies).

        ### 📈 Difference Factor (DF)
        Reward your unique picks! Points are multiplied based on how many other players made the same choice.
        - **Brackets**: Rare correct picks get up to a **5x exponential multiplier**.
        - **Teams**: Rare player selections get up to a **2x exponential multiplier**.

        ---
        📱 **Mobile users**: For the best experience, please use your phone in **Landscape mode** to view the brackets.
        """)

    elif st.session_state.page == "leagues":
        st.title("Global League Standings")
        winners = results_data.get("winners", {})
        s_gms_results = results_data.get("series_games", {})

        # Pre-calculate Popularity for Difference Factor (DF)
        pop_stats = {}
        for sid in winners.keys():
            picks = [b.get(sid) for b in all_brackets.values() if b.get(sid) != "---"]
            pop_stats[sid] = {t: picks.count(t)/total_users for t in set(picks)} if picks else {}
        
        leaderboard = []
        base_scores = {"wr1": 4, "er1": 4, "wr2": 8, "er2": 8, "wr3": 16, "er3": 16, "final": 32}

        for user, pdata in all_brackets.items():
            b_pts, t_pts = 0.0, 0.0
            b_dfs, t_dfs = [], []
            
            # 1. Bracket Scoring
            for sid, win_team in winners.items():
                if win_team != "---" and pdata.get(sid) == win_team:
                    base = next((v for k, v in base_scores.items() if sid.startswith(k)), 0)
                    multiplier = 1.5 if int(pdata.get(f"games_{sid}", 0)) == int(s_gms_results.get(sid, -1)) else 1.0
                    
                    pop = pop_stats[sid].get(win_team, 1.0)
                    df = 5**(1-pop) # Exponential DF
                    b_dfs.append(df)
                    b_pts += (base * multiplier * df)

            # 2. Team Scoring
            for slot in ["f1", "f2", "f3", "d1", "d2", "g"]:
                p_full = pdata.get(slot, "---")
                if p_full == "---": continue
                p_name = p_full.split(" - ")[0]
                
                if slot.startswith("f"): base = f_pts_map.get(p_name, 0)
                elif slot.startswith("d"): base = d_pts_map.get(p_name, 0)
                else: base = g_pts_map.get(p_name, 0)
                
                if base > 0:
                    pop = roster_pop.get(p_full, 1.0)
                    df = 2**(1-pop) # Team DF is back to x2 (2^(1-p))
                    t_dfs.append(df)
                    t_pts += (base * df)

            leaderboard.append({
                "name": user, "b_pts": b_pts, "t_pts": t_pts, "total": b_pts + t_pts,
                "b_df": sum(b_dfs)/len(b_dfs) if b_dfs else 1.0,
                "t_df": sum(t_dfs)/len(t_dfs) if t_dfs else 1.0,
                "winner": pdata.get("final", "---")
            })

        leaderboard.sort(key=lambda x: x['total'], reverse=True)

        if all_brackets:
            st.write("**DF : Difference Factor**")
            cols = st.columns([0.4, 1.4, 0.9, 0.9, 0.9, 0.9, 0.9, 1.1, 1.1])
            heads = ["#", "PLAYER", "BRACKET PTS", "BRACKET DF  \n(1x-5x)", "TEAM PTS", "TEAM DF  \n(1x-2x)", "TOTAL PTS", "VIEW BRACKET", "VIEW TEAM"]
            for i, h in enumerate(heads): cols[i].write(f"**{h}**")
            st.divider()

            for i, row in enumerate(leaderboard):
                cols = st.columns([0.4, 1.4, 0.9, 0.9, 0.9, 0.9, 0.9, 1.1, 1.1])
                cols[0].write(f"{i+1}")

                theme = THEMES.get(row['winner'], THEMES["---"])
                badge = f"background:{theme[0]}; color:{theme[1]} !important; border:2px solid {theme[2]}; padding:4px 10px; border-radius:6px; font-weight:bold; display:inline-block;"
                cols[1].markdown(f'<div style="{badge}">{row["name"]}</div>', unsafe_allow_html=True)

                cols[2].write(f"{row['b_pts']:.1f}")
                cols[3].write(f"x{row['b_df']:.2f}")
                cols[4].write(f"{row['t_pts']:.1f}")
                cols[5].write(f"x{row['t_df']:.2f}")
                cols[6].write(f"**{row['total']:.1f}**")

                if cols[7].button("View", key=f"vb_{row['name']}", use_container_width=True):
                    st.query_params["view_user"] = row['name']
                    st.query_params["page"] = "bracket"
                    st.rerun()
                if cols[8].button("View", key=f"vt_{row['name']}", use_container_width=True):
                    st.query_params["view_user"] = row['name']
                    st.query_params["page"] = "my_team"
                    st.rerun()
        else:
            st.write("No one has joined yet.")

    elif st.session_state.page == "player_stats":
        st.title("Players Standings")
        
        tabs = st.tabs(["Forwards (PPG)", "Defense (PPG)", "Goalies (SV%)"])
        
        with tabs[0]:
            f_list = []
            for t, (fs, _, _) in ROSTERS.items():
                for p in fs:
                    s = player_stats.get(p, {"gp":0, "pts":0})
                    ppg = round(s['pts']/s['gp'], 2) if s['gp'] > 0 else 0.0
                    f_list.append({"Player": p, "Team": ABBR[t], "GP": s['gp'], "PTS": s['pts'], "PPG": ppg, "POINTS GIVEN": f_pts_map.get(p, 0)})
            sorted_f = sorted(f_list, key=lambda x: x['PPG'], reverse=True)
            for i, x in enumerate(sorted_f): x["RANK"] = f"{i+1}"
            st.table(sorted_f)
            
        with tabs[1]:
            d_list = []
            for t, (_, ds, _) in ROSTERS.items():
                for p in ds:
                    s = player_stats.get(p, {"gp":0, "pts":0})
                    ppg = round(s['pts']/s['gp'], 2) if s['gp'] > 0 else 0.0
                    d_list.append({"Player": p, "Team": ABBR[t], "GP": s['gp'], "PTS": s['pts'], "PPG": ppg, "POINTS GIVEN": d_pts_map.get(p, 0)})
            sorted_d = sorted(d_list, key=lambda x: x['PPG'], reverse=True)
            for i, x in enumerate(sorted_d): x["RANK"] = f"{i+1}"
            st.table(sorted_d)
            
        with tabs[2]:
            g_list = []
            for t, (_, _, gs) in ROSTERS.items():
                for p in gs:
                    data = player_stats.get(p, {"sv_list": [0.900]})
                    sv_history = data.get("sv_list", [data.get("sv", 0.900)])
                    avg_sv = sum(sv_history) / len(sv_history) if sv_history else 0.0
                    g_list.append({"Player": p, "Team": ABBR[t], "SV%": f"{avg_sv:.3f}", "POINTS GIVEN": g_pts_map.get(p, 0)})
            sorted_g = sorted(g_list, key=lambda x: x['SV%'], reverse=True)
            for i, x in enumerate(sorted_g): x["RANK"] = f"{i+1}"
            st.table(sorted_g)

    elif st.session_state.page == "my_team":
        target_user = st.query_params.get("view_user", st.session_state.user)
        is_viewing_others = target_user != st.session_state.user
        st.title("My Fantasy Roster")
        
        if is_viewing_others:
            st.warning(f"Viewing **{target_user}**'s team (Read-only)")
        elif is_locked:
            st.error("🔒 Roster editing is locked for the tournament.")
        else:
            st.info("Select 3 Forwards, 2 Defensemen, and 1 Goalie. Players must be unique.")
        
        all_p = load_json("brackets.json")
        u_p = all_p.get(target_user, {})

        # Generate options lists
        f_opts = ["---"] + [f"{p} - {ABBR[t]}" for t, (fs, _, _) in ROSTERS.items() for p in fs]
        d_opts = ["---"] + [f"{p} - {ABBR[t]}" for t, (_, ds, _) in ROSTERS.items() for p in ds]
        g_opts = ["---"] + [f"{p} - {ABBR[t]}" for t, (_, _, gs) in ROSTERS.items() for p in gs]

        def sbox(label, opts, key, index):
            return st.selectbox(label, opts, index=index, key=key, disabled=is_viewing_others)

        def get_idx(key, opts): return opts.index(u_p[key]) if key in u_p and u_p[key] in opts else 0

        # Hockey formation: Top (3 F), Middle (2 D), Bottom (1 G)
        f_cols = st.columns(3)
        f1 = f_cols[0].selectbox("---", f_opts, index=get_idx("f1", f_opts), key="f1_sel", disabled=is_viewing_others, label_visibility="collapsed")
        f2 = f_cols[1].selectbox("---", f_opts, index=get_idx("f2", f_opts), key="f2_sel", disabled=is_viewing_others, label_visibility="collapsed")
        f3 = f_cols[2].selectbox("---", f_opts, index=get_idx("f3", f_opts), key="f3_sel", disabled=is_viewing_others, label_visibility="collapsed")
        
        d_cols = st.columns([1, 2, 2, 1])
        d1 = d_cols[1].selectbox("--", d_opts, index=get_idx("d1", d_opts), key="d1_sel", disabled=is_viewing_others, label_visibility="collapsed")
        d2 = d_cols[2].selectbox("--", d_opts, index=get_idx("d2", d_opts), key="d2_sel", disabled=is_viewing_others, label_visibility="collapsed")
        
        g_cols = st.columns([1, 1, 1])
        g = g_cols[1].selectbox("-", g_opts, index=get_idx("g", g_opts), key="g_sel", disabled=is_viewing_others, label_visibility="collapsed")

        # Real-time uniqueness validation
        picks = [f1, f2, f3, d1, d2, g]
        active_picks = [p for p in picks if p != "---"]
        has_duplicates = len(active_picks) != len(set(active_picks))

        st.divider()
        if not is_viewing_others and not is_locked:
            if has_duplicates:
                st.error("Duplicate players detected! Each selection must be a different player.")
            
            if st.button("SAVE TEAM", use_container_width=True, type="primary", disabled=has_duplicates):
                u_p.update({"f1": f1, "f2": f2, "f3": f3, "d1": d1, "d2": d2, "g": g})
                all_p[st.session_state.user] = u_p
                save_json("brackets.json", all_p)
                st.success("Roster updated successfully!")
                st.rerun()

    elif st.session_state.page == "admin" and st.session_state.user == "arnseg":
        st.title("Admin Control Panel")
        if "admin_auth" not in st.session_state: st.session_state.admin_auth = False
        
        if not st.session_state.admin_auth:
            code = st.text_input("Enter Admin Secret Code", type="password")
            if st.button("Unlock"):
                # Use the secret if it exists, otherwise fallback to the default code
                admin_secret = st.secrets.get("ADMIN_CODE", "NHL123NHL")
                if code == admin_secret:
                    st.session_state.admin_auth = True
                    st.rerun()
                else: st.error("Incorrect code")
        else:
            st.success("Authenticated")
            tabs = st.tabs(["Lock Settings (Brackets & Teams)", "Series Results", "Player Stats", "User Management"])
            
            with tabs[0]:
                new_lock = st.toggle("Global Lock (Brackets & Teams)", value=is_locked)
                if new_lock != is_locked:
                    results_data["locked"] = new_lock
                    save_json("results.json", results_data)
                    st.rerun()

            with tabs[1]:
                st.subheader("Official Series Outcomes")
                all_keys = [f"wr1_{i}" for i in range(4)] + [f"er1_{i}" for i in range(4)] + ["wr2_0", "wr2_1", "er2_0", "er2_1", "wr3", "er3", "final"]
                for k in all_keys:
                    if k.startswith("wr1"): t1, t2 = WEST_R1[int(k.split("_")[1])]
                    elif k.startswith("er1"): t1, t2 = EAST_R1[int(k.split("_")[1])]
                    else:
                        mapping = {"wr2_0":("wr1_0","wr1_1"),"wr2_1":("wr1_2","wr1_3"),"er2_0":("er1_0","er1_1"),"er2_1":("er1_2","er1_3"),"wr3":("wr2_0","wr2_1"),"er3":("er2_0","er2_1"),"final":("wr3","er3")}
                        k1, k2 = mapping.get(k)
                        t1, t2 = results_data["winners"].get(k1, "---"), results_data["winners"].get(k2, "---")
                    
                    c1, c2, c3 = st.columns([1, 2, 1])
                    c1.write(f"**{k}**")
                    opts = ["---", t1, t2] if t1 != "---" and t2 != "---" else ["---"]
                    cur_w = results_data["winners"].get(k, "---")
                    w_idx = opts.index(cur_w) if cur_w in opts else 0
                    win = c2.selectbox("Winner", opts, index=w_idx, key=f"w_{k}")
                    
                    gms = c3.number_input("Games", 4, 7, value=results_data.get("series_games", {}).get(k, 4), key=f"g_{k}")
                    results_data["winners"][k] = win
                    if "series_games" not in results_data: results_data["series_games"] = {}
                    results_data["series_games"][k] = gms
                save_json("results.json", results_data)

            with tabs[2]:
                st.subheader("Edit Player Performance")
                t_sel = st.selectbox("Select Team", list(ROSTERS.keys()))
                cat = st.radio("Category", ["Forwards", "Defense", "Goalies"], horizontal=True)
                idx = 0 if cat == "Forwards" else 1 if cat == "Defense" else 2
                p_sel = st.selectbox("Select Player", ROSTERS[t_sel][idx], key=f"p_sel_{t_sel}_{cat}")
                
                if cat != "Goalies":
                    cur = player_stats.get(p_sel, {"gp": 0, "pts": 0})
                    gp = st.number_input("Games Played", 0, 82, value=cur.get('gp', 0), key=f"gp_in_{p_sel}")
                    pts = st.number_input("Points", 0, 200, value=cur.get('pts', 0), key=f"pts_in_{p_sel}")
                    ppg = round(pts / gp, 2) if gp > 0 else 0.0
                    st.write(f"Calculated PPG: **{ppg}**")
                    if st.button("Update Skater"):
                        player_stats[p_sel] = {"gp": gp, "pts": pts}
                        save_json("players_stats.json", player_stats); st.rerun()
                else:
                    data = player_stats.get(p_sel, {})
                    if "sv_list" not in data:
                        data = {"sv_list": [data.get("sv", 0.900)]}
                    
                    avg = sum(data["sv_list"]) / len(data["sv_list"]) if data["sv_list"] else 0.0
                    st.write(f"Recorded Games ({len(data['sv_list'])}):")
                    st.info(", ".join([f"{v:.3f}" for v in data["sv_list"]]) if data["sv_list"] else "No games recorded")
                    st.write(f"Current Average: **{avg:.3f}**")
                    
                    new_sv = st.number_input("New Game Save %", 0.0, 1.0, value=0.900, step=0.001, format="%.3f", key=f"sv_add_{p_sel}")
                    c1, c2 = st.columns(2)
                    if c1.button("Add Game"):
                        data["sv_list"].append(new_sv)
                        player_stats[p_sel] = data
                        save_json("players_stats.json", player_stats); st.rerun()
                    if c2.button("Reset Stats"):
                        data["sv_list"] = []
                        player_stats[p_sel] = data
                        save_json("players_stats.json", player_stats); st.rerun()

            with tabs[3]:
                st.subheader("User Management")
                # Filter out admin accounts from the deletion list for safety
                player_list = [u for u in all_brackets.keys() if u != "arnseg"]
                if player_list:
                    u_to_del = st.selectbox("Select player to remove from server", player_list)
                    if st.button("DELETE PLAYER DATA", type="primary", use_container_width=True):
                        del all_brackets[u_to_del]
                        save_json("brackets.json", all_brackets)
                        st.success(f"User '{u_to_del}' and all their data have been deleted.")
                        st.rerun()
                else:
                    st.info("No non-admin players found in the database.")

    elif st.session_state.page == "bracket":
        # Determine which user's data to display
        target_user = st.query_params.get("view_user", st.session_state.user)
        is_viewing_others = target_user != st.session_state.user
        
        preds = load_json("brackets.json").get(target_user, {})
        active_serie = query_params.get("view_serie")

        if is_viewing_others:
            st.warning(f"👁️ Viewing **{target_user}**'s bracket (Read-only)")

        if active_serie:
            # Resolution logic (remains same)
            if active_serie.startswith("wr1"): tA, tB = WEST_R1[int(active_serie.split("_")[1])]
            elif active_serie.startswith("er1"): tA, tB = EAST_R1[int(active_serie.split("_")[1])]
            elif active_serie == "wr2_0": tA, tB = preds.get("wr1_0", "---"), preds.get("wr1_1", "---")
            elif active_serie == "wr2_1": tA, tB = preds.get("wr1_2", "---"), preds.get("wr1_3", "---")
            elif active_serie == "er2_0": tA, tB = preds.get("er1_0", "---"), preds.get("er1_1", "---")
            elif active_serie == "er2_1": tA, tB = preds.get("er1_2", "---"), preds.get("er1_3", "---")
            elif active_serie == "wr3": tA, tB = preds.get("wr2_0", "---"), preds.get("wr2_1", "---")
            elif active_serie == "er3": tA, tB = preds.get("er2_0", "---"), preds.get("er2_1", "---")
            elif active_serie == "final": tA, tB = preds.get("wr3", "---"), preds.get("er3", "---")
            else: tA, tB = "---", "---"

            sA, sB = TEAM_DATA.get(tA, TEAM_DATA["---"]), TEAM_DATA.get(tB, TEAM_DATA["---"])
            # Build Pick URLs
            base_url = f"/?page=bracket&edit={str(st.session_state.edit_mode).lower()}&user={st.session_state.user}&view_serie={active_serie}"
            if is_viewing_others: base_url += f"&view_user={target_user}"
            
            pickA_url = f"{base_url}&pick={tA}"
            pickB_url = f"{base_url}&pick={tB}"

            _, mid_col, _ = st.columns([1, 1.8, 1])
            with mid_col:
                # Only make the headers clickable if in Edit Mode
                can_edit = st.session_state.edit_mode and not is_viewing_others and not is_locked
                linkA = f'href="{pickA_url}" target="_self"' if can_edit and tA != "---" else ""
                linkB = f'href="{pickB_url}" target="_self"' if can_edit and tB != "---" else ""
                
                # Game length selection UI
                cur_gms = preds.get(f"games_{active_serie}", 4)
                gms_html = '<div style="display:flex; justify-content:center; gap:8px; margin-top:15px; border-top:1px solid #333; padding-top:15px;">'
                for g_val in [4, 5, 6, 7]:
                    g_url = f"{base_url}&games={g_val}"
                    is_sel = int(cur_gms) == g_val
                    border = f"2px solid {'#1565C0' if is_sel else '#444'}"
                    bg = "#1565C0" if is_sel else "#222"
                    color = "white" if is_sel else "#888"
                    g_link = f'href="{g_url}" target="_self"' if can_edit else ""
                    gms_html += f'<a {g_link} style="flex:1;"><div style="background:{bg}; color:{color} !important; border:{border}; padding:8px; border-radius:6px; font-weight:bold; font-size:14px; text-align:center;">{g_val}</div></a>'
                gms_html += '</div>'

                st.markdown(f"""
                <div class="floating-menu">
                    <a href="/?page=bracket&edit={str(st.session_state.edit_mode).lower()}&user={st.session_state.user}" target="_self" class="close-x">×</a>
                    <div style="display:flex; justify-content:space-between; margin-bottom:20px;">
                        <a {linkA} style="width:42%;"><div style="background:{THEMES.get(tA, THEMES['---'])[0]}; color:{THEMES.get(tA, THEMES['---'])[1]} !important; border:3px solid {THEMES.get(tA, THEMES['---'])[2]}; padding:15px; border-radius:10px; font-weight:bold; font-size:18px; text-align:center; cursor:pointer;">{tA}</div></a>
                        <div style="align-self:center; font-weight:bold; color:#555 !important; font-size:20px;">VS</div>
                        <a {linkB} style="width:42%;"><div style="background:{THEMES.get(tB, THEMES['---'])[0]}; color:{THEMES.get(tB, THEMES['---'])[1]} !important; border:3px solid {THEMES.get(tB, THEMES['---'])[2]}; padding:15px; border-radius:10px; font-weight:bold; font-size:18px; text-align:center; cursor:pointer;">{tB}</div></a>
                    </div>
                    <div class="stat-row"><span>{sA['pts']}</span><span>POINTS</span><span>{sB['pts']}</span></div>
                    <div class="stat-row"><span>{sA['gpg']}</span><span>GPG</span><span>{sB['gpg']}</span></div>
                    <div class="stat-row"><span>{sA['gapg']}</span><span>GAPG</span><span>{sB['gapg']}</span></div>
                    <div style="text-align:center; font-size:12px; color:#666; margin-top:15px; font-weight:bold; text-transform:uppercase;">Series Length</div>
                    {gms_html}
                </div>
                """, unsafe_allow_html=True)

                if is_locked and not is_viewing_others:
                    st.warning("Brackets are locked for the start of the tournament.")
                elif not st.session_state.edit_mode and not is_viewing_others:
                    st.info("Click EDIT in the sidebar to modify your bracket.")
            st.divider()

        def draw_serie(s_id, teams, opp_keys=None):
            nA = preds.get(opp_keys[0], "---") if opp_keys else teams[0]
            nB = preds.get(opp_keys[1], "---") if opp_keys else teams[1]
            win, gms = preds.get(s_id, "---"), preds.get(f"games_{s_id}", 4)
            cA, cB = THEMES.get(nA, THEMES["---"]), THEMES.get(nB, THEMES["---"])
            lck = "0.3" if (nA == "---" or nB == "---") else "1.0"
            txtA, txtB = (f"★ {nA}" if win == nA else nA), (f"★ {nB}" if win == nB else nB)
            # URL carries both the edit state and the user session
            url = f"/?page=bracket&view_serie={s_id}&edit={str(st.session_state.edit_mode).lower()}&user={st.session_state.user}"
            if target_user != st.session_state.user:
                url += f"&view_user={target_user}"
            st.markdown(f'<a href="{url}" target="_self"><div style="margin:8px 0; opacity:{lck};"><div style="background:{cA[0]}; color:{cA[1]} !important; padding:6px; border:4px solid {cA[2]}; border-radius:6px; font-weight:bold; font-size:12px; text-align:center; margin-bottom:4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{txtA}</div><div style="background:{cB[0]}; color:{cB[1]} !important; padding:6px; border:4px solid {cB[2]}; border-radius:6px; font-weight:bold; font-size:12px; text-align:center; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{txtB}</div>{"<div style=\'text-align:center;font-size:10px;color:#888\'>in "+str(gms)+"</div>" if win != "---" else ""}</div></a>', unsafe_allow_html=True)

        cols = st.columns([1.5, 1, 1, 1.5, 1, 1, 1.5])
        titles = ["R1 WEST", "R2", "R3", "FINAL", "R3", "R2", "R1 EAST"]
        for i, col in enumerate(cols):
            with col: st.markdown(f'<div class="round-title">{titles[i]}</div>', unsafe_allow_html=True)
            
        with cols[0]:
            for i, t in enumerate(WEST_R1): draw_serie(f"wr1_{i}", t)
        with cols[1]:
            st.markdown("<div style='height:42px'></div>", unsafe_allow_html=True)
            draw_serie("wr2_0", None, ["wr1_0", "wr1_1"]); st.markdown("<div style='height:84px'></div>", unsafe_allow_html=True)
            draw_serie("wr2_1", None, ["wr1_2", "wr1_3"])
        with cols[2]:
            st.markdown("<div style='height:126px'></div>", unsafe_allow_html=True)
            draw_serie("wr3", None, ["wr2_0", "wr2_1"])
        with cols[3]:
            st.markdown("<div style='height:210px'></div>", unsafe_allow_html=True)
            draw_serie("final", None, ["wr3", "er3"])
            chmp = preds.get("final", "---")
            if chmp != "---":
                c = THEMES.get(chmp, THEMES["---"])
                st.markdown(f'<div style="background:{c[0]}; color:{c[1]} !important; border:6px solid {c[2]}; border-radius:15px; padding:20px 5px; text-align:center; margin-top:20px; min-height:100px; display:flex; flex-direction:column; justify-content:center;"><div style="font-size:0.9em; font-weight:bold; opacity:0.8; text-transform:uppercase;">Champion</div><div style="font-size:1.5em; font-weight:800; line-height:1.1; margin-top:5px;">{chmp}</div></div>', unsafe_allow_html=True)
        with cols[4]:
            st.markdown("<div style='height:126px'></div>", unsafe_allow_html=True)
            draw_serie("er3", None, ["er2_0", "er2_1"])
        with cols[5]:
            st.markdown("<div style='height:42px'></div>", unsafe_allow_html=True)
            draw_serie("er2_0", None, ["er1_0", "er1_1"]); st.markdown("<div style='height:84px'></div>", unsafe_allow_html=True)
            draw_serie("er2_1", None, ["er1_2", "er1_3"])
        with cols[6]:
            for i, t in enumerate(EAST_R1): draw_serie(f"er1_{i}", t)

        # --- BRACKET TOOLS (UNDERNEATH) ---
        if not is_viewing_others:
            st.divider()
            _, t_col, _ = st.columns([1, 1, 1])
            with t_col:
                if is_locked:
                    st.error("🔒 BRACKET LOCKED")
                else:
                    new_edit_state = "false" if st.session_state.edit_mode else "true"
                    e_label = "SAVE & CLOSE BRACKET" if st.session_state.edit_mode else "EDIT BRACKET"
                    st.markdown(f'<a href="/?page=bracket&edit={new_edit_state}&user={st.session_state.user}" target="_self" style="display: block; padding: 10px; background: {"#C62828" if st.session_state.edit_mode else "#1565C0"}; color: white !important; text-align: center; border-radius: 8px; font-weight: bold; margin-bottom: 10px;">{e_label}</a>', unsafe_allow_html=True)
                    
                    if st.session_state.edit_mode:
                        if st.button("RESET BRACKET", use_container_width=True):
                            all_p = load_json("brackets.json")
                            all_p[st.session_state.user] = {}
                            save_json("brackets.json", all_p)
                            st.rerun()
