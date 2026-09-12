import json
import streamlit as st
import streamlit.components.v1 as components

# ============================================================
# SUPABASE CONFIG
# ============================================================
def get_supabase_public_config():
    """
    Return only the browser-safe Supabase connection values.

    IMPORTANT:
    - The publishable/anon key is safe to expose to the browser.
    - A secret/service-role key must NEVER be injected into GAME_HTML.
    """
    try:
        cfg = st.secrets["supabase"]
        url = str(cfg.get("url", "")).strip()

        public_key = str(
            cfg.get("publishable_key", "")
            or cfg.get("anon_key", "")
        ).strip()

        # Backward-compatible fallback only when `key` is already a
        # browser-safe publishable/anon key. Never expose sb_secret_*.
        if not public_key:
            fallback = str(cfg.get("key", "")).strip()
            if fallback and not fallback.startswith("sb_secret_"):
                public_key = fallback

        return url, public_key
    except Exception:
        return "", ""

SUPABASE_URL, SUPABASE_PUBLIC_KEY = get_supabase_public_config()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Testing Game",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# LOGIN
# ============================================================
def check_credentials(username: str, password: str) -> bool:
    """
    Credentials are stored in Streamlit Secrets.
    Example:
    [auth.users]
    Tester1 = "Blue"
    """
    try:
        users = st.secrets["auth"]["users"]
        return username in users and password == users[username]
    except Exception:
        return False

def show_login():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        .block-container {
            padding-top: 2.2rem;
            max-width: 920px;
        }
        .login-title {
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: .15rem;
        }
        .login-sub {
            opacity: .72;
            margin-bottom: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    left, right = st.columns(
        [1.35, 1],
        vertical_alignment="center"
    )
    with left:
        st.markdown(
            '<div class="login-title">🔵 Testing Game</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="login-sub">'
            'For the game to begin please sign in'
            '</div>',
            unsafe_allow_html=True,
        )
        with st.form(
            "login_form",
            clear_on_submit=False
        ):
            username = st.text_input(
                "Username",
                placeholder="Username"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Password"
            )
            submitted = st.form_submit_button(
                "LOGIN",
                use_container_width=True
            )
        if submitted:
            if check_credentials(username, password):
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error(
                    "🦖 RAWR... wrong username or password. "
                    "No castle hunting for impostors."
                )
    with right:
        try:
            st.image(
                "RATeamLogo.png",
                use_container_width=True
            )
        except Exception:
            st.info(
                "Add **RATeamLogo.png** to the same "
                "GitHub folder as `app.py`."
            )
    st.stop()

if not st.session_state.get(
    "authenticated",
    False
):
    show_login()

# ============================================================
# LOGGED-IN HEADER
# ============================================================
head_left, head_right = st.columns(
    [5, 1],
    vertical_alignment="center"
)
with head_left:

    st.caption(
        f"Logged in as "
        f"**{st.session_state.get('username', '')}**"
    )

with head_right:
    if st.button(
        "Log out",
        use_container_width=True
    ):
        st.session_state.clear()
        st.rerun()
# ============================================================
# GAME
# ============================================================
GAME_HTML = r"""
<div id="ks-root" tabindex="0">
<style>
#ks-root {
    width: 100%;
    outline: none;
    color: #f8fafc;
    font-family:
        Arial,
        Helvetica,
        sans-serif;
}
#ks-wrap {
    max-width: 900px;
    margin: 0 auto;
}

/* =========================
   PLAYER SCOREBOARD
   ========================= */

#all-player-scoreboard {
    width: min(650px, 94%);
    margin: 4px auto 16px auto;
    background: #111827;
    border: 2px solid #7c3aed;
    border-radius: 10px;
    padding: 10px 14px;
    box-sizing: border-box;
}

.all-score-title {
    color: #ffd166;
    font-size: 15px;
    font-weight: 900;
    text-align: center;
    margin-bottom: 7px;
}

.all-score-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
    color: #f8fafc;
}

.all-score-table th,
.all-score-table td {
    padding: 5px 4px;
    text-align: center;
    border-bottom: 1px solid #334155;
}

.all-score-table th:first-child,
.all-score-table td:first-child {
    text-align: left;
}

.all-score-table th {
    color: #93c5fd;
    font-weight: 900;
}

.all-score-table tr:last-child td {
    border-bottom: 0;
}

/* =========================
   INTRO
   ========================= */
#intro-panel {
    max-width: 820px;
    margin:
        28px auto
        18px auto;
    padding:
        30px 34px;
    border:
        2px solid
        #7c3aed;
    border-radius:
        14px;
    background:
        #111827;
    text-align:
        center;
    line-height:
        1.65;
    font-size:
        17px;
}
#intro-title {
    color:
        #ffd166;
    font-size:
        27px;
    font-weight:
        900;
    margin-bottom:
        18px;
}
#intro-text {
    color:
        #f8fafc;
    font-size:
        17px;
}

#start-game {
    margin-top:
        22px;
    min-width:
        210px;
    border:
        0;
    border-radius:
        9px;
    padding:
        12px 18px;
    font-size:
        16px;

    font-weight:
        900;

    color:
        white;

    background:
        #7c3aed;

    cursor:
        pointer;
}

#start-game:hover {

    background:
        #5b21b6;
}

#intro-buttons {
    margin-top: 22px;
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

#intro-buttons #start-game,
#intro-buttons #help-game {
    margin-top: 0;
}

#help-game {
    min-width: 150px;
    border: 2px solid #7c3aed;
    border-radius: 9px;
    padding: 10px 16px;
    font-size: 15px;
    font-weight: 900;
    color: #7c3aed;
    background: white;
    cursor: pointer;
}

#help-game:hover {
    background: #f3e8ff;
}

/* Help pop-up */
#help-modal {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(2, 6, 23, 0.72);
    z-index: 9999;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
}

#help-card {
    width: min(620px, 92vw);
    background: #111827;
    border: 2px solid #7c3aed;
    border-radius: 14px;
    padding: 24px 26px;
    color: #f8fafc;
    text-align: left;
    box-shadow: 0 18px 50px rgba(0,0,0,.35);
}

#help-card h3 {
    margin: 0 0 14px 0;
    color: #ffd166;
    text-align: center;
    font-size: 24px;
}

#help-card p {
    margin: 9px 0;
    line-height: 1.55;
    font-size: 15px;
}

#help-card strong {
    color: #93c5fd;
}

#close-help {
    display: block;
    margin: 18px auto 0;
    min-width: 140px;
    border: 0;
    border-radius: 8px;
    padding: 10px 15px;
    background: #7c3aed;
    color: white;
    font-weight: 900;
    cursor: pointer;
}

#close-help:hover {
    background: #5b21b6;
}

/* =========================
   GAME HEADER
   ========================= */

#ks-header {

    text-align:
        center;

    margin:
        2px 0
        8px 0;
}

#ks-title {

    font-size:
        25px;

    font-weight:
        900;

    color:
        #ffd166;

    letter-spacing:
        .5px;
}

#ks-status {

    font-size:
        14px;

    font-weight:
        700;

    margin-top:
        4px;
    color:black;
}

#ks-letters {

    font-size:
        18px;

    font-weight:
        900;

    color:
        #7dd3fc;

    margin-top:
        4px;

    margin-bottom:
        5px;

    letter-spacing:
        6px;
}

/* =========================
   GAME CANVAS
   ========================= */

#game-shell {

    position:
        relative;

    width:
        100%;

    border-radius:
        8px;

    overflow:
        hidden;
}

#game {

    display:
        block;

    margin:
        0 auto;

    background:
        #050816;

    border:
        3px solid
        #6d28d9;

    /*
       Original canvas is still
       1230 × 750 internally.

       We only SCALE its display
       size, so collision logic and
       movement remain untouched.
    */

    width:
        min(780px, 88vw);

    max-width:
        100%;

    height:
        auto;
}

/* =========================
   BUTTONS
   ========================= */

#controls {

    margin:
        8px auto 0;

    max-width:
        860px;

    display:
        flex;

    justify-content:
        center;

    gap:
        10px;

    flex-wrap:
        wrap;
}

#controls button {

    min-width:
        150px;

    border:
        0;

    border-radius:
        8px;

    padding:
        8px 12px;

    font-size:
        14px;

    font-weight:
        800;

    color:
        white;

    background:
        #7c3aed;

    cursor:
        pointer;
}

#controls button:hover {

    background:
        #5b21b6;
}

#help {

    text-align:
        center;

    opacity:
        .78;

    margin-top:
        6px;

    font-size:
        12px;
}

/* =========================
   GUESS PANEL
   ========================= */

#guess-panel {

    display:
        none;

    max-width:
        620px;

    margin:
        10px auto 0;

    border:
        2px solid
        #ffd166;

    background:
        #111827;

    border-radius:
        10px;

    padding:
        14px;

    text-align:
        center;
}

#guess-panel h3 {

    margin:
        0 0 8px;

    color:
        #ffd166;
}

#guess-panel input {

    width:
        min(360px, 88%);

    padding:
        10px 12px;

    border-radius:
        7px;

    border:
        1px solid
        #475569;

    background:
        #020617;

    color:
        white;

    font-size:
        17px;

    text-align:
        center;
}

#guess-panel button {

    margin-left:
        8px;

    padding:
        10px 15px;

    border:
        0;

    border-radius:
        7px;

    color:
        white;

    background:
        #2563eb;

    font-weight:
        800;

    cursor:
        pointer;
}

#guess-feedback {

    min-height:
        24px;

    margin-top:
        10px;

    font-weight:
        800;
}


/* =========================
   MOBILE TOUCH CONTROLS
   ========================= */
#mobile-controls {
    display: none;
    margin: 10px auto 4px;
    width: 210px;
    user-select: none;
    -webkit-user-select: none;
    touch-action: none;
}

.mobile-pad {
    display: grid;
    grid-template-columns: 64px 64px 64px;
    grid-template-rows: 58px 58px 58px;
    gap: 6px;
    justify-content: center;
}

.mobile-move {
    border: 0;
    border-radius: 14px;
    background: #7c3aed;
    color: white;
    font-size: 27px;
    font-weight: 900;
    line-height: 1;
    box-shadow: 0 4px 0 #4c1d95;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
}

.mobile-move:active,
.mobile-move.pressed {
    transform: translateY(3px);
    box-shadow: 0 1px 0 #4c1d95;
    background: #5b21b6;
}

#move-up { grid-column: 2; grid-row: 1; }
#move-left { grid-column: 1; grid-row: 2; }
#move-down { grid-column: 2; grid-row: 2; }
#move-right { grid-column: 3; grid-row: 2; }

#mobile-hint {
    text-align: center;
    font-size: 11px;
    opacity: .72;
    margin-top: 7px;
}

@media (max-width: 700px) {

    #ks-wrap {
        width: 100%;
        padding: 0 2px;
        box-sizing: border-box;
    }

    #all-player-scoreboard {
        width: 98%;
        padding: 8px;
        margin-bottom: 10px;
    }

    .all-score-table {
        font-size: 10px;
    }

    #intro-panel {
        margin: 10px auto;
        padding: 18px 14px;
        font-size: 15px;
    }

    #intro-title {
        font-size: 22px;
        margin-bottom: 10px;
    }

    #intro-text {
        font-size: 15px;
        line-height: 1.5;
    }

    #game {
        width: 96vw;
        max-width: 100%;
        border-width: 2px;
        touch-action: none;
    }

    #controls {
        width: 98%;
        gap: 6px;
    }

    #controls button {
        min-width: 0;
        flex: 1 1 30%;
        padding: 9px 6px;
        font-size: 12px;
    }

    #mobile-controls {
        display: block;
    }

    #help {
        font-size: 11px;
        margin-top: 7px;
    }

    #help-card {
        width: 94vw;
        max-height: 86vh;
        overflow-y: auto;
        padding: 18px 16px;
    }

    #ks-title {

        font-size:
            20px;
    }

    #ks-status {

        font-size:
            12px;
    }

    #ks-letters {

        font-size:
            15px;

        letter-spacing:
            3px;
    }

    #guess-panel button {

        margin:
            8px 0 0;

        width:
            88%;
    }

}

</style>

<div id="ks-wrap">

<div id="all-player-scoreboard">
    <div class="all-score-title">🏆 Player scoreboard</div>
    <table class="all-score-table">
        <thead>
            <tr>
                <th>Player</th>
                <th>Games</th>
                <th>Wins</th>
                <th>Words</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>Bubbly</td>
                <td id="all-Bubbly-games">0</td>
                <td id="all-Bubbly-wins">0</td>
                <td id="all-Bubbly-words">0/3</td>
            </tr>
            <tr>
                <td>Tester1</td>
                <td id="all-Tester1-games">0</td>
                <td id="all-Tester1-wins">0</td>
                <td id="all-Tester1-words">0/3</td>
            </tr>
            <tr>
                <td>Tester2</td>
                <td id="all-Tester2-games">0</td>
                <td id="all-Tester2-wins">0</td>
                <td id="all-Tester2-words">0/3</td>
            </tr>
            <tr>
                <td>Tester3</td>
                <td id="all-Tester3-games">0</td>
                <td id="all-Tester3-wins">0</td>
                <td id="all-Tester3-words">0/3</td>
            </tr>
            <tr>
                <td>Tester4</td>
                <td id="all-Tester4-games">0</td>
                <td id="all-Tester4-wins">0</td>
                <td id="all-Tester4-words">0/3</td>
            </tr>
        </tbody>
    </table>
</div>

</div>

<!-- ======================================================
     INTRO SCREEN
     ====================================================== -->

<div id="intro-panel">

    <div id="intro-title">
        🏰 Welcome, Castle Explorer!
    </div>

    <div id="intro-text">

        Welcome to the ultimate prehistoric spell-off,
        where you run around collecting castles to snag
        secret letters and solve a hidden word!

        <br><br>

        Sounds simple, right?

        <br><br>

        Except there's a hungry dinosaur hot on your tail,
        fully convinced that
        &quot;legendary castle explorer&quot;
        is the top item on today's lunch menu.

    </div>

    <div id="intro-buttons">
        <button id="start-game">
            START GAME
        </button>

        <button id="help-game">
            HELP
        </button>
    </div>

</div>

<div id="help-modal">
    <div id="help-card">
        <h3>🎮 How to play</h3>

        <p>
            You are the <strong>green dog</strong>.
            Your job is to explore the playground while the
            <strong>red dinosaur</strong> chases you.
        </p>

        <p>
            Around the maze you will find <strong> castles</strong>.
            Walk into a castle to collect it and reveal one hidden character.
        </p>

        <p>
            The playground also contains <strong>portals</strong>.
            Matching letters show which portal connects to which.
            <strong>Purple = IN</strong> and <strong>blue = OUT</strong>.
        </p>

        <p>
            After you visit every castle, you will be asked to solve the secret.
            The answer can be a <strong>word</strong>, a <strong>phrase</strong>,
            or a <strong>name</strong>.
        </p>

        <p>
            Move with <strong>Arrow Keys</strong> or <strong>WASD</strong>.
            Press <strong>SPACE</strong> to pause or resume.
        </p>

        <button id="close-help">
            GOT IT
        </button>
    </div>
</div>

<!-- ======================================================
     GAME AREA
     ====================================================== -->

<div
    id="game-area"
    style="display:none;"
>

<div id="ks-header">

    <div id="ks-title">
        🏖️ Game Testing 🏰
    </div>

    <div id="ks-status">
    </div>

    <div id="ks-letters">
    </div>

</div>

<div id="game-shell">

    <canvas id="game">
    </canvas>

</div>

<div id="controls">

    <button id="restart">
        Restart Game
    </button>

    <button id="pause">
        Pause / Resume (SPACE)
    </button>

    <button id="help-game-live">
        Help
    </button>

</div>

<div id="mobile-controls" aria-label="Mobile movement controls">
    <div class="mobile-pad">
        <button class="mobile-move" id="move-up" aria-label="Move up">▲</button>
        <button class="mobile-move" id="move-left" aria-label="Move left">◀</button>
        <button class="mobile-move" id="move-down" aria-label="Move down">▼</button>
        <button class="mobile-move" id="move-right" aria-label="Move right">▶</button>
    </div>
    <div id="mobile-hint">Tap the arrows or swipe directly on the playground</div>
</div>

<div id="help">

    Move with Arrow Keys / WASD / touch controls
    • SPACE pauses
    • Purple portal = IN
    • Blue portal = OUT

</div>

<div id="guess-panel">

    <h3>
        🦖😢 NOOO! YOU GOT ALL THE CASTLES!
    </h3>

    <div id="guess-text">
        My snack escaped...
        Fine. Guess the word or phrase!
    </div>

    <div
        id="guess-rule"
        style="
            margin-top:8px;
            font-weight:800;
            color:#f8fafc;
        "
    >
    </div>

    <div
        style="
            margin:10px 0;
            font-weight:800
        "
        id="found-letters"
    >
    </div>

    <input
        id="guess-input"
        maxlength="40"
        placeholder="Type the hidden word or phrase..."
    />

    <button id="guess-button">
        GUESS
    </button>

    <div id="guess-feedback">
    </div>

</div>

</div>

</div>

<script>

(() => {

/* ============================================================
   SETUP
   ============================================================ */

const ROOT =
    document.getElementById(
        "ks-root"
    );

if (
    ROOT.dataset.ready === "1"
) {
    return;
}

ROOT.dataset.ready = "1";

const CURRENT_USER = __CURRENT_USER_JSON__;
const SUPABASE_URL = __SUPABASE_URL_JSON__;
const SUPABASE_PUBLIC_KEY = __SUPABASE_PUBLIC_KEY_JSON__;

const KNOWN_PLAYERS = [
    "Bubbly",
    "Tester1",
    "Tester2",
    "Tester3",
    "Tester4"
];

function emptyStats() {
    return { games: 0, wins: 0, winningWords: [] };
}

function normaliseStats(row) {
    return {
        games: Number(row?.games || 0),
        wins: Number(row?.wins || 0),
        winningWords: Array.isArray(row?.solved_words)
            ? row.solved_words
            : []
    };
}

let playerStats = emptyStats();
let allPlayerStats = {};
let supabaseReady = Boolean(SUPABASE_URL && SUPABASE_PUBLIC_KEY);
let initialStatsLoaded = false;
let initialStatsPromise = null;

function supabaseHeaders(extra = {}) {
    return {
        // New Supabase publishable keys belong in the apikey header.
        "apikey": SUPABASE_PUBLIC_KEY,
        ...extra
    };
}

async function fetchAllPlayerStats() {
    if (!supabaseReady) return {};

    const response = await fetch(
        `${SUPABASE_URL}/rest/v1/game_stats?select=username,games,wins,solved_words`,
        {
            method: "GET",
            headers: supabaseHeaders({
                "Accept": "application/json"
            })
        }
    );

    if (!response.ok) {
        throw new Error(`Supabase read failed: ${response.status}`);
    }

    const rows = await response.json();
    const result = {};

    for (const row of rows) {
        result[row.username] = normaliseStats(row);
    }

    return result;
}

async function ensurePlayerStatsLoaded() {
    if (initialStatsLoaded) return;

    if (!initialStatsPromise) {
        initialStatsPromise = (async () => {
            try {
                const remoteStats = await fetchAllPlayerStats();
                allPlayerStats = remoteStats;

                if (allPlayerStats[CURRENT_USER]) {
                    playerStats = {
                        games: allPlayerStats[CURRENT_USER].games,
                        wins: allPlayerStats[CURRENT_USER].wins,
                        winningWords: [
                            ...allPlayerStats[CURRENT_USER].winningWords
                        ]
                    };
                }
            } catch (err) {
                console.error(err);
            } finally {
                initialStatsLoaded = true;
            }
        })();
    }

    await initialStatsPromise;
}

async function updateAllPlayerScoreboard() {
    try {
        const remoteStats = await fetchAllPlayerStats();

        if (Object.keys(remoteStats).length) {
            allPlayerStats = remoteStats;
        }
        initialStatsLoaded = true;

        if (allPlayerStats[CURRENT_USER]) {
            playerStats = {
                games: allPlayerStats[CURRENT_USER].games,
                wins: allPlayerStats[CURRENT_USER].wins,
                winningWords: [...allPlayerStats[CURRENT_USER].winningWords]
            };
        }
    } catch (err) {
        console.error(err);
    }

    for (const username of KNOWN_PLAYERS) {
        const stats = allPlayerStats[username] || emptyStats();

        const gamesEl = document.getElementById(
            `all-${username}-games`
        );
        const winsEl = document.getElementById(
            `all-${username}-wins`
        );
        const wordsEl = document.getElementById(
            `all-${username}-words`
        );

        if (gamesEl) gamesEl.textContent = stats.games;
        if (winsEl) winsEl.textContent = stats.wins;
        if (wordsEl) {
            wordsEl.textContent =
                `${stats.winningWords.length}/${WORD_OPTIONS.length}`;
        }
    }
}

function updateScoreboard() {
    updateAllPlayerScoreboard();
}

async function savePlayerStats() {
    allPlayerStats[CURRENT_USER] = {
        games: playerStats.games,
        wins: playerStats.wins,
        winningWords: [...playerStats.winningWords]
    };

    // Update the UI immediately, then persist online.
    for (const username of KNOWN_PLAYERS) {
        const stats = allPlayerStats[username] || emptyStats();
        const gamesEl = document.getElementById(`all-${username}-games`);
        const winsEl = document.getElementById(`all-${username}-wins`);
        const wordsEl = document.getElementById(`all-${username}-words`);

        if (gamesEl) gamesEl.textContent = stats.games;
        if (winsEl) winsEl.textContent = stats.wins;
        if (wordsEl) {
            wordsEl.textContent =
                `${stats.winningWords.length}/${WORD_OPTIONS.length}`;
        }
    }

    if (!supabaseReady) {
        console.error("Supabase is not configured.");
        return;
    }

    try {
        const response = await fetch(
            `${SUPABASE_URL}/rest/v1/game_stats?on_conflict=username`,
            {
                method: "POST",
                headers: supabaseHeaders({
                    "Content-Type": "application/json",
                    "Prefer": "resolution=merge-duplicates,return=representation"
                }),
                body: JSON.stringify({
                    username: CURRENT_USER,
                    games: playerStats.games,
                    wins: playerStats.wins,
                    solved_words: playerStats.winningWords
                })
            }
        );

        if (!response.ok) {
            const details = await response.text();
            throw new Error(
                `Supabase save failed: ${response.status} ${details}`
            );
        }
    } catch (err) {
        console.error(err);
    }
}

async function recordGameStart() {
    // Never overwrite existing online history with zeros if the player
    // clicks START before the first scoreboard request finishes.
    await ensurePlayerStatsLoaded();
    playerStats.games += 1;
    await savePlayerStats();
}

async function recordWin() {
    await ensurePlayerStatsLoaded();
    playerStats.wins += 1;

    if (!playerStats.winningWords.includes(WORD)) {
        playerStats.winningWords.push(WORD);
    }

    await savePlayerStats();
}

const WORD_OPTIONS = [
    "Testing",
    "Res non verba",
    "P!nk"
];

// Load the shared scoreboard from Supabase when the game opens.
updateScoreboard();

// Keep the scoreboard fresh if another player is playing elsewhere.
setInterval(
    updateAllPlayerScoreboard,
    15000
);

let WORD = WORD_OPTIONS[0];
let PLAYABLE_LETTERS = [];
let previousWord = null;

const CELL = 30;
const SPEED = 135;

/* ============================================================
   MAZE
   One base maze + mirrored variants.
   Every round randomly selects one layout.
   ============================================================ */

const BASE_MAZE_STR = [
    "11111111111111111111111111111111111111111",
    "10000000000000000000100000000000000000001",
    "10111101111101111110101111101111101111101",
    "10000101000001000000100000101000001000001",
    "11110101011111011111111110101011111011111",
    "10000100010000000000100000100010000000001",
    "10111111010111111110101111111010111111001",
    "10000000010000000000100000000010000000001",
    "10111101111101111110111110111111101111101",
    "10000100000001000000000000100000001000001",
    "11110111111001011111111110101111111011111",
    "10000100001000010000000000100010000000001",
    "10111101001111110111111110111010111111001",
    "10000001000000000100000000100010000000001",
    "10111111111101111110111111101111111111101",
    "10000000000100000000100000001000000000001",
    "11111101110111111110101111111011101111111",
    "10000001000100000000100000000000100000001",
    "10111111011101111111111110111110111111001",
    "10000000010000000000100000100000100000001",
    "10111101111111101110101111101111101111101",
    "10000100000000001000100000000000001000001",
    "11110111111111111011111111111111111011111",
    "10000000000000000000000000000000000000001",
    "11111111111111111111111111111111111111111"
];

const ROWS = BASE_MAZE_STR.length;
const COLS = BASE_MAZE_STR[0].length;

const BASE_PLAYER_START = [23, 2];
const BASE_DINO_START = [1, 39];

const BASE_PORTALS = {
    A: [[1, 3], [23, 37]],
    B: [[5, 38], [19, 2]],
    C: [[17, 38], [3, 2]],
    D: [[23, 20], [1, 20]]
};

const MAZE_VARIANTS = [
    "normal",
    "mirrorX",
    "mirrorY",
    "rotate180"
];

let MAZE = [];
let PLAYER_START = [...BASE_PLAYER_START];
let DINO_START = [...BASE_DINO_START];
let PORTALS = {};
let CURRENT_MAZE_VARIANT = "normal";

function transformPos(pos, variant) {
    const [r, c] = pos;

    if (variant === "mirrorX") {
        return [r, COLS - 1 - c];
    }
    if (variant === "mirrorY") {
        return [ROWS - 1 - r, c];
    }
    if (variant === "rotate180") {
        return [ROWS - 1 - r, COLS - 1 - c];
    }
    return [r, c];
}

function buildMaze(variant) {
    let rows = [...BASE_MAZE_STR];

    if (variant === "mirrorX" || variant === "rotate180") {
        rows = rows.map(row => [...row].reverse().join(""));
    }
    if (variant === "mirrorY" || variant === "rotate180") {
        rows = [...rows].reverse();
    }

    return rows.map(row => [...row].map(Number));
}

function applyRandomMaze() {
    CURRENT_MAZE_VARIANT =
        MAZE_VARIANTS[
            Math.floor(Math.random() * MAZE_VARIANTS.length)
        ];

    MAZE = buildMaze(CURRENT_MAZE_VARIANT);
    PLAYER_START = transformPos(BASE_PLAYER_START, CURRENT_MAZE_VARIANT);
    DINO_START = transformPos(BASE_DINO_START, CURRENT_MAZE_VARIANT);

    PORTALS = {};
    for (const [label, pair] of Object.entries(BASE_PORTALS)) {
        PORTALS[label] = [
            transformPos(pair[0], CURRENT_MAZE_VARIANT),
            transformPos(pair[1], CURRENT_MAZE_VARIANT)
        ];
    }
}

/* ============================================================
   RANDOM WORD / PHRASE + RANDOM CASTLES
   Spaces do NOT need castles.
   Every other character DOES, including punctuation such as !.
   ============================================================ */

function chooseRandomWord() {
    let choices = WORD_OPTIONS;

    if (previousWord !== null && WORD_OPTIONS.length > 1) {
        choices = WORD_OPTIONS.filter(word => word !== previousWord);
    }

    WORD = choices[Math.floor(Math.random() * choices.length)];
    previousWord = WORD;
    PLAYABLE_LETTERS = [...WORD].filter(ch => ch !== " ");
}

function allPortalKeys() {
    const keys = new Set();
    for (const pair of Object.values(PORTALS)) {
        keys.add(keyOf(pair[0]));
        keys.add(keyOf(pair[1]));
    }
    return keys;
}

function manhattan(a, b) {
    return Math.abs(a[0] - b[0]) + Math.abs(a[1] - b[1]);
}

function randomCastlePositions(count) {
    const portalKeys = allPortalKeys();

    const candidates = [];
    for (let r = 1; r < ROWS - 1; r++) {
        for (let c = 1; c < COLS - 1; c++) {
            if (MAZE[r][c] !== 0) {
                continue;
            }

            const p = [r, c];
            const k = keyOf(p);

            if (portalKeys.has(k)) {
                continue;
            }
            if (samePos(p, PLAYER_START) || samePos(p, DINO_START)) {
                continue;
            }

            // Keep castles away from the starting characters.
            if (manhattan(p, PLAYER_START) < 5) {
                continue;
            }
            if (manhattan(p, DINO_START) < 5) {
                continue;
            }

            candidates.push(p);
        }
    }

    // Try several times to obtain a nicely spread-out set.
    for (let attempt = 0; attempt < 300; attempt++) {
        const pool = shuffle(candidates);
        const chosen = [];

        for (const p of pool) {
            const farEnough =
                chosen.every(other => manhattan(p, other) >= 5);

            if (farEnough) {
                chosen.push(p);
            }

            if (chosen.length === count) {
                return chosen;
            }
        }
    }

    // Fallback: slightly relax the spacing if a future long phrase
    // needs more castles than the strict rule can fit.
    for (let minDistance = 4; minDistance >= 2; minDistance--) {
        const pool = shuffle(candidates);
        const chosen = [];

        for (const p of pool) {
            if (chosen.every(other => manhattan(p, other) >= minDistance)) {
                chosen.push(p);
            }
            if (chosen.length === count) {
                return chosen;
            }
        }
    }

    return shuffle(candidates).slice(0, count);
}

let CASTLE_POSITIONS = [];

/* ============================================================
   HTML ELEMENTS
   ============================================================ */

const canvas =
    document.getElementById(
        "game"
    );

const ctx =
    canvas.getContext(
        "2d"
    );

canvas.width =
    COLS * CELL;

canvas.height =
    ROWS * CELL;

const statusEl =
    document.getElementById(
        "ks-status"
    );

const lettersEl =
    document.getElementById(
        "ks-letters"
    );

const guessPanel =
    document.getElementById(
        "guess-panel"
    );

const guessInput =
    document.getElementById(
        "guess-input"
    );

const guessButton =
    document.getElementById(
        "guess-button"
    );

const guessFeedback =
    document.getElementById(
        "guess-feedback"
    );

const foundLetters =
    document.getElementById(
        "found-letters"
    );

const guessRule =
    document.getElementById(
        "guess-rule"
    );

const introPanel =
    document.getElementById(
        "intro-panel"
    );

const gameArea =
    document.getElementById(
        "game-area"
    );

const startGameButton =
    document.getElementById(
        "start-game"
    );

const helpGameButton =
    document.getElementById(
        "help-game"
    );

const helpGameLiveButton =
    document.getElementById(
        "help-game-live"
    );

const helpModal =
    document.getElementById(
        "help-modal"
    );

const closeHelpButton =
    document.getElementById(
        "close-help"
    );

/* ============================================================
   GAME VARIABLES
   ============================================================ */

let timer =
    null;

let guessTimer =
    null;

let state =
    {};

let fireworks =
    [];

let fireworkFrame =
    0;

let fireworkTimer =
    null;

let openingCountdownTimer =
    null;

let openingCountdownFinish =
    null;

/* ============================================================
   UTILITIES
   ============================================================ */

function keyOf(pos) {

    return (
        `${pos[0]},${pos[1]}`
    );

}

function shuffle(arr) {

    const a =
        [...arr];

    for (
        let i =
            a.length - 1;

        i > 0;

        i--
    ) {

        const j =
            Math.floor(
                Math.random() *
                (i + 1)
            );

        [
            a[i],
            a[j]
        ] = [
            a[j],
            a[i]
        ];

    }

    return a;

}

/* ============================================================
   RESET
   ============================================================ */

function resetGame(
    beginNow = true
) {

    if (timer) {

        clearInterval(
            timer
        );

        timer =
            null;
    }

    if (guessTimer) {

        clearTimeout(
            guessTimer
        );

        guessTimer =
            null;
    }

    if (openingCountdownTimer) {

        clearInterval(
            openingCountdownTimer
        );

        openingCountdownTimer =
            null;
    }

    if (openingCountdownFinish) {

        clearTimeout(
            openingCountdownFinish
        );

        openingCountdownFinish =
            null;
    }

    stopFireworks();

    applyRandomMaze();
    chooseRandomWord();

    CASTLE_POSITIONS =
        randomCastlePositions(
            PLAYABLE_LETTERS.length
        );

    const shuffled =
        shuffle(
            PLAYABLE_LETTERS
        );

    const letterMap = {};

    CASTLE_POSITIONS.forEach(
        (p, i) => {
            letterMap[keyOf(p)] = shuffled[i];
        }
    );

    state = {

        gameOver:
            false,

        awaitingGuess:
            false,

        won:
            false,

        score:
            0,

        paused:
            false,

        countdownActive:
            false,

        countdownValue:
            null,

        player:
            [...PLAYER_START],

        playerDir:
            [0, 0],

        nextDir:
            [0, 0],

        dino:
            [...DINO_START],

        dinoTick:
            0,

        castles:
            new Set(
                CASTLE_POSITIONS.map(
                    keyOf
                )
            ),

        castleLetters:
            letterMap,

        collected:
            [],

        portalCooldown:
            0,

        lastEvent:
            "Find all letters in the castles!"

    };

    guessPanel.style.display =
        "none";

    guessFeedback.textContent =
        "";

    guessInput.value =
        "";

    render();

    if (beginNow) {

        startOpeningCountdown();

    }

}

/* ============================================================
   WALL CHECK
   ============================================================ */

function isWall(
    r,
    c
) {

    return (

        r < 0 ||

        r >= ROWS ||

        c < 0 ||

        c >= COLS ||

        MAZE[r][c] === 1

    );

}

function samePos(
    a,
    b
) {

    return (

        a[0] === b[0] &&

        a[1] === b[1]

    );

}

/* ============================================================
   PLAYER MOVEMENT
   ============================================================ */

function movePlayer() {

    let nr =
        state.player[0] +
        state.nextDir[0];

    let nc =
        state.player[1] +
        state.nextDir[1];

    if (
        !isWall(
            nr,
            nc
        )
    ) {

        state.playerDir =
            [...state.nextDir];

    }

    nr =
        state.player[0] +
        state.playerDir[0];

    nc =
        state.player[1] +
        state.playerDir[1];

    if (
        !isWall(
            nr,
            nc
        )
    ) {

        state.player =
            [nr, nc];

    }

    checkPortal();

    checkCastle();

    checkCollision();

}

/* ============================================================
   PORTALS
   ============================================================ */

function checkPortal() {

    if (
        state.portalCooldown > 0
    ) {

        return;

    }

    for (
        const [
            label,
            pair
        ]
        of
        Object.entries(
            PORTALS
        )
    ) {

        const entry =
            pair[0];

        const exit =
            pair[1];

        if (
            samePos(
                state.player,
                entry
            )
        ) {

            state.player =
                [...exit];

            state.portalCooldown =
                4;

            state.lastEvent =
                `🌀 Portal ${label}: purple IN → blue OUT`;

            return;

        }

    }

}

/* ============================================================
   CASTLE COLLECTION
   ============================================================ */

function checkCastle() {

    const k =
        keyOf(
            state.player
        );

    if (
        !state.castles.has(k)
    ) {

        return;

    }

    const letter =
        state.castleLetters[k];

    state.castles.delete(k);

    state.collected.push(
        letter
    );

    state.score +=
        250;

    state.lastEvent =
        `🏰 Castle opened — letter: ${letter}`;

    if (
        state.castles.size === 0
    ) {

        state.playerDir =
            [0, 0];

        state.nextDir =
            [0, 0];

        state.awaitingGuess =
            true;

        state.lastEvent =
            "🦖😢 NOOO! You got all the castles...";

        /*
        Show the guess panel almost immediately.
        */

        guessTimer =
            setTimeout(
                () => {

                    if (
                        !state.gameOver &&
                        state.awaitingGuess
                    ) {

                        showGuessPanel();

                    }

                },
                700
            );

    }

}

/* ============================================================
   NEIGHBOURS
   ============================================================ */

function getNeighbors(
    pos,
    includePortals = true
) {

    const [
        r,
        c
    ] = pos;

    const out =
        [];

    for (
        const [
            dr,
            dc
        ]
        of
        [
            [-1, 0],
            [1, 0],
            [0, -1],
            [0, 1]
        ]
    ) {

        const nr =
            r + dr;

        const nc =
            c + dc;

        if (
            !isWall(
                nr,
                nc
            )
        ) {

            out.push(
                [nr, nc]
            );

        }

    }

    if (
        includePortals
    ) {

        for (
            const pair
            of
            Object.values(
                PORTALS
            )
        ) {

            if (
                samePos(
                    pos,
                    pair[0]
                )
            ) {

                out.push(
                    [...pair[1]]
                );

            }

        }

    }

    return out;

}

/* ============================================================
   BFS PATH FINDING
   ============================================================ */

function bfsNextStep(
    start,
    target
) {

    if (
        samePos(
            start,
            target
        )
    ) {

        return [...start];

    }

    const q =
        [[...start]];

    const prev =
        new Map();

    prev.set(
        keyOf(start),
        null
    );

    let found =
        false;

    while (
        q.length
    ) {

        const cur =
            q.shift();

        if (
            samePos(
                cur,
                target
            )
        ) {

            found =
                true;

            break;

        }

        for (
            const nxt
            of
            getNeighbors(
                cur,
                true
            )
        ) {

            const k =
                keyOf(nxt);

            if (
                !prev.has(k)
            ) {

                prev.set(
                    k,
                    cur
                );

                q.push(
                    nxt
                );

            }

        }

    }

    if (
        !found &&
        !prev.has(
            keyOf(target)
        )
    ) {

        return [...start];

    }

    let step =
        [...target];

    let parent =
        prev.get(
            keyOf(step)
        );

    if (
        parent === undefined
    ) {

        return [...start];

    }

    while (
        parent &&
        !samePos(
            parent,
            start
        )
    ) {

        step =
            [...parent];

        parent =
            prev.get(
                keyOf(step)
            );

    }

    return step;

}

/* ============================================================
   PREDICT PLAYER MOVEMENT
   ============================================================ */

function predictPlayerTarget() {

    let target =
        [...state.player];

    const [
        dr,
        dc
    ] =
        state.playerDir;

    for (
        let i = 0;
        i < 3;
        i++
    ) {

        const nr =
            target[0] + dr;

        const nc =
            target[1] + dc;

        if (
            isWall(
                nr,
                nc
            )
        ) {

            break;

        }

        target =
            [nr, nc];

    }

    return target;

}

/* ============================================================
   DINOSAUR AI
   ============================================================ */

function moveDino() {

    state.dinoTick +=
        1;

    /*
    Dino skips every fourth move.
    Player therefore has a slight
    speed advantage.
    */

    if (
        state.dinoTick % 4 === 0
    ) {

        return;

    }

    const start =
        [...state.dino];

    const player =
        [...state.player];

    const predicted =
        predictPlayerTarget();

    const manhattan =

        Math.abs(
            start[0] -
            player[0]
        )

        +

        Math.abs(
            start[1] -
            player[1]
        );

    const target =

        manhattan <= 7

        ?

        player

        :

        predicted;

    let next =
        bfsNextStep(
            start,
            target
        );

    if (
        samePos(
            next,
            start
        )

        &&

        !samePos(
            start,
            player
        )
    ) {

        next =
            bfsNextStep(
                start,
                player
            );

    }

    state.dino =
        [...next];

    /*
    Dino can use portals too.
    */

    for (
        const pair
        of
        Object.values(
            PORTALS
        )
    ) {

        if (
            samePos(
                state.dino,
                pair[0]
            )
        ) {

            state.dino =
                [...pair[1]];

            break;

        }

    }

    checkCollision();

}

/* ============================================================
   COLLISION
   ============================================================ */

function checkCollision() {

    if (
        state.awaitingGuess ||
        state.gameOver
    ) {

        return;

    }

    if (
        samePos(
            state.player,
            state.dino
        )
    ) {

        state.gameOver =
            true;

        state.won =
            false;

        state.playerDir =
            [0, 0];

        state.nextDir =
            [0, 0];

        state.lastEvent =
            "🦖 NOM NOM... you were delicious!";

    }

}

/* ============================================================
   INITIAL 3-2-1-GO COUNTDOWN
   ============================================================ */

function startOpeningCountdown() {

    if (timer) {

        clearInterval(
            timer
        );

        timer =
            null;

    }

    if (openingCountdownTimer) {

        clearInterval(
            openingCountdownTimer
        );

    }

    if (openingCountdownFinish) {

        clearTimeout(
            openingCountdownFinish
        );

    }

    state.paused =
        true;

    state.countdownActive =
        true;

    state.countdownValue =
        3;

    state.lastEvent =
        "Get ready...";

    render();

    openingCountdownTimer =
        setInterval(
            () => {

                if (
                    state.countdownValue > 1
                ) {

                    state.countdownValue -=
                        1;

                    render();

                    return;

                }

                if (
                    state.countdownValue === 1
                ) {

                    state.countdownValue =
                        "GO!";

                    state.lastEvent =
                        "GO! 🐶💨";

                    render();

                    return;

                }

                clearInterval(
                    openingCountdownTimer
                );

                openingCountdownTimer =
                    null;

            },
            850
        );

    openingCountdownFinish =
        setTimeout(
            () => {

                if (
                    openingCountdownTimer
                ) {

                    clearInterval(
                        openingCountdownTimer
                    );

                    openingCountdownTimer =
                        null;

                }

                state.countdownActive =
                    false;

                state.countdownValue =
                    null;

                state.paused =
                    false;

                state.lastEvent =
                    "Visit all castles!";

                render();

                timer =
                    setInterval(
                        gameLoop,
                        SPEED
                    );

                ROOT.focus();

            },
            3400
        );

}

/* ============================================================
   PAUSE
   ============================================================ */

function pauseGame() {

    if (
        state.gameOver ||
        state.awaitingGuess ||
        state.countdownActive
    ) {

        return;

    }

    if (
        !state.paused
    ) {

        state.paused =
            true;

        state.playerDir =
            [0, 0];

        state.nextDir =
            [0, 0];

        state.lastEvent =
            "🐾 Pawsing the Claws...";

        render();

    }

    else {

        startCountdown();

    }

}

/* ============================================================
   PAUSE RESUME COUNTDOWN
   ============================================================ */

function startCountdown() {

    if (
        !state.paused ||
        state.countdownActive
    ) {

        return;

    }

    state.countdownActive =
        true;

    state.countdownValue =
        3;

    state.lastEvent =
        "Get ready...";

    render();

    const countdown =
        setInterval(
            () => {

                state.countdownValue -=
                    1;

                if (
                    state.countdownValue <= 0
                ) {

                    clearInterval(
                        countdown
                    );

                    state.countdownActive =
                        false;

                    state.countdownValue =
                        null;

                    state.paused =
                        false;

                    state.lastEvent =
                        "GO! 🐶💨";

                    render();

                    ROOT.focus();

                    return;

                }

                render();

            },
            1000
        );

}

/* ============================================================
   LETTER HELPERS
   ============================================================ */

function counts(s) {

    const m =
        {};

    for (
        const ch
        of s
    ) {

        m[ch] =
            (m[ch] || 0) + 1;

    }

    return m;

}

function sameCounts(
    a,
    b
) {

    const ca =
        counts(a);

    const cb =
        counts(b);

    const keys =
        new Set(
            [
                ...Object.keys(ca),
                ...Object.keys(cb)
            ]
        );

    for (
        const k
        of keys
    ) {

        if (
            (ca[k] || 0)
            !==
            (cb[k] || 0)
        ) {

            return false;

        }

    }

    return true;

}

/* ============================================================
   GUESS PANEL
   ============================================================ */

function showGuessPanel() {

    guessRule.textContent =
        `Use all ${PLAYABLE_LETTERS.length} characters to finish the game.`;

    foundLetters.textContent =
        "Letters you found: "
        +
        state.collected.join(
            "   "
        );

    guessPanel.style.display =
        "block";

    guessFeedback.textContent =
        "";

    guessInput.value =
        "";

    guessInput.focus();

    requestAnimationFrame(() => {
        guessPanel.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });
    });

}

/* ============================================================
   GUESS WORD
   ============================================================ */

function normalizedSpacing(s) {
    return s
        .trim()
        .replace(/\s+/g, " ");
}

function answerMatches(rawGuess) {
    const guess = normalizedSpacing(rawGuess);
    const answer = normalizedSpacing(WORD);

    // P!nk is deliberately case-sensitive:
    // correct = P!nk
    // wrong   = p!nk, P!NK, etc.
    if (WORD === "P!nk") {
        return guess === answer;
    }

    // The other words/phrases are case-insensitive.
    return guess.toLocaleLowerCase() === answer.toLocaleLowerCase();
}

function playableOnly(s) {
    return [...normalizedSpacing(s)]
        .filter(ch => ch !== " ")
        .join("");
}

function submitGuess() {
    const rawGuess = guessInput.value;

    if (answerMatches(rawGuess)) {
        state.awaitingGuess = false;
        state.gameOver = true;
        state.won = true;
        state.score += 1000;
        state.lastEvent = `🎉 CORRECT! ${WORD}!`;

        recordWin();

        guessPanel.style.display = "none";
        render();

        // Move the view back to the game before the fireworks start.
        requestAnimationFrame(() => {
            canvas.scrollIntoView({
                behavior: "smooth",
                block: "center"
            });
        });

        setTimeout(() => {
            startFireworks();
        }, 350);

        return;
    }

    const collected = state.collected.join("");
    const guessedPlayable = playableOnly(rawGuess);
    const collectedPlayable = playableOnly(collected);

    const comparableGuess =
        WORD === "P!nk"
            ? guessedPlayable
            : guessedPlayable.toLocaleLowerCase();

    const comparableCollected =
        WORD === "P!nk"
            ? collectedPlayable
            : collectedPlayable.toLocaleLowerCase();

    if (!sameCounts(comparableGuess, comparableCollected)) {
        guessFeedback.textContent =
            "🦖 RAWR! Sneaky characters? " +
            `Use only the ${PLAYABLE_LETTERS.length} characters you actually found: ` +
            state.collected.join(" ");

        guessFeedback.style.color = "#fbbf24";
    } else if (
        WORD === "P!nk" &&
        normalizedSpacing(rawGuess) !== "P!nk"
    ) {
        guessFeedback.textContent =
            "Almost! For this one capitalization matters: P is uppercase, n and k are lowercase — and don't forget !";
        guessFeedback.style.color = "#fbbf24";
    } else {
        guessFeedback.textContent =
            "🦖 Whomp, whomp... Better luck next time! 😋";
        guessFeedback.style.color = "#ff6b6b";
    }

    guessInput.value = "";
    guessInput.focus();
}

/* ============================================================
   GAME LOOP
   ============================================================ */

function gameLoop() {

    if (

        !state.gameOver

        &&

        !state.awaitingGuess

        &&

        !state.paused

        &&

        !state.countdownActive

    ) {

        if (
            state.portalCooldown > 0
        ) {

            state.portalCooldown -=
                1;

        }

        movePlayer();

        if (
            !state.gameOver &&
            !state.awaitingGuess
        ) {

            moveDino();

        }

    }

    render();

}

/* ============================================================
   TEXT LABELS
   ============================================================ */

function answerPattern() {
    let collectedIndex = 0;

    return [...WORD]
        .map(ch => {
            if (ch !== " ") {
                if (collectedIndex < state.collected.length) {
                    return state.collected[collectedIndex++];
                }
                collectedIndex++;
                return "_";
            }

            // Spaces are shown automatically and do not need castles.
            return "   ";
        })
        .join(" ");
}

function updateLabels() {
    const total = PLAYABLE_LETTERS.length;
    const found = total - state.castles.size;

    statusEl.textContent =
        `Castles ${found}/${total}` +
        `   •   Score ${state.score}` +
        `   •   ${state.lastEvent}`;

    lettersEl.textContent =
        "Letters:   " + answerPattern();
}

/* ============================================================
   DRAW HELPERS
   ============================================================ */

function drawRect(
    x,
    y,
    w,
    h,
    fill,
    stroke = null,
    sw = 1
) {

    ctx.fillStyle =
        fill;

    ctx.fillRect(
        x,
        y,
        w,
        h
    );

    if (
        stroke
    ) {

        ctx.strokeStyle =
            stroke;

        ctx.lineWidth =
            sw;

        ctx.strokeRect(
            x,
            y,
            w,
            h
        );

    }

}

/* ============================================================
   DRAW PORTAL
   ============================================================ */

function drawPortal(
    pos,
    label,
    entry
) {

    const [
        r,
        c
    ] =
        pos;

    const cx =
        c * CELL +
        CELL / 2;

    const cy =
        r * CELL +
        CELL / 2;

    ctx.beginPath();

    ctx.arc(
        cx,
        cy,
        14,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =

        entry

        ?

        "#7c3aed"

        :

        "#0284c7";

    ctx.fill();

    ctx.strokeStyle =

        entry

        ?

        "#e9d5ff"

        :

        "#bae6fd";

    ctx.lineWidth =
        3;

    ctx.stroke();

    ctx.beginPath();

    ctx.arc(
        cx,
        cy,
        9,
        0,
        Math.PI * 2
    );

    ctx.strokeStyle =
        "white";

    ctx.lineWidth =
        1;

    ctx.stroke();

    ctx.textAlign =
        "center";

    ctx.fillStyle =
        "white";

    ctx.font =
        "bold 12px Arial";

    ctx.fillText(
        label,
        cx,
        cy + 2
    );

    ctx.font =
        "bold 6px Arial";

    ctx.fillText(
        entry
        ?
        "IN"
        :
        "OUT",

        cx,

        cy + 11
    );

}

/* ============================================================
   DRAW CASTLE
   ============================================================ */

function drawCastle(pos) {

    const [
        r,
        c
    ] =
        pos;

    const cx =
        c * CELL +
        CELL / 2;

    const cy =
        r * CELL +
        CELL / 2;

    ctx.beginPath();

    ctx.arc(
        cx,
        cy,
        14,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =
        "#fde68a";

    ctx.fill();

    ctx.strokeStyle =
        "#f59e0b";

    ctx.lineWidth =
        2;

    ctx.stroke();

    drawRect(
        cx - 10,
        cy - 3,
        20,
        12,
        "#d6a24b",
        "#7c4a16"
    );

    drawRect(
        cx - 11,
        cy - 10,
        7,
        8,
        "#d6a24b",
        "#7c4a16"
    );

    drawRect(
        cx + 4,
        cy - 10,
        7,
        8,
        "#d6a24b",
        "#7c4a16"
    );

    drawRect(
        cx - 3,
        cy + 3,
        6,
        6,
        "#7c4a16"
    );

}

/* ============================================================
   DRAW PLAYER - RED DOG
   ============================================================ */

function drawPlayer() {

    const [r, c] = state.player;
    const cx = c * CELL + CELL / 2;
    const cy = r * CELL + CELL / 2;

    /* LEFT EAR */

    ctx.beginPath();

    ctx.ellipse(
        cx - 11,
        cy - 2,
        6,
        10,
        -.25,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =
        "#15803d";

    ctx.fill();

    /* RIGHT EAR */

    ctx.beginPath();

    ctx.ellipse(
        cx + 11,
        cy - 2,
        6,
        10,
        .25,
        0,
        Math.PI * 2
    );

    ctx.fill();

    /* HEAD */

    ctx.beginPath();

    ctx.arc(
        cx,
        cy,
        13,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =
        "#22c55e";

    ctx.fill();

    ctx.strokeStyle =
        "#bbf7d0";

    ctx.lineWidth =
        2;

    ctx.stroke();

    /* MUZZLE */

    ctx.beginPath();

    ctx.ellipse(
        cx,
        cy + 5,
        8,
        6,
        0,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =
        "#dcfce7";

    ctx.fill();

    /* EYES */

    ctx.beginPath();

    ctx.arc(
        cx - 5,
        cy - 4,
        2,
        0,
        Math.PI * 2
    );

    ctx.arc(
        cx + 5,
        cy - 4,
        2,
        0,
        Math.PI * 2
    );

    ctx.fillStyle =
        "#111827";

    ctx.fill();

    /* NOSE */

    ctx.beginPath();

    ctx.ellipse(
        cx,
        cy + 2,
        3,
        2.5,
        0,
        0,
        Math.PI * 2
    );

    ctx.fill();

}

/* ============================================================
   DRAW DINOSAUR
   ============================================================ */

function drawDino() {

    const [
        r,
        c
    ] =
        state.dino;

    const cx =
        c * CELL +
        CELL / 2;

    const cy =
        r * CELL +
        CELL / 2;

    ctx.fillStyle =
        "#ef4444";

    ctx.strokeStyle =
        "#fca5a5";

    ctx.lineWidth =
        2;

    ctx.beginPath();

    ctx.arc(
        cx,
        cy - 1,
        14,
        Math.PI,
        0
    );

    ctx.lineTo(
        cx + 14,
        cy + 8
    );

    ctx.lineTo(
        cx - 14,
        cy + 8
    );

    ctx.closePath();

    ctx.fill();

    ctx.stroke();

    ctx.textAlign =
        "center";

    ctx.font =
        "15px Arial";

    ctx.fillText(
        "🦖",
        cx,
        cy + 5
    );

}

/* ============================================================
   OVERLAY BOX
   ============================================================ */

function overlayBox(
    w,
    h,
    border
) {

    const cx =
        canvas.width / 2;

    const cy =
        canvas.height / 2;

    drawRect(

        cx - w / 2,

        cy - h / 2,

        w,

        h,

        "#111827",

        border,

        4

    );

    return [
        cx,
        cy
    ];

}

/* ============================================================
   PAUSE / COUNTDOWN OVERLAY
   ============================================================ */

function drawPauseOverlay() {

    if (
        state.countdownActive &&
        state.countdownValue != null
    ) {

        const [
            cx,
            cy
        ] =
            overlayBox(
                320,
                230,
                "#f87171"
            );

        ctx.textAlign =
            "center";

        ctx.fillStyle =
            "white";

        ctx.font =
            "bold 24px Arial";

        ctx.fillText(
            "READY?",
            cx,
            cy - 38
        );

        ctx.fillStyle =
            "#fde047";

        ctx.font =

            state.countdownValue === "GO!"

            ?

            "bold 72px Arial"

            :

            "bold 72px Arial";

        ctx.fillText(

            String(
                state.countdownValue
            ),

            cx,

            cy + 28

        );

        return;

    }

    const [
        cx,
        cy
    ] =
        overlayBox(
            760,
            230,
            "#f87171"
        );

    ctx.textAlign =
        "center";

    ctx.fillStyle =
        "#bbf7d0";

    ctx.font =
        "bold 32px Arial";

    ctx.fillText(
        "🐾 PAWSING THE CLAWS 🐾",
        cx,
        cy - 62
    );

    ctx.fillStyle =
        "white";

    ctx.font =
        "bold 20px Arial";

    ctx.fillText(
        "Hunting for letters, dodging T-Rexes...",
        cx,
        cy - 12
    );

    ctx.fillText(
        "even legendary castle explorers need a breather.",
        cx,
        cy + 18
    );

    ctx.fillStyle =
        "#93c5fd";

    ctx.fillText(
        "Press SPACE when you're ready to run again!",
        cx,
        cy + 72
    );

}

/* ============================================================
   GUESS OVERLAY
   ============================================================ */

function drawGuessOverlay() {
    const [cx, cy] = overlayBox(
        780,
        190,
        "#ffd166"
    );

    ctx.textAlign = "center";
    ctx.fillStyle = "#ffd166";
    ctx.font = "bold 31px Arial";
    ctx.fillText(
        "🦖😢 NOOO! YOU GOT ALL THE CASTLES!",
        cx,
        cy - 42
    );

    ctx.fillStyle = "#86efac";
    ctx.font = "bold 21px Arial";
    ctx.fillText(
        "My snack escaped... Fine. Guess the word or phrase!",
        cx,
        cy + 8
    );

    ctx.fillStyle = "white";
    ctx.font = "bold 18px Arial";
    ctx.fillText(
        `Use all ${PLAYABLE_LETTERS.length} letters to finish the game.`,
        cx,
        cy + 50
    );
}

/* ============================================================
   WIN / DEATH OVERLAY
   ============================================================ */

function drawEndOverlay() {

    const [
        cx,
        cy
    ] =
        overlayBox(

            780,

            220,

            state.won

            ?

            "#22c55e"

            :

            "#22c55e"

        );

    ctx.textAlign =
        "center";

    if (
        state.won
    ) {

        ctx.fillStyle =
            "#fde047";

        ctx.font =
            "bold 36px Arial";

        ctx.fillText(
            "🎉 CONGRATULATIONS! 🎉",
            cx,
            cy - 42
        );

        ctx.fillStyle =
            "#7dd3fc";

        ctx.font =
            "bold 40px Arial";

        ctx.fillText(
            WORD,
            cx,
            cy + 24
        );

    }

    else {

        ctx.fillStyle =
            "#86efac";

        ctx.font =
            "bold 36px Arial";

        ctx.fillText(
            "🦖 NOM NOM NOM!",
            cx,
            cy - 42
        );

        ctx.fillStyle =
            "white";

        ctx.font =
            "bold 24px Arial";

        ctx.fillText(
            "You were delicious! 😋",
            cx,
            cy + 18
        );

    }

}

/* ============================================================
   MAIN DRAW
   ============================================================ */

function render() {

    updateLabels();

    ctx.clearRect(
        0,
        0,
        canvas.width,
        canvas.height
    );

    drawRect(
        0,
        0,
        canvas.width,
        canvas.height,
        "#050816"
    );

    /* DRAW MAZE */

    for (
        let r = 0;
        r < ROWS;
        r++
    ) {

        for (
            let c = 0;
            c < COLS;
            c++
        ) {

            const x =
                c * CELL;

            const y =
                r * CELL;

            if (
                MAZE[r][c] === 1
            ) {

                drawRect(

                    x + 1,

                    y + 1,

                    CELL - 2,

                    CELL - 2,

                    "#111827",

                    "#2563eb",

                    2

                );

            }

            else if (
                (r + c) % 3 === 0
            ) {

                ctx.beginPath();

                ctx.arc(
                    x + CELL / 2,
                    y + CELL / 2,
                    1,
                    0,
                    Math.PI * 2
                );

                ctx.fillStyle =
                    "#a78bfa";

                ctx.fill();

            }

        }

    }

    /* PORTALS */

    for (
        const [
            label,
            pair
        ]
        of
        Object.entries(
            PORTALS
        )
    ) {

        drawPortal(
            pair[0],
            label,
            true
        );

        drawPortal(
            pair[1],
            label,
            false
        );

    }

    /* CASTLES */

    for (
        const k
        of state.castles
    ) {

        drawCastle(
            k
                .split(",")
                .map(Number)
        );

    }

    /* CHARACTERS */

    drawDino();

    drawPlayer();

    /* OVERLAYS */

    if (
        state.awaitingGuess
    ) {
        // Keep the maze visible while the lower guess panel is active.
        // The guess panel below the game already shows the message.
    }

    else if (
        state.gameOver
    ) {

        drawEndOverlay();

    }

    else if (
        state.paused
    ) {

        drawPauseOverlay();

    }

    drawFireworks();

}

/* ============================================================
   FIREWORKS
   ============================================================ */

function startFireworks() {

    stopFireworks();

    fireworks =
        [];

    fireworkFrame =
        0;

    for (
        let i = 0;
        i < 7;
        i++
    ) {

        spawnFirework();

    }

    fireworkTimer =
        setInterval(
            () => {

                fireworkFrame++;

                if (
                    fireworkFrame > 360
                ) {

                    stopFireworks();

                    render();

                    return;

                }

                for (
                    const fw
                    of fireworks
                ) {

                    for (
                        const p
                        of fw.particles
                    ) {

                        const rad =

                            p.angle *

                            Math.PI /

                            180;

                        p.x +=

                            Math.cos(rad)

                            *

                            p.speed;

                        p.y +=

                            Math.sin(rad)

                            *

                            p.speed

                            +

                            p.gravity

                            *

                            0.13;

                        p.gravity +=
                            0.12;

                        p.speed *=
                            0.985;

                    }

                }

                // Keep launching new fireworks
                // throughout the celebration
                if (
                    fireworkFrame % 15 === 0
                ) {

                    for (
                        let i = 0;
                        i < 3;
                        i++
                    ) {

                        spawnFirework();

                    }

                }

                render();

            },
            45
        );

}

/* ============================================================
   SPAWN FIREWORK
   ============================================================ */

function spawnFirework() {

    const palette = [

        "#fde047",

        "#fb7185",

        "#22d3ee",

        "#a78bfa",

        "#34d399",

        "#f97316"

    ];

    const color =

        palette[

            Math.floor(

                Math.random()

                *

                palette.length

            )

        ];

    const cx =

        80

        +

        Math.random()

        *

        (
            canvas.width -
            160
        );

    const cy =

        70

        +

        Math.random()

        *

        (
            canvas.height /
            2
        );

    const particles =
        [];

    for (
        let i = 0;
        i < 18;
        i++
    ) {

        particles.push(
            {

                x:
                    cx,

                y:
                    cy,

                angle:
                    i * 20,

                speed:
                    2.4
                    +
                    Math.random()
                    *
                    2.8,

                gravity:
                    0

            }
        );

    }

    fireworks.push(
        {
            color,
            particles
        }
    );

}

/* ============================================================
   DRAW FIREWORKS
   ============================================================ */

function drawFireworks() {

    for (
        const fw
        of fireworks
    ) {

        for (
            const p
            of fw.particles
        ) {

            const size =

                Math.max(

                    1.5,

                    Math.min(
                        4,
                        p.speed
                    )

                );

            ctx.beginPath();

            ctx.arc(
                p.x,
                p.y,
                size,
                0,
                Math.PI * 2
            );

            ctx.fillStyle =
                fw.color;

            ctx.fill();

        }

    }

}

/* ============================================================
   STOP FIREWORKS
   ============================================================ */

function stopFireworks() {

    if (
        fireworkTimer
    ) {

        clearInterval(
            fireworkTimer
        );

    }

    fireworkTimer =
        null;

    fireworks =
        [];

}

/* ============================================================
   KEYBOARD
   ============================================================ */

function keyHandler(e) {

    const tag =

        (
            e.target

            &&

            e.target.tagName

            ||

            ""
        )

        .toLowerCase();

    const editing =

        tag === "input"

        ||

        tag === "textarea";

    if (
        editing
    ) {

        if (

            e.key === "Enter"

            &&

            e.target === guessInput

        ) {

            e.preventDefault();

            submitGuess();

        }

        return;

    }

    const key =
        e.key.toLowerCase();

    /* SPACE = PAUSE */

    if (
        key === " "
    ) {

        e.preventDefault();

        pauseGame();

        return;

    }

    if (

        state.gameOver

        ||

        state.awaitingGuess

        ||

        state.paused

        ||

        state.countdownActive

    ) {

        return;

    }

    const dirs = {

        arrowup:
            [-1, 0],

        w:
            [-1, 0],

        arrowdown:
            [1, 0],

        s:
            [1, 0],

        arrowleft:
            [0, -1],

        a:
            [0, -1],

        arrowright:
            [0, 1],

        d:
            [0, 1]

    };

    if (
        dirs[key]
    ) {

        e.preventDefault();

        state.nextDir =
            dirs[key];

    }

}


/* ============================================================
   MOBILE / TOUCH MOVEMENT
   ============================================================ */
function setTouchDirection(direction) {
    if (
        state.gameOver ||
        state.awaitingGuess ||
        state.paused ||
        state.countdownActive
    ) {
        return;
    }

    state.nextDir = direction;
    ROOT.focus({ preventScroll: true });
}

const touchDirections = {
    "move-up": [-1, 0],
    "move-down": [1, 0],
    "move-left": [0, -1],
    "move-right": [0, 1]
};

Object.entries(touchDirections).forEach(([id, direction]) => {
    const button = document.getElementById(id);
    if (!button) return;

    const press = (event) => {
        event.preventDefault();
        button.classList.add("pressed");
        setTouchDirection(direction);
    };

    const release = (event) => {
        if (event) event.preventDefault();
        button.classList.remove("pressed");
    };

    button.addEventListener("pointerdown", press);
    button.addEventListener("pointerup", release);
    button.addEventListener("pointercancel", release);
    button.addEventListener("pointerleave", release);
    button.addEventListener("contextmenu", event => event.preventDefault());
});

/* Swipe anywhere on the canvas to change direction. */
let swipeStartX = null;
let swipeStartY = null;
const SWIPE_MIN = 22;

canvas.addEventListener(
    "touchstart",
    (event) => {
        if (!event.touches || event.touches.length !== 1) return;
        swipeStartX = event.touches[0].clientX;
        swipeStartY = event.touches[0].clientY;
        event.preventDefault();
    },
    { passive: false }
);

canvas.addEventListener(
    "touchmove",
    (event) => {
        // Prevent the page from scrolling while the player is swiping the maze.
        event.preventDefault();
    },
    { passive: false }
);

canvas.addEventListener(
    "touchend",
    (event) => {
        if (swipeStartX === null || swipeStartY === null) return;

        const touch = event.changedTouches && event.changedTouches[0];
        if (!touch) return;

        const dx = touch.clientX - swipeStartX;
        const dy = touch.clientY - swipeStartY;
        swipeStartX = null;
        swipeStartY = null;

        if (Math.max(Math.abs(dx), Math.abs(dy)) < SWIPE_MIN) return;

        if (Math.abs(dx) > Math.abs(dy)) {
            setTouchDirection(dx > 0 ? [0, 1] : [0, -1]);
        } else {
            setTouchDirection(dy > 0 ? [1, 0] : [-1, 0]);
        }

        event.preventDefault();
    },
    { passive: false }
);

/* ============================================================
   BUTTON LISTENERS
   ============================================================ */

ROOT.addEventListener(
    "keydown",
    keyHandler
);

document
    .getElementById(
        "restart"
    )
    .addEventListener(
        "click",
        () => {

            recordGameStart();

            resetGame(
                true
            );

        }
    );

helpGameButton.addEventListener(
    "click",
    () => {
        helpModal.style.display = "flex";
    }
);

helpGameLiveButton.addEventListener(
    "click",
    () => {
        // Opening Help during gameplay automatically pauses the game.
        // Do not trigger the resume countdown if it was already paused.
        if (
            !state.gameOver &&
            !state.awaitingGuess &&
            !state.countdownActive &&
            !state.paused
        ) {
            state.paused = true;
            state.playerDir = [0, 0];
            state.nextDir = [0, 0];
            state.lastEvent = "🐾 Pawsing the Claws...";
            render();
        }

        helpModal.style.display = "flex";
    }
);

closeHelpButton.addEventListener(
    "click",
    () => {
        helpModal.style.display = "none";
        ROOT.focus();
    }
);

helpModal.addEventListener(
    "click",
    (event) => {
        if (event.target === helpModal) {
            helpModal.style.display = "none";
            ROOT.focus();
        }
    }
);

document.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Escape" &&
            helpModal.style.display === "flex"
        ) {
            helpModal.style.display = "none";
            ROOT.focus();
        }
    }
);

startGameButton.addEventListener(
    "click",
    () => {

        introPanel.style.display =
            "none";

        gameArea.style.display =
            "block";

        recordGameStart();

        resetGame(
            true
        );

        ROOT.focus();

    }
);

document
    .getElementById(
        "pause"
    )
    .addEventListener(
        "click",
        pauseGame
    );

guessButton.addEventListener(
    "click",
    submitGuess
);

/* Clicking game restores
   keyboard focus */

canvas.addEventListener(
    "click",
    () => {

        ROOT.focus();

    }
);

ROOT.addEventListener(
    "click",
    e => {

        if (
            e.target !== guessInput
        ) {

            ROOT.focus();

        }

    }
);

/* ============================================================
   INITIAL STATE
   IMPORTANT:
   Game does NOT start yet.
   User must press START GAME.
   ============================================================ */

resetGame(
    false
);

})();

</script>

</div>

"""

# ============================================================
# DISPLAY GAME
# ============================================================

CURRENT_USER_JSON = json.dumps(
    st.session_state.get("username", "Player")
)
SUPABASE_URL_JSON = json.dumps(SUPABASE_URL)
SUPABASE_PUBLIC_KEY_JSON = json.dumps(SUPABASE_PUBLIC_KEY)

if not SUPABASE_URL or not SUPABASE_PUBLIC_KEY:
    st.warning(
        "Supabase scoreboard is not connected yet. Add `url` and "
        "`publishable_key` under `[supabase]` in Streamlit Secrets."
    )

GAME_HTML_FOR_USER = (
    GAME_HTML
    .replace("__CURRENT_USER_JSON__", CURRENT_USER_JSON)
    .replace("__SUPABASE_URL_JSON__", SUPABASE_URL_JSON)
    .replace("__SUPABASE_PUBLIC_KEY_JSON__", SUPABASE_PUBLIC_KEY_JSON)
)

components.html(
    GAME_HTML_FOR_USER,
    height=825,
    scrolling=True
)
