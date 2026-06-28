import streamlit as st
import json
import re
import random
import html
from pathlib import Path

st.set_page_config(
    page_title="Brainrot ↔ Corporate",
    page_icon="🔄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
#MainMenu, footer, header { visibility: hidden; }

.block-container {
    max-width: 780px;
    padding-top: 3rem;
    padding-bottom: 4rem;
}

.hero-wrap {
    text-align: center;
    margin-bottom: 2rem;
}

.hero-title {
    font-size: clamp(2rem, 6vw, 3rem);
    font-weight: 900;
    background: linear-gradient(135deg, #ff6bdf 0%, #c44dff 45%, #4da9ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.15;
    margin: 0 0 0.4rem 0;
}

.hero-sub {
    color: #666;
    font-size: 0.95rem;
    font-style: italic;
    margin: 0;
}

/* Mode radio */
div[data-testid="stRadio"] > div {
    justify-content: center;
    gap: 10px;
}

div[data-testid="stRadio"] label {
    border-radius: 100px !important;
    padding: 6px 20px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.04) !important;
    cursor: pointer;
    transition: all 0.2s;
    font-size: 0.9rem !important;
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    height: 44px !important;
    transition: all 0.15s !important;
}

[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #c44dff, #4da9ff) !important;
    border: none !important;
    color: white !important;
}

[data-testid="baseButton-primary"]:hover {
    opacity: 0.88 !important;
    box-shadow: 0 4px 20px rgba(196,77,255,0.35) !important;
}

/* Text area */
.stTextArea textarea {
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: rgba(255,255,255,0.03) !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    transition: border-color 0.2s !important;
}

.stTextArea textarea:focus {
    border-color: rgba(196,77,255,0.5) !important;
    box-shadow: 0 0 0 3px rgba(196,77,255,0.1) !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-size: 0.82rem !important;
    color: #555 !important;
}

/* Output */
.output-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #555;
    margin: 16px 0 6px;
}

.output-box {
    border-radius: 14px;
    padding: 20px 24px;
    white-space: pre-wrap;
    line-height: 1.7;
    font-size: 0.95rem;
    word-break: break-word;
}

.box-original {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    color: #888;
}

.box-brainrot {
    background: rgba(0,232,122,0.06);
    border: 1px solid rgba(0,232,122,0.22);
    color: #00e87a;
    font-weight: 500;
}

.box-corporate {
    background: rgba(77,169,255,0.06);
    border: 1px solid rgba(77,169,255,0.22);
    color: #4da9ff;
    font-weight: 500;
}

.count-tag {
    text-align: right;
    font-size: 0.78rem;
    color: #484848;
    margin-top: 8px;
}

.no-match {
    color: #484848;
    font-style: italic;
}

hr { border-color: rgba(255,255,255,0.07) !important; margin: 1.5rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────

RANDOM_EMAILS = [
    """\
Hi Team,

As we circle back on our Q3 synergy initiatives, I wanted to touch base regarding \
the low-hanging fruit we identified in our last alignment session. Going forward, \
let's ensure all stakeholders are leveraging our core competencies to move the needle \
on our key deliverables.

Action items: Please drill down into your pain points and provide value-add \
recommendations before our next deep dive. Let's take this offline if needed.

Best,
Chad from Finance""",

    """\
Dear All,

I wanted to proactively reach out to facilitate a paradigm shift in how we approach \
our bandwidth constraints. At the end of the day, our robust and scalable solutions \
need to be more agile. Let's ideate on best practices to ensure seamless delivery of \
our bleeding-edge, disruptive innovations. Let's align on this ASAP.

Regards,
Brenda, Director of Synergies""",

    """\
Hi,

Just wanted to loop you in on our deep dive around stakeholder synergy. We need to \
move the needle on transparency and leverage our core competencies. Please touch base \
with me to drill down on the pain points and circle back with your action items by EOD.

Per my last email, this is mission critical going forward. Thank you for your patience.

Thanks,
Derek""",

    """\
Team,

As per our last call, let's pivot our strategy and boil the ocean on ideation for our \
next paradigm shift. The bleeding-edge approach we've been exploring is a real game \
changer. Let's take this to the next level — reach out to all stakeholders to ensure \
we have the bandwidth to deliver this seamlessly and at scale.

Best,
Karen, VP of Innovative Synergies""",
]

# ── Core logic ────────────────────────────────────────────────────────────────

@st.cache_resource
def load_dictionary() -> dict:
    dict_path = Path(__file__).parent / "dictionary.json"
    with open(dict_path, encoding="utf-8") as f:
        return json.load(f)


def translate(text: str, mapping: dict) -> tuple[str, int]:
    result = text
    total = 0
    for phrase in sorted(mapping.keys(), key=len, reverse=True):
        pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
        result, n = pattern.subn(mapping[phrase], result)
        total += n
    return result, total


dictionary = load_dictionary()

# ── Session state defaults ────────────────────────────────────────────────────

for key, val in [("result", None), ("original", None), ("count", 0)]:
    if key not in st.session_state:
        st.session_state[key] = val

# Random-email trigger: must run before text_area to pre-fill it
if st.session_state.get("_rand"):
    st.session_state.input_text = random.choice(RANDOM_EMAILS)
    del st.session_state["_rand"]
    st.session_state["_auto"] = True

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero-wrap">
  <h1 class="hero-title">Brainrot ↔ Corporate</h1>
  <p class="hero-sub">making corp speak actually comprehensible (or not)</p>
</div>
""", unsafe_allow_html=True)

# ── Mode selector ─────────────────────────────────────────────────────────────

mode = st.radio(
    "",
    options=["Corp → Brainrot", "Brainrot → Corp"],
    horizontal=True,
    label_visibility="collapsed",
)
is_brainrot = mode == "Corp → Brainrot"

# Clear result when mode flips
if st.session_state.get("_last_mode") != mode:
    st.session_state.result = None
    st.session_state["_last_mode"] = mode

st.write("")

# ── Text input ────────────────────────────────────────────────────────────────

placeholder = (
    "Paste corporate speak here…\n\nTry: Let's circle back on the synergy and touch base with stakeholders going forward."
    if is_brainrot else
    "Drop your brainrot here…\n\nTry: no cap, this is bussin fr fr and it's giving main character energy"
)

st.text_area(
    "",
    key="input_text",
    height=168,
    placeholder=placeholder,
    label_visibility="collapsed",
)

# ── Action buttons ────────────────────────────────────────────────────────────

c1, c2 = st.columns(2)
with c1:
    rand_hit = st.button("🎲 Random Corporate Email", use_container_width=True)
with c2:
    go_label = "Translate → Brainrot" if is_brainrot else "Translate → Corporate"
    go_hit = st.button(go_label, type="primary", use_container_width=True)

# ── Example phrases ───────────────────────────────────────────────────────────

with st.expander("💡 Example phrases that get translated"):
    if is_brainrot:
        st.caption(
            "circle back · synergy · touch base · low-hanging fruit · move the needle · "
            "bandwidth · deep dive · paradigm shift · boil the ocean · loop you in · "
            "going forward · per my last email · action items · pain points · reach out"
        )
    else:
        st.caption(
            "no cap · bussin · fr fr · it's giving · slay · main character · goated · "
            "vibe check · ate and left no crumbs · rizz · rent free · deadass · on god · "
            "ghosted · ratio · sus · based · lowkey · highkey · W · L"
        )

# ── Handle random click ───────────────────────────────────────────────────────

if rand_hit:
    st.session_state["_rand"] = True
    st.rerun()

# ── Handle translation ────────────────────────────────────────────────────────

_auto = st.session_state.get("_auto", False)
if "_auto" in st.session_state:
    del st.session_state["_auto"]

if go_hit or _auto:
    text = st.session_state.input_text.strip()
    if text:
        mapping = dictionary["corp_to_slang"] if is_brainrot else dictionary["slang_to_corp"]
        result, count = translate(text, mapping)
        st.session_state.result = result
        st.session_state.original = text
        st.session_state.count = count
    else:
        st.warning("Enter some text first.", icon="⚠️")

# ── Output ────────────────────────────────────────────────────────────────────

if st.session_state.result is not None:
    st.markdown("<hr>", unsafe_allow_html=True)

    orig = html.escape(st.session_state.original)
    res = html.escape(st.session_state.result)

    st.markdown('<p class="output-label">Original</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-box box-original">{orig}</div>', unsafe_allow_html=True)

    cls = "box-brainrot" if is_brainrot else "box-corporate"
    lbl = "Brainrot" if is_brainrot else "Corporate"

    if st.session_state.count == 0:
        body = (
            '<span class="no-match">No corporate speak detected — '
            "you're already speaking fluent internet.</span>"
            if is_brainrot else
            '<span class="no-match">No brainrot detected — '
            "suspiciously professional already.</span>"
        )
    else:
        body = res

    st.markdown(f'<p class="output-label">{lbl}</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="output-box {cls}">{body}</div>', unsafe_allow_html=True)

    n = st.session_state.count
    st.markdown(
        f'<p class="count-tag">{n} phrase{"s" if n != 1 else ""} translated</p>',
        unsafe_allow_html=True,
    )
