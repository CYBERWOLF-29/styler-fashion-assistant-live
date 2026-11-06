from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from config import settings
from components.voice_assistant import render_voice_assistant
from services.ai_assistant import respond_to_voice_command
from styler_app.analysis import (
    analyze_wardrobe_image,
    analyse_portrait,
    build_colour_palette,
    build_shopping_list,
    generate_outfit_recommendations,
)
from styler_app.storage import DEFAULT_PROFILE, is_demo_mode, load_outfits, load_profile, load_wardrobe, save_outfits, save_profile, save_wardrobe


st.set_page_config(page_title="STYLER", page_icon="👗", layout="wide")


def initialize_state() -> None:
    if "profile" not in st.session_state:
        st.session_state.profile = load_profile()
    if "wardrobe" not in st.session_state:
        st.session_state.wardrobe = load_wardrobe()
    if "outfits" not in st.session_state:
        st.session_state.outfits = load_outfits()
    if "nav" not in st.session_state:
        st.session_state.nav = "Home"
    if "voice_prompt" not in st.session_state:
        st.session_state.voice_prompt = ""
    if "voice_response" not in st.session_state:
        st.session_state.voice_response = ""
    if "voice_response_id" not in st.session_state:
        st.session_state.voice_response_id = ""
    if "voice_last_outfit" not in st.session_state:
        st.session_state.voice_last_outfit = None
    if "voice_last_occasion" not in st.session_state:
        st.session_state.voice_last_occasion = None
    if "voice_recent_combinations" not in st.session_state:
        st.session_state.voice_recent_combinations = []
    if "voice_last_event_id" not in st.session_state:
        st.session_state.voice_last_event_id = ""


def process_voice_command(command: str) -> None:
    response, outfit, combinations, occasion = respond_to_voice_command(
        command,
        st.session_state.profile,
        st.session_state.wardrobe,
        st.session_state.voice_recent_combinations,
        st.session_state.voice_last_outfit,
        st.session_state.voice_last_occasion,
    )
    st.session_state.voice_response = response
    st.session_state.voice_response_id = str(int(st.session_state.voice_response_id or "0") + 1)
    if outfit is not None:
        st.session_state.voice_last_outfit = outfit
    st.session_state.voice_last_occasion = occasion
    st.session_state.voice_recent_combinations.extend(combinations)
    st.session_state.voice_recent_combinations = st.session_state.voice_recent_combinations[-24:]


def save_session_data() -> None:
    save_profile(st.session_state.profile)
    save_wardrobe(st.session_state.wardrobe)
    save_outfits(st.session_state.outfits)


def render_header() -> None:
    st.markdown(
        """
        <style>
        :root {
            --cream: #f9f4ee;
            --beige: #e7d9c8;
            --sand: #d4b79d;
            --brown: #5c4335;
            --charcoal: #1f1f1f;
            --gold: #b9985a;
            --panel: rgba(255,255,255,0.62);
            --shadow: 0 18px 40px rgba(62,41,31,0.12);
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(217,189,146,0.18), transparent 30%),
                radial-gradient(circle at bottom right, rgba(92,67,53,0.10), transparent 30%),
                linear-gradient(135deg, #f8f3ee 0%, #f2e8de 50%, #efe3d5 100%);
            color: var(--charcoal);
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        .stSidebar > div {
            background: rgba(245, 236, 228, 0.92);
            border-right: 1px solid rgba(92, 67, 53, 0.08);
        }
        div[data-testid="stSidebarNav"] {
            background: rgba(245, 236, 228, 0.92);
        }
        .stTabs [role="tablist"] {
            gap: 0.8rem;
        }
        .stTabs [role="tab"] {
            border-radius: 999px;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.45);
            border: 1px solid rgba(92,67,53,0.08);
        }
        .stTabs [role="tab"][aria-selected="true"] {
            background: linear-gradient(135deg, #5c4335 0%, #8d6f58 100%);
            color: #fff;
            box-shadow: var(--shadow);
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 999px !important;
            background: linear-gradient(135deg, #5c4335 0%, #8d6f58 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 12px 30px rgba(92,67,53,0.18) !important;
            padding: 0.65rem 1.2rem !important;
            font-weight: 600 !important;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            filter: brightness(1.03);
            transform: translateY(-1px);
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stNumberInput > div > div,
        .stTextArea > div > div > textarea {
            border-radius: 14px !important;
            background: rgba(255,255,255,0.86) !important;
            border: 1px solid rgba(92, 67, 53, 0.14) !important;
        }
        .metric-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.74), rgba(255,255,255,0.52));
            border: 1px solid rgba(92, 67, 53, 0.08);
            border-radius: 22px;
            padding: 1.2rem 1.3rem;
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
        }
        .luxury-panel {
            background: linear-gradient(180deg, rgba(255,255,255,0.78), rgba(248,238,230,0.85));
            border-radius: 28px;
            border: 1px solid rgba(92,67,53,0.08);
            box-shadow: var(--shadow);
            padding: 1.5rem;
        }
        .brand-mark {
            letter-spacing: 0.18em;
            text-transform: uppercase;
            color: #7a5d47;
            font-weight: 700;
            font-size: 0.76rem;
        }
        .title-spotlight {
            font-size: clamp(2.2rem, 4vw, 4rem);
            font-weight: 700;
            letter-spacing: -0.06em;
            background: linear-gradient(135deg, #473327 0%, #8f6b52 48%, #b9985a 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.2rem;
        }
        h1, h2, h3, h4 {
            color: #2f241f;
        }
        .stAlert {
            border-radius: 18px !important;
        }
        @media (max-width: 768px) {
            .block-container {
                padding: 1rem 1rem 2rem !important;
            }
            .title-spotlight {
                font-size: clamp(2.5rem, 14vw, 4rem);
            }
            h1 {
                font-size: 1.8rem !important;
            }
            h2 {
                font-size: 1.45rem !important;
            }
            h3 {
                font-size: 1.2rem !important;
            }
            div[data-testid="stHorizontalBlock"] {
                flex-wrap: wrap !important;
                gap: 0.75rem !important;
            }
            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 100% !important;
            }
            .metric-card, .luxury-panel {
                border-radius: 20px;
                padding: 1.1rem !important;
            }
            .stButton > button, .stDownloadButton > button,
            [data-testid="stFormSubmitButton"] > button {
                min-height: 46px;
                width: 100%;
            }
            input, textarea, [role="combobox"] {
                font-size: 16px !important;
            }
            [data-testid="stFileUploader"] section {
                padding: 0.8rem !important;
            }
            [data-testid="stSidebar"] {
                min-width: min(85vw, 320px) !important;
            }
            [data-testid="stSidebar"] button {
                min-height: 44px;
            }
            .stCaption, [data-testid="stCaptionContainer"] {
                line-height: 1.5;
            }
        }
        @media (max-width: 420px) {
            .block-container {
                padding-left: 0.75rem !important;
                padding-right: 0.75rem !important;
            }
            .brand-mark {
                letter-spacing: 0.12em;
            }
            .luxury-panel {
                padding: 0.9rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('<div class="brand-mark">AI personal fashion assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="title-spotlight">STYLER</div>', unsafe_allow_html=True)
    st.caption("Your Wardrobe. Your Colours. Your Style.")


def onboarding_form() -> None:
    st.header("Welcome to STYLER")
    st.markdown("Create your personal style profile to unlock AI wardrobe and outfit suggestions.")
    with st.form("onboarding_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Preferred name", key="name")
            st.text_input("Nickname", key="nickname")
            st.selectbox("Age range", ["", "18-24", "25-34", "35-44", "45-54", "55+"], index=0, key="age_range")
            st.selectbox("Gender presentation", ["", "Woman", "Man", "Non-binary", "Prefer not to say"], index=0, key="gender_presentation")
            st.text_input("Country", key="country")
            st.text_input("Location", key="location")
        with col2:
            st.text_input("Height", key="height")
            st.text_input("Preferred clothing sizes", key="sizes")
            st.text_input("Preferred aesthetic", key="aesthetic", value="Minimal luxury")
            st.selectbox("Preferred fit", ["Relaxed", "Tailored", "Straight", "Oversized"], index=0, key="preferred_fit")
            st.text_input("Favourite colours", key="favourite_colours", value="Warm cream, Olive green, Navy")
            st.text_input("Colours you dislike", key="disliked_colours", value="Neon pink")
            st.text_input("Budget range", key="budget_range", value="150-350")
            st.text_input("Shopping preferences", key="shopping_preferences", value="Elevated basics")
        st.multiselect("Common occasions", ["Work", "Weekend brunch", "Evening events", "Travel", "Weddings", "Casual dates"], default=["Work", "Weekend brunch"], key="common_occasions")
        submitted = st.form_submit_button("Save my profile")
        if submitted:
            profile = st.session_state.profile.copy()
            profile.update({
                "is_onboarded": True,
                "name": st.session_state.get("name", ""),
                "preferred_nickname": st.session_state.get("nickname", ""),
                "age_range": st.session_state.get("age_range", ""),
                "gender_presentation": st.session_state.get("gender_presentation", ""),
                "country": st.session_state.get("country", ""),
                "location": st.session_state.get("location", ""),
                "height": st.session_state.get("height", ""),
                "preferred_sizes": st.session_state.get("sizes", ""),
                "preferred_aesthetic": st.session_state.get("aesthetic", "Minimal luxury"),
                "preferred_fit": st.session_state.get("preferred_fit", "Relaxed"),
                "favourite_colours": [c.strip() for c in str(st.session_state.get("favourite_colours", "Warm cream, Olive green, Navy")).split(",") if c.strip()],
                "colours_disliked": [c.strip() for c in str(st.session_state.get("disliked_colours", "Neon pink")).split(",") if c.strip()],
                "budget_range": st.session_state.get("budget_range", "150-350"),
                "shopping_preferences": st.session_state.get("shopping_preferences", "Elevated basics"),
                "common_occasions": st.session_state.get("common_occasions", ["Work", "Weekend brunch"]),
            })
            st.session_state.profile = profile
            save_session_data()
            st.success("Your profile has been saved. Welcome to STYLER.")
            st.rerun()


def home_page() -> None:
    st.header("Home")
    profile = st.session_state.profile
    name = profile.get("name") or profile.get("preferred_nickname") or "Stylist"
    if not st.session_state.voice_last_outfit and st.session_state.wardrobe:
        initial_recommendations = generate_outfit_recommendations(
            profile,
            st.session_state.wardrobe,
            profile.get("default_occasion", settings.DEFAULT_OCCASION),
        )
        if initial_recommendations:
            st.session_state.voice_last_outfit = initial_recommendations[0]
            st.session_state.voice_last_occasion = profile.get("default_occasion", settings.DEFAULT_OCCASION)
    if is_demo_mode():
        st.info("Public demo with sample wardrobe: changes are temporary to this browser session and are not saved.")

    st.markdown(
        """
        <div class="luxury-panel">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                <div>
                    <div class="brand-mark" style="margin-bottom:0.4rem;">Good evening</div>
                    <div style="font-size: clamp(1.8rem,2.5vw,2.8rem); font-weight:700; letter-spacing:-0.05em;">{name}</div>
                </div>
                <div style="padding:0.7rem 1rem; border-radius:999px; background: rgba(185,152,90,0.12); border:1px solid rgba(185,152,90,0.25); color:#5c4335; font-weight:600;">
                    Today: Work-ready elegance
                </div>
            </div>
            <div style="margin-top:1.2rem; font-size:1.02rem; color:#4b3b32;">
                Your wardrobe is curated for soft neutrals, elevated structure, and confident everyday polish.
            </div>
        </div>
        """.format(name=name),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card"><div class="brand-mark">Wardrobe</div><div style="font-size:2.2rem;font-weight:700;">{}</div></div>'.format(len(st.session_state.wardrobe)), unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><div class="brand-mark">Saved outfits</div><div style="font-size:2.2rem;font-weight:700;">{}</div></div>'.format(len(st.session_state.outfits)), unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><div class="brand-mark">Palette</div><div style="font-size:1.3rem;font-weight:700;">{}</div></div>'.format(profile.get("preferred_aesthetic", "Minimal luxury")), unsafe_allow_html=True)

    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)
    voice_col, result_col = st.columns([2, 3])
    with voice_col:
        voice_event = render_voice_assistant(
            response=st.session_state.voice_response,
            response_id=st.session_state.voice_response_id,
            language=profile.get("voice_language", settings.VOICE_LANGUAGE),
        )
        if (
            isinstance(voice_event, dict)
            and voice_event.get("id")
            and voice_event.get("id") != st.session_state.voice_last_event_id
        ):
            st.session_state.voice_last_event_id = voice_event["id"]
            command = str(voice_event.get("text", "")).strip()
            if command:
                process_voice_command(command)
                st.rerun()

        st.caption(
            "Allow microphone access, then say “Hey STYLER.” Voice works only while this tab is open and listening. "
            "Chrome or Edge is recommended; your browser’s speech service may process audio."
        )
        with st.form("voice_form"):
            user_prompt = st.text_input("Or type a command", key="voice_prompt")
            submitted = st.form_submit_button("Ask STYLER")
            if submitted:
                if user_prompt.strip():
                    process_voice_command(user_prompt)
                    st.rerun()
    with result_col:
        outfit = st.session_state.voice_last_outfit
        st.markdown('<div class="luxury-panel">', unsafe_allow_html=True)
        st.markdown('<div class="brand-mark">STYLER responds</div>', unsafe_allow_html=True)
        if outfit:
            st.subheader(f"{outfit['top']}  +  {outfit['bottom']}")
            st.markdown(f"**{outfit['score']} match**")
            st.write(outfit["note"])
            st.caption("Both pieces were selected from your saved wardrobe.")
        elif st.session_state.voice_response:
            st.write(st.session_state.voice_response)
        else:
            st.write("Say “Hey STYLER, what should I wear today?” to receive a recommendation from your wardrobe.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Your style snapshot")
    colA, colB = st.columns(2)
    with colA:
        st.info(f"Preferred aesthetic: {profile.get('preferred_aesthetic', 'Minimal luxury')}")
        st.info(f"Colour priorities: {', '.join(profile.get('favourite_colours', ['Warm cream', 'Olive green']))}")
    with colB:
        st.info(f"Favourite occasions: {', '.join(profile.get('common_occasions', ['Work', 'Weekend brunch']))}")
        st.info(f"Budget range: ${profile.get('budget_range', '150-350')}")

    st.markdown("### Style suggestions")
    recs = generate_outfit_recommendations(
        profile,
        st.session_state.wardrobe,
        profile.get("default_occasion", settings.DEFAULT_OCCASION),
    )
    for rec in recs:
        st.markdown(
            f"<div class='luxury-panel' style='margin-bottom:0.8rem;'><strong>{rec['top']}</strong> + <strong>{rec['bottom']}</strong> — <span style='color:#7a5d47;font-weight:700;'>{rec['score']}</span> match<br><span style='color:#4b3b32;'>{rec['note']}</span></div>",
            unsafe_allow_html=True,
        )


def wardrobe_page() -> None:
    st.header("My Wardrobe")
    uploaded = st.file_uploader("Upload clothing photos", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

    if uploaded:
        new_items: List[Dict[str, Any]] = []
        for file in uploaded:
            bytes_data = file.read()
            analysis = analyze_wardrobe_image(bytes_data, file.name)
            item = {
                "id": f"item-{len(st.session_state.wardrobe) + len(new_items) + 1}",
                "name": file.name.rsplit(".", 1)[0],
                "category": analysis["category"],
                "subcategory": analysis["subcategory"],
                "main_colour": analysis["main_colour"],
                "secondary_colour": analysis["secondary_colour"],
                "pattern": analysis["pattern"],
                "fabric": analysis["fabric"],
                "fit": analysis["fit"],
                "style": analysis["style"],
                "season": analysis["season"],
                "formality": analysis["formality"],
                "image_name": file.name,
                "thumbnail": file.name,
            }
            new_items.append(item)
            st.session_state.wardrobe.append(item)
        save_session_data()
        st.success(f"Added {len(new_items)} wardrobe item(s).")

    if st.session_state.wardrobe:
        st.markdown("### Saved pieces")
        search = st.text_input("Search wardrobe by name or category")
        filtered = [item for item in st.session_state.wardrobe if search.lower() in item.get("name", "").lower() or search.lower() in item.get("category", "").lower()]
        filtered = filtered if search else st.session_state.wardrobe
        for item in filtered:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**{item['name']}**")
                    st.markdown(f"{item['category']} / {item['subcategory']}")
                    st.markdown(f"Colour: {item['main_colour']} • {item['secondary_colour']}")
                    if st.button(f"Delete {item['name']}", key=f"del-{item['id']}"):
                        st.session_state.wardrobe = [entry for entry in st.session_state.wardrobe if entry.get('id') != item.get('id')]
                        save_session_data()
                        st.rerun()
                with col2:
                    st.json({
                        "Pattern": item.get("pattern"),
                        "Fabric": item.get("fabric"),
                        "Fit": item.get("fit"),
                        "Style": item.get("style"),
                        "Season": item.get("season"),
                        "Formality": item.get("formality"),
                    }, expanded=False)
                    if st.button(f"Save to outfit board", key=f"save-{item['id']}"):
                        st.session_state.outfits.append({
                            "id": f"outfit-{len(st.session_state.outfits) + 1}",
                            "name": f"{item['category']} mix",
                            "pieces": [item['name']],
                            "occasion": "General",
                            "palette": [item['main_colour']]
                        })
                        save_session_data()
                        st.success("Saved to your outfit board.")
    else:
        st.info("No wardrobe items yet. Upload a few key pieces to get started.")


def colour_analysis_page() -> None:
    st.header("Colour Analysis")
    st.markdown("Upload a natural-light selfie to estimate undertones and palette compatibility.")
    uploaded = st.file_uploader("Upload portrait photo", type=["jpg", "jpeg", "png", "webp"])
    if uploaded is not None:
        analysis = analyse_portrait(uploaded.read())
        st.json(analysis)
        palette = build_colour_palette(st.session_state.profile)
        for label, colors in palette.items():
            st.markdown(f"### {label.title()}")
            cols = st.columns(len(colors))
            for col, colour in zip(cols, colors):
                col.markdown(
                    f"<div style='background:{colour};height:80px;border-radius:12px;border:1px solid #d0d0d0'></div><small>{colour}</small>",
                    unsafe_allow_html=True,
                )
        st.caption("Important note: skin undertone analysis should be confirmed by the user and never treated as certain when lighting is poor or the image is filtered.")


def stylist_page() -> None:
    st.header("AI Stylist")
    occasion = st.selectbox("Occasion", ["Work", "Weekend brunch", "Evening event", "Travel", "Casual date"], index=0)
    if st.button("Generate outfit ideas"):
        recs = generate_outfit_recommendations(st.session_state.profile, st.session_state.wardrobe, occasion)
        if recs:
            for rec in recs:
                st.markdown(f"### {rec['top']} + {rec['bottom']}")
                st.write(f"Match score: {rec['score']}")
                st.write(rec['note'])
                st.code(rec['colour_story'])
        else:
            st.info("Add more wardrobe items to unlock outfit recommendations.")


def outfit_studio_page() -> None:
    st.header("Outfit Studio")
    top_options = [item['name'] for item in st.session_state.wardrobe if item.get('category') in {'TOP WEAR', 'ACCESSORIES'}]
    bottom_options = [item['name'] for item in st.session_state.wardrobe if item.get('category') == 'BOTTOM WEAR']
    if not top_options or not bottom_options:
        st.info("Add a few tops and bottoms to build an outfit in the studio.")
        return
    top_choice = st.selectbox("Top wear", top_options)
    bottom_choice = st.selectbox("Bottom wear", bottom_options)
    occasion = st.selectbox("Occasion", ["Work", "Weekend brunch", "Formal dinner", "Travel", "Day off"], index=0)
    if st.button("Save outfit concept"):
        outfit = {
            "id": f"outfit-{len(st.session_state.outfits) + 1}",
            "name": f"{top_choice} + {bottom_choice}",
            "pieces": [top_choice, bottom_choice],
            "occasion": occasion,
            "palette": ["#F7F1E7", "#1F2A44"],
        }
        st.session_state.outfits.append(outfit)
        save_session_data()
        st.success("Outfit saved to your Saved Outfits board.")


def occasion_styling_page() -> None:
    st.header("Occasion Styling")
    occasion = st.selectbox("What are you dressing for?", ["Work", "Wedding", "Date night", "Weekend brunch", "Travel"], index=0)
    palette = build_colour_palette(st.session_state.profile)
    if occasion == "Work":
        suggestion = "Cream shirt + navy trousers + soft leather accessories"
    elif occasion == "Wedding":
        suggestion = "Soft beige blazer + tailored trousers + muted terracotta details"
    elif occasion == "Date night":
        suggestion = "Dark chocolate knit + stone trousers + polished shoes"
    else:
        suggestion = "Relaxed shirt + olive or navy basics + suede accessories"
    st.success(suggestion)
    st.markdown("Colour harmony")
    cols = st.columns(len(palette['recommended']))
    for idx, colour in enumerate(palette['recommended']):
        cols[idx].markdown(f"<div style='background:{colour};height:50px;border-radius:10px'></div><small>{colour}</small>", unsafe_allow_html=True)


def face_body_analysis_page() -> None:
    st.header("Face & Body Analysis")
    body_type = st.selectbox("Body proportions", ["Athletic", "Balanced", "Tall and lean", "Curvy", "Petite", "Prefer not to say"], index=0)
    fit = st.selectbox("Preferred fit", ["Relaxed", "Tailored", "Oversized", "Straight", "Slim"])
    st.text_area("Style notes", "I prefer clean lines with soft layering and elevated basics.")
    st.info("STYLER uses self-reported information only, never inferring sensitive characteristics from visual data.")
    if st.button("Generate body-aware styling guide"):
        st.success(f"Based on your {body_type.lower()} profile and {fit.lower()} preference, choose structured silhouettes with soft drape, balanced proportions, and tonal layering.")


def shopping_assistant_page() -> None:
    st.header("Shopping Assistant")
    budget = st.text_input("Budget range", value=st.session_state.profile.get('budget_range', '150-350'))
    category = st.selectbox("Focus area", ["ALL", "TOP WEAR", "BOTTOM WEAR", "FOOTWEAR", "ACCESSORIES"], index=0)
    recommendations = build_shopping_list(st.session_state.profile, budget)
    for item in recommendations:
        if category == "ALL" or category == item['category']:
            st.markdown(f"- **{item['item']}** — {item['budget']} — {item['reason']}")


def saved_outfits_page() -> None:
    st.header("Saved Outfits")
    if st.session_state.outfits:
        for item in st.session_state.outfits:
            st.markdown(f"### {item['name']}")
            st.write(f"Occasion: {item.get('occasion', 'General')}")
            st.write(f"Pieces: {', '.join(item.get('pieces', []))}")
    else:
        st.info("No outfits saved yet. Create one in the Outfit Studio or AI Stylist.")


def profile_page() -> None:
    st.header("My Profile")
    profile = st.session_state.profile
    with st.form("profile_form"):
        st.text_input("Name", key="profile_name", value=profile.get("name", ""))
        st.text_input("Nickname", key="profile_nickname", value=profile.get("preferred_nickname", ""))
        st.text_input("Country", key="profile_country", value=profile.get("country", ""))
        st.text_input("Location", key="profile_location", value=profile.get("location", ""))
        st.text_input("Preferred aesthetic", key="profile_aesthetic", value=profile.get("preferred_aesthetic", "Minimal luxury"))
        st.text_input("Budget range", key="profile_budget", value=profile.get("budget_range", "150-350"))
        st.text_input("Favourite colours", key="profile_favourite_colours", value=", ".join(profile.get("favourite_colours", [])))
        submitted = st.form_submit_button("Update profile")
        if submitted:
            profile.update({
                "name": st.session_state.get("profile_name", ""),
                "preferred_nickname": st.session_state.get("profile_nickname", ""),
                "country": st.session_state.get("profile_country", ""),
                "location": st.session_state.get("profile_location", ""),
                "preferred_aesthetic": st.session_state.get("profile_aesthetic", "Minimal luxury"),
                "budget_range": st.session_state.get("profile_budget", "150-350"),
                "favourite_colours": [c.strip() for c in str(st.session_state.get("profile_favourite_colours", "")).split(",") if c.strip()],
                "is_onboarded": True,
            })
            st.session_state.profile = profile
            save_session_data()
            st.success("Profile updated.")


def settings_page() -> None:
    st.header("Settings")
    st.toggle("Enable seasonal reminders", value=True, key="seasonal_reminders")
    st.toggle("Smart outfit alerts", value=True, key="smart_outfit_alerts")
    st.selectbox("Default shopping budget", ["Under $150", "$150-$300", "$300-$500", "$500+"], index=1, key="default_budget")
    if st.button("Reset profile"):
        st.session_state.profile = DEFAULT_PROFILE.copy()
        st.session_state.wardrobe = []
        st.session_state.outfits = []
        st.session_state.voice_response = ""
        st.session_state.voice_response_id = ""
        st.session_state.voice_last_outfit = None
        st.session_state.voice_last_occasion = None
        st.session_state.voice_recent_combinations = []
        save_session_data()
        st.success("Profile and local style data reset.")
        st.rerun()
    st.warning("This will clear your local STYLER data.")


def render_navigation() -> None:
    st.sidebar.markdown(
        """
        <div style="padding:1rem 0.5rem 0.5rem 0.5rem; text-align:center;">
            <div class="brand-mark" style="margin-bottom:0.5rem;">STYLER</div>
            <div style="font-size:1.3rem; font-weight:700; letter-spacing:-0.04em; color:#2f241f;">Your wardrobe intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    pages = [
        "Home",
        "My Wardrobe",
        "Colour Analysis",
        "AI Stylist",
        "Outfit Studio",
        "Occasion Styling",
        "Face & Body Analysis",
        "Shopping Assistant",
        "Saved Outfits",
        "My Profile",
        "Settings",
    ]
    choice = st.sidebar.radio("Navigation", pages, index=0)
    st.session_state.nav = choice
    return choice


def main() -> None:
    initialize_state()
    render_header()
    page = render_navigation()
    if not st.session_state.profile.get("is_onboarded"):
        onboarding_form()
        return
    if page == "Home":
        home_page()
    elif page == "My Wardrobe":
        wardrobe_page()
    elif page == "Colour Analysis":
        colour_analysis_page()
    elif page == "AI Stylist":
        stylist_page()
    elif page == "Outfit Studio":
        outfit_studio_page()
    elif page == "Occasion Styling":
        occasion_styling_page()
    elif page == "Face & Body Analysis":
        face_body_analysis_page()
    elif page == "Shopping Assistant":
        shopping_assistant_page()
    elif page == "Saved Outfits":
        saved_outfits_page()
    elif page == "My Profile":
        profile_page()
    elif page == "Settings":
        settings_page()


if __name__ == "__main__":
    main()
