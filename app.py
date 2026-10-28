import streamlit as st
import json
from datetime import datetime
from services.memory_repository import MemoryRepository
from services.ollama_client import OllamaClient
from services.story_writer import StoryWriter
from services.interview_questions import InterviewQuestionsGenerator
from services.remembrance_builder import RemembranceBuilder
from services.export_service import ExportService
import config

# Page setup
st.set_page_config(
    page_title="Echoes AI — Private Memory Journal",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Warm Cream & Burgundy Aesthetic CSS
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

    :root {
        --bg-cream: #FAF7F2;
        --card-bg: #FFFFFF;
        --burgundy: #6B1D2F;
        --burgundy-light: #8E2B40;
        --burgundy-soft: #F5EAEB;
        --marigold: #D9822B;
        --marigold-gold: #E5A93C;
        --text-dark: #2B2320;
        --text-muted: #665C54;
        --border-color: #E8DFD5;
    }

    .stApp {
        background-color: var(--bg-cream);
        color: var(--text-dark);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4 {
        font-family: 'Crimson Pro', Georgia, serif;
        color: var(--burgundy) !important;
        font-weight: 600;
    }

    .echoes-banner {
        background: linear-gradient(135deg, #FAF4EB 0%, #F5EAEB 100%);
        border: 1px solid var(--border-color);
        border-left: 5px solid var(--burgundy);
        padding: 24px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 2px 8px rgba(107, 29, 47, 0.04);
    }

    .echoes-banner h1 {
        margin: 0;
        font-size: 2.2rem;
        letter-spacing: -0.5px;
    }

    .echoes-tagline {
        color: var(--burgundy-light);
        font-family: 'Crimson Pro', Georgia, serif;
        font-style: italic;
        font-size: 1.25rem;
        margin-top: 4px;
    }

    .echoes-card {
        background: #FFFFFF;
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .echoes-card:hover {
        border-color: var(--marigold);
        box-shadow: 0 4px 12px rgba(217, 130, 43, 0.08);
    }

    .badge-pill {
        display: inline-block;
        padding: 3px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 9999px;
        background-color: var(--burgundy-soft);
        color: var(--burgundy);
        border: 1px solid rgba(107, 29, 47, 0.15);
        margin-right: 6px;
        margin-bottom: 4px;
    }

    .badge-tag {
        display: inline-block;
        padding: 2px 8px;
        font-size: 0.72rem;
        border-radius: 9999px;
        background-color: #FDF4E7;
        color: var(--marigold);
        border: 1px solid rgba(217, 130, 43, 0.25);
        margin-right: 4px;
    }

    .tribute-box {
        background: #FFFDF9;
        border: 1px solid #EAD8C7;
        border-top: 4px solid var(--marigold);
        border-radius: 10px;
        padding: 24px;
        margin-top: 16px;
        font-family: 'Crimson Pro', Georgia, serif;
        font-size: 1.15rem;
        line-height: 1.7;
    }

    .privacy-notice {
        background: #F8F9FA;
        border: 1px solid #DCE1E5;
        border-left: 4px solid #4A5568;
        padding: 12px 16px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #4A5568;
        margin: 10px 0;
    }

    /* Buttons */
    div.stButton > button {
        background-color: var(--burgundy);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        background-color: var(--burgundy-light);
        color: white;
        box-shadow: 0 2px 6px rgba(107, 29, 47, 0.25);
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Initialize singletons in session_state
if "repo" not in st.session_state:
    st.session_state.repo = MemoryRepository(config.DB_PATH)
if "ollama" not in st.session_state:
    st.session_state.ollama = OllamaClient(host=config.DEFAULT_OLLAMA_HOST)
if "story_writer" not in st.session_state:
    st.session_state.story_writer = StoryWriter(st.session_state.ollama)
if "interview_gen" not in st.session_state:
    st.session_state.interview_gen = InterviewQuestionsGenerator(st.session_state.ollama)
if "remembrance_builder" not in st.session_state:
    st.session_state.remembrance_builder = RemembranceBuilder(st.session_state.ollama)
if "export_service" not in st.session_state:
    st.session_state.export_service = ExportService(st.session_state.repo)

repo = st.session_state.repo
ollama = st.session_state.ollama
writer = st.session_state.story_writer
interviewer = st.session_state.interview_gen
remembrance = st.session_state.remembrance_builder
exporter = st.session_state.export_service

# Sidebar Navigation & Local Status
with st.sidebar:
    st.markdown("### 📖 **Echoes AI**")
    st.caption("Ghost in the Machine • Hacktoberfest 2026")
    st.write("---")

    nav_choice = st.radio(
        "Navigation",
        [
            "📝 Write & Enhance Memory",
            "📚 Memory Library",
            "🕯️ Remembrance Page",
            "📦 Export & Backup",
            "🛡️ Privacy & Settings"
        ],
        label_visibility="collapsed"
    )

    st.write("---")
    st.markdown("#### ⚙️ Local AI Engine")
    conn_status = ollama.check_connection()
    if conn_status["connected"]:
        st.success(f"🟢 Ollama Local ({len(conn_status['models'])} models)")
        available_models = conn_status["models"] or [config.DEFAULT_MODEL]
        selected_model = st.selectbox("Active Model", available_models, index=0)
    else:
        st.warning("🟠 Ollama Offline / Not Running")
        st.caption("AI features will provide gentle offline prompts. To enable local LLM inference, run `ollama serve`.")
        selected_model = config.DEFAULT_MODEL

    st.write("---")
    st.caption("🔒 **100% Local-First & Private**\nNo cloud APIs, no external telemetry, no data leaves this device.")

# Header Banner
st.markdown(f"""
<div class="echoes-banner">
    <h1>Echoes AI</h1>
    <div class="echoes-tagline">“{config.APP_TAGLINE}”</div>
    <div style="font-size: 0.95rem; color: #5C524B; margin-top: 6px;">
        A quiet sanctuary to preserve family stories, cherished traditions, and memories of loved ones with local AI assistance.
    </div>
</div>
""", unsafe_allow_html=True)


# ==========================================
# 1. WRITE & ENHANCE MEMORY
# ==========================================
if nav_choice == "📝 Write & Enhance Memory":
    st.markdown("### 📝 Preserve a Memory")
    st.markdown(
        "Write your raw thoughts, fragments, or rough notes below. You can save your original version "
        "immediately, generate gentle interview questions to unlock deeper sensory details, or let the local AI "
        "weave your notes into a heartfelt personal story."
    )

    # Active editing session memory ID
    editing_id = st.session_state.get("editing_memory_id", None)
    initial_data = {}
    if editing_id:
        initial_data = repo.get_memory(editing_id) or {}
        st.info(f"✏️ Currently editing existing memory: **{initial_data.get('title')}** (ID #{editing_id})")
        if st.button("Cancel Editing / Start Fresh"):
            st.session_state.editing_memory_id = None
            st.rerun()

    col1, col2 = st.columns([2, 1])

    with col1:
        mem_title = st.text_input(
            "Memory Title",
            value=initial_data.get("title", ""),
            placeholder="e.g., Grandfather's Sunday Morning Lemonade Ritual"
        )
        mem_notes = st.text_area(
            "Original Story / Rough Notes *",
            value=initial_data.get("raw_notes", ""),
            height=200,
            placeholder="Write freely: who was there, what room you were in, the sounds, smells, laughs, or the feelings you remember..."
        )

    with col2:
        mem_category = st.selectbox(
            "Category",
            config.MEMORY_CATEGORIES,
            index=config.MEMORY_CATEGORIES.index(initial_data.get("category"))
            if initial_data.get("category") in config.MEMORY_CATEGORIES else 0
        )
        mem_date = st.text_input(
            "Approximate Date / Era",
            value=initial_data.get("approximate_date", ""),
            placeholder="e.g., Summer 1994, or Autumn around Thanksgiving"
        )
        mem_people = st.text_input(
            "People & Relationships",
            value=initial_data.get("people", ""),
            placeholder="e.g., Grandma Clara, Uncle Ray, little cousin Sam"
        )
        mem_tags = st.text_input(
            "Tags (comma-separated)",
            value=initial_data.get("tags", ""),
            placeholder="porch, summer, cooking, laughter"
        )
        is_remembrance = st.checkbox(
            "🕯️ Mark as Remembrance / Tribute memory",
            value=bool(initial_data.get("is_remembrance", 0)),
            help="Flags this story for easy inclusion in a memorial tribute."
        )

    # Action Toolbar
    col_a, col_b, col_c, col_d = st.columns([1.2, 1.2, 1.2, 1])

    with col_a:
        save_raw = st.button("💾 Save Original Notes Only")
    with col_b:
        generate_questions = st.button("💭 Generate Interview Questions")
    with col_c:
        suggest_title_btn = st.button("💡 Suggest Title with AI")
    with col_d:
        clear_btn = st.button("🗑️ Clear Form")

    if clear_btn:
        st.session_state.editing_memory_id = None
        st.session_state.pop("generated_questions", None)
        st.session_state.pop("generated_story", None)
        st.rerun()

    if suggest_title_btn:
        if not mem_notes.strip():
            st.warning("Please enter some rough notes first to suggest a title.")
        else:
            with st.spinner("Reflecting on title ideas..."):
                t_res = writer.suggest_title(mem_notes, mem_category, model=selected_model)
                if t_res["success"]:
                    st.success(f"Suggested Title: **{t_res['title']}**")
                else:
                    st.error(t_res["error"])

    # Handle Interview Questions Assistant
    if generate_questions:
        if not mem_notes.strip():
            st.warning("Please provide rough notes before generating follow-up questions.")
        else:
            with st.spinner("Generating gentle oral history prompts..."):
                q_res = interviewer.generate_questions(
                    raw_notes=mem_notes,
                    title=mem_title,
                    category=mem_category,
                    people=mem_people,
                    model=selected_model
                )
                st.session_state.generated_questions = q_res["questions"]
                if q_res.get("error"):
                    st.info(q_res["error"])

    # Display Interview Assistant if available
    if "generated_questions" in st.session_state and st.session_state.generated_questions:
        st.markdown("---")
        st.markdown("#### 💭 Gentle Follow-Up Prompts (Oral History Interview)")
        st.caption("Take your time with these optional questions to expand your memory. You can skip any question.")
        
        answered_notes = []
        for i, q in enumerate(st.session_state.generated_questions, 1):
            st.markdown(f"**{i}. {q}**")
            ans = st.text_input(f"Your answer to #{i} (optional)", key=f"q_ans_{i}")
            if ans.strip():
                answered_notes.append(f"- *{q}*\n  {ans.strip()}")

        if answered_notes and st.button("➕ Append Answers to Raw Notes"):
            addition = "\n\nReflection Details:\n" + "\n".join(answered_notes)
            mem_notes += addition
            st.success("Appended reflection details to notes above!")

    st.markdown("---")
    st.markdown("### ✨ AI Story Enhancement")
    st.caption("Transform rough notes into a readable narrative while strictly preserving your authentic facts.")

    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        chosen_style = st.radio(
            "Choose Narrative Voice",
            options=list(config.STORY_STYLES.keys()),
            format_func=lambda k: f"**{config.STORY_STYLES[k]['label']}** — {config.STORY_STYLES[k]['description']}",
            horizontal=False
        )
    with col_s2:
        st.markdown("**Ethical Safeguards Active:**")
        st.markdown("""
        - ✅ Zero external cloud calls
        - ✅ Grounded in your supplied names & details
        - ✅ Never fabricates false history or deceased contact
        """)

    if st.button("✨ Craft Enhanced Story"):
        if not mem_notes.strip():
            st.warning("Please enter rough notes to enhance.")
        else:
            with st.spinner("Weaving your memories locally with care..."):
                enh_res = writer.enhance_story(
                    raw_notes=mem_notes,
                    title=mem_title,
                    approximate_date=mem_date,
                    people=mem_people,
                    category=mem_category,
                    tags=mem_tags,
                    style=chosen_style,
                    model=selected_model
                )
                if enh_res["success"]:
                    st.session_state.generated_story = enh_res["story"]
                    st.session_state.last_style = chosen_style
                else:
                    st.error(f"Could not enhance story: {enh_res['error']}")

    # Preview and Final Save
    enhanced_story_val = st.session_state.get(
        "generated_story",
        initial_data.get("enhanced_story", "")
    )

    if enhanced_story_val:
        st.markdown("#### 📖 Review & Edit Enhanced Narrative")
        st.caption("You have full control. Review and edit the wording below before saving:")
        editable_story = st.text_area(
            "Enhanced Story (Editable)",
            value=enhanced_story_val,
            height=260
        )
    else:
        editable_story = ""

    # Primary Save Button
    if st.button("💾 Save Memory to Library", type="primary"):
        if not mem_notes.strip():
            st.warning("Cannot save: Memory rough notes cannot be empty.")
        else:
            save_payload = {
                "id": editing_id,
                "title": mem_title or "Untitled Memory",
                "raw_notes": mem_notes,
                "enhanced_story": editable_story,
                "approximate_date": mem_date,
                "people": mem_people,
                "category": mem_category,
                "tags": mem_tags,
                "style_used": st.session_state.get("last_style", initial_data.get("style_used", "")),
                "is_remembrance": is_remembrance
            }
            new_id = repo.save_memory(save_payload)
            st.success(f"🎉 Memory successfully saved! (ID #{new_id})")
            st.session_state.editing_memory_id = None
            st.session_state.pop("generated_story", None)
            st.session_state.pop("generated_questions", None)

    if save_raw:
        if not mem_notes.strip():
            st.warning("Cannot save: Memory rough notes cannot be empty.")
        else:
            save_payload = {
                "id": editing_id,
                "title": mem_title or "Untitled Memory",
                "raw_notes": mem_notes,
                "enhanced_story": initial_data.get("enhanced_story", ""),
                "approximate_date": mem_date,
                "people": mem_people,
                "category": mem_category,
                "tags": mem_tags,
                "is_remembrance": is_remembrance
            }
            new_id = repo.save_memory(save_payload)
            st.success(f"💾 Original notes preserved safely! (ID #{new_id})")


# ==========================================
# 2. MEMORY LIBRARY
# ==========================================
elif nav_choice == "📚 Memory Library":
    st.markdown("### 📚 Personal Memory Library")
    st.caption("Explore, search, and cherish your preserved personal archives.")

    # Search and Filter Toolbar
    f_col1, f_col2, f_col3, f_col4 = st.columns([2, 1.2, 1.2, 1])
    with f_col1:
        search_query = st.text_input("🔍 Search memories", placeholder="Search keywords, people, or places...")
    with f_col2:
        all_cats = ["All"] + config.MEMORY_CATEGORIES
        cat_filter = st.selectbox("Category", all_cats)
    with f_col3:
        all_tags = ["All"] + repo.get_unique_tags()
        tag_filter = st.selectbox("Tag", all_tags)
    with f_col4:
        rem_only = st.checkbox("🕯️ Remembrance Only")

    memories = repo.get_all_memories(
        category=None if cat_filter == "All" else cat_filter,
        search_query=search_query if search_query.strip() else None,
        tag=None if tag_filter == "All" else tag_filter,
        remembrance_only=rem_only
    )

    st.write(f"Showing **{len(memories)}** preserved stories")

    if not memories:
        st.info("No memories match your search. Write your first story in the **Write & Enhance Memory** tab!")
    else:
        for mem in memories:
            with st.container():
                st.markdown(f"""
                <div class="echoes-card">
                    <div style="display: flex; justify-content: space-between; align-items: baseline;">
                        <h3 style="margin: 0; font-size: 1.45rem;">{mem['title']}</h3>
                        <span style="font-size: 0.82rem; color: #7B726B;">Updated: {mem['updated_at'][:10]}</span>
                    </div>
                    <div style="margin: 8px 0;">
                        <span class="badge-pill">{mem['category']}</span>
                        {f"<span class='badge-pill' style='background:#FDF0E6; color:#B45309;'>🕯️ Remembrance</span>" if mem.get('is_remembrance') else ""}
                        {f"<span style='font-size: 0.85rem; color: #5C524B; margin-left: 8px;'>📅 {mem['approximate_date']}</span>" if mem.get('approximate_date') else ""}
                        {f"<span style='font-size: 0.85rem; color: #5C524B; margin-left: 8px;'>👥 {mem['people']}</span>" if mem.get('people') else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                tab_story, tab_raw, tab_actions = st.tabs(["📖 Preserved Story", "📝 Original Notes", "⚙️ Actions & Export"])

                with tab_story:
                    if mem.get("enhanced_story"):
                        st.markdown(mem["enhanced_story"])
                        if mem.get("style_used"):
                            st.caption(f"Style: {mem['style_used'].title()}")
                    else:
                        st.info("No enhanced story generated yet. You can edit this entry to polish it with local AI.")

                with tab_raw:
                    st.text_area("Original User Notes", value=mem.get("raw_notes", ""), height=130, disabled=True, key=f"raw_{mem['id']}")

                with tab_actions:
                    act_c1, act_c2, act_c3, act_c4 = st.columns([1, 1, 1, 1])
                    with act_c1:
                        if st.button("✏️ Edit Entry", key=f"edit_{mem['id']}"):
                            st.session_state.editing_memory_id = mem["id"]
                            st.rerun()

                    with act_c2:
                        md_content = exporter.export_memory_to_markdown(mem["id"])
                        st.download_button(
                            "📥 Download Markdown",
                            data=md_content,
                            file_name=f"echoes_memory_{mem['id']}.md",
                            mime="text/markdown",
                            key=f"dl_md_{mem['id']}"
                        )

                    with act_c3:
                        txt_content = exporter.export_memory_to_txt(mem["id"])
                        st.download_button(
                            "📄 Download TXT",
                            data=txt_content,
                            file_name=f"echoes_memory_{mem['id']}.txt",
                            mime="text/plain",
                            key=f"dl_txt_{mem['id']}"
                        )

                    with act_c4:
                        if st.button("🗑️ Delete", key=f"del_{mem['id']}"):
                            st.session_state[f"confirm_delete_{mem['id']}"] = True

                    if st.session_state.get(f"confirm_delete_{mem['id']}"):
                        st.warning("Are you sure you want to delete this memory? This action cannot be undone.")
                        col_yes, col_no = st.columns(2)
                        with col_yes:
                            if st.button("Yes, permanently delete", key=f"conf_yes_{mem['id']}"):
                                repo.delete_memory(mem["id"])
                                st.session_state.pop(f"confirm_delete_{mem['id']}", None)
                                st.success("Memory deleted.")
                                st.rerun()
                        with col_no:
                            if st.button("Cancel", key=f"conf_no_{mem['id']}"):
                                st.session_state.pop(f"confirm_delete_{mem['id']}", None)
                                st.rerun()

                st.write("")


# ==========================================
# 3. REMEMBRANCE PAGE
# ==========================================
elif nav_choice == "🕯️ Remembrance Page":
    st.markdown("### 🕯️ Personal Remembrance Page")
    st.markdown(
        "A quiet, dignified memorial sanctuary honoring loved ones who have touched our lives. "
        "Echoes AI weaves personal traditions, favorite sayings, and cherished stories into an enduring tribute. "
        "*(Note: Local AI synthesizes only user-provided facts and never claims to contact or channel deceased souls.)*"
    )

    r_tab1, r_tab2 = st.tabs(["✨ Create New Memorial Tribute", "🏛️ Preserved Memorial Profiles"])

    with r_tab1:
        col_r1, col_r2 = st.columns([1.5, 1])

        with col_r1:
            honoree_name = st.text_input("Name of Loved One / Honoree *", placeholder="e.g., Grandmother Martha Vance")
            life_dates = st.text_input("Life Years / Dates (Optional)", placeholder="e.g., 1932 – 2021")
            
            # Allow linking existing memories
            remembrance_mems = repo.get_all_memories(remembrance_only=True)
            mem_options = {f"#{m['id']} {m['title']}": m.get('enhanced_story') or m.get('raw_notes') for m in remembrance_mems}
            selected_mems = st.multiselect(
                "Incorporate Stories from your Library (Remembrance Tagged)",
                options=list(mem_options.keys())
            )

            incorporated_stories = "\n\n".join([mem_options[k] for k in selected_mems])
            user_stories = st.text_area(
                "Personal Stories & Memories",
                value=incorporated_stories,
                height=150,
                placeholder="Stories of kindness, quiet strength, holiday dinners, or road trips..."
            )

        with col_r2:
            sayings = st.text_area(
                "Words & Favorite Sayings",
                height=110,
                placeholder="Phrases they often repeated, advice they lived by, words of encouragement..."
            )
            traditions = st.text_area(
                "Important Traditions & Customs",
                height=110,
                placeholder="Sunday afternoon walks, secret pie crust recipes, holiday songs..."
            )
            reflections = st.text_area(
                "Personal Reflection / Message",
                height=100,
                placeholder="What you miss most, or a message of gratitude..."
            )

        if st.button("🕯️ Draft Memorial Page with Local AI", type="primary"):
            if not honoree_name.strip():
                st.warning("Please provide the honoree's name.")
            else:
                with st.spinner("Compiling a dignified tribute locally..."):
                    trib_res = remembrance.draft_tribute(
                        name=honoree_name,
                        dates=life_dates,
                        stories=user_stories,
                        sayings=sayings,
                        traditions=traditions,
                        notes=reflections,
                        model=selected_model
                    )
                    st.session_state.current_tribute = trib_res["tribute"]
                    if trib_res.get("is_fallback"):
                        st.info(trib_res.get("error"))

        if "current_tribute" in st.session_state:
            st.markdown("---")
            st.markdown("#### 📜 Review Memorial Tribute")
            editable_tribute = st.text_area(
                "Memorial Tribute (Markdown Editable)",
                value=st.session_state.current_tribute,
                height=300
            )

            col_s1, col_s2 = st.columns(2)
            with col_s1:
                if st.button("💾 Save to Memorial Profiles"):
                    profile_id = repo.save_remembrance_profile({
                        "honoree_name": honoree_name,
                        "dates": life_dates,
                        "sayings": sayings,
                        "traditions": traditions,
                        "compiled_tribute": editable_tribute,
                        "linked_memory_ids": ", ".join(selected_mems)
                    })
                    st.success(f"Memorial profile permanently saved! (Profile #{profile_id})")
            with col_s2:
                st.download_button(
                    "📥 Download Memorial Tribute (.md)",
                    data=editable_tribute,
                    file_name=f"remembrance_{honoree_name.lower().replace(' ', '_')}.md",
                    mime="text/markdown"
                )

            # Visual Rendering Preview
            st.markdown("<div class='tribute-box'>", unsafe_allow_html=True)
            st.markdown(editable_tribute)
            st.markdown("</div>", unsafe_allow_html=True)

    with r_tab2:
        profiles = repo.get_all_remembrance_profiles()
        if not profiles:
            st.info("No memorial profiles created yet.")
        else:
            for prof in profiles:
                with st.expander(f"🕯️ {prof['honoree_name']} ({prof.get('dates') or 'Undated'})"):
                    st.markdown("<div class='tribute-box'>", unsafe_allow_html=True)
                    st.markdown(prof.get("compiled_tribute", ""))
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.write("")
                    col_p1, col_p2 = st.columns([1, 1])
                    with col_p1:
                        st.download_button(
                            "📥 Export Tribute",
                            data=prof.get("compiled_tribute", ""),
                            file_name=f"tribute_{prof['id']}.md",
                            key=f"dl_prof_{prof['id']}"
                        )
                    with col_p2:
                        if st.button(f"🗑️ Delete Memorial Profile", key=f"del_prof_{prof['id']}"):
                            repo.delete_remembrance_profile(prof["id"])
                            st.success("Profile removed.")
                            st.rerun()


# ==========================================
# 4. EXPORT & BACKUP
# ==========================================
elif nav_choice == "📦 Export & Backup":
    st.markdown("### 📦 Export & Backup")
    st.markdown(
        "Take complete ownership of your personal stories. Export individual files or generate "
        "a verified, complete JSON backup of all memories and memorial tributes."
    )

    st.markdown("#### 💾 Complete System Backup")
    json_backup = exporter.export_all_to_json()
    st.download_button(
        "📥 Download Full JSON Backup",
        data=json_backup,
        file_name=f"echoes_ai_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json"
    )

    st.markdown("---")
    st.markdown("#### 📥 Restore from Backup")
    st.caption("Safely import memories from an Echoes AI JSON backup file. No existing memories will be overwritten silently.")

    uploaded_file = st.file_uploader("Select an Echoes AI Backup JSON file", type=["json"])
    if uploaded_file is not None:
        try:
            content_str = uploaded_file.read().decode("utf-8")
            skip_dups = st.checkbox("Skip duplicate memories (matching title & notes)", value=True)
            if st.button("Start Safe Import"):
                ok, message, count = exporter.validate_and_import_json(content_str, skip_duplicates=skip_dups)
                if ok:
                    st.success(message)
                else:
                    st.error(f"Import failed: {message}")
        except Exception as e:
            st.error(f"Could not read upload: {str(e)}")


# ==========================================
# 5. PRIVACY & SETTINGS
# ==========================================
elif nav_choice == "🛡️ Privacy & Settings":
    st.markdown("### 🛡️ Privacy Controls & Transparency")
    st.markdown(
        "Echoes AI is engineered around local sovereignty, privacy by design, and strict data stewardship."
    )

    st.markdown(f"""
    <div class="privacy-notice">
        <b>Data Storage Notice:</b> Your memories are stored locally in an unencrypted SQLite database at:
        <code>{config.DB_PATH}</code>.<br>
        Local files are stored in plaintext on this machine's disk and rely on your operating system's user permissions.
        Echoes AI does not transmit telemetry, prompts, or personal memories across the network.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 🌟 Ethical Manifesto & Safeguards")
    st.markdown("""
    1. **100% Local Inference:** All story synthesis, interview generation, and title suggestions run on your local device via Ollama.
    2. **No Data Exploitation:** Your personal narratives are never used to train or fine-tune models.
    3. **Respectful Bereavement Principles:** Echoes AI strictly refuses to impersonate deceased relatives or simulate consciousness.
    4. **Original Fidelity:** The application always preserves your original, unedited raw notes alongside any AI-enhanced text.
    5. **Untrusted Data Handling:** Imported JSON files are treated as untrusted data and strictly validated.
    """)

    st.markdown("---")
    st.markdown("#### 🚨 Danger Zone")
    st.markdown("Irrevocably erase all saved memories and memorial profiles from this machine.")

    confirm_box = st.checkbox("I understand that deleting all memories is permanent and cannot be undone.")
    if st.button("🔥 Erase All Memories Locally", type="primary", disabled=not confirm_box):
        if repo.delete_all_memories(confirmation=True):
            st.success("All local memories and memorial profiles have been permanently removed.")
            st.rerun()
        else:
            st.error("Deletion rejected.")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8C827A; font-size: 0.82rem;'>"
    "Echoes AI • Built with Python, Streamlit & Ollama for Hacktoberfest 2026 'Ghost in the Machine' • Local-First & Private"
    "</div>",
    unsafe_allow_html=True
)
