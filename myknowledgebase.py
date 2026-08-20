import streamlit as st
from pathlib import Path
import re
import yaml

# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="My Knowledge Base",
    page_icon="📚",
    layout="wide"
)

NOTES_DIR = Path("notes")
NOTES_DIR.mkdir(exist_ok=True)


# ============================================================
# NOTE FUNCTIONS
# ============================================================

def slugify(text):
    """Convert title into a safe filename."""

    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text)

    return text


def get_note_files():
    """Return all markdown files."""

    return sorted(
        NOTES_DIR.glob("*.md"),
        key=lambda x: x.name.lower()
    )


def read_note(file_path):
    """Read a markdown note and return metadata + content."""

    text = file_path.read_text(
        encoding="utf-8"
    )

    metadata = {}
    content = text

    # --------------------------------------------------------
    # Read YAML front matter
    # --------------------------------------------------------

    if text.startswith("---"):

        parts = text.split("---", 2)

        if len(parts) == 3:

            try:
                metadata = yaml.safe_load(parts[1]) or {}
                content = parts[2].strip()

            except Exception:
                metadata = {}

    return metadata, content


def save_note(title, category, tags, content):

    filename = slugify(title) + ".md"

    file_path = NOTES_DIR / filename

    # --------------------------------------------------------
    # Prepare tags
    # --------------------------------------------------------

    tag_list = [
        tag.strip()
        for tag in tags.split(",")
        if tag.strip()
    ]

    # --------------------------------------------------------
    # YAML metadata
    # --------------------------------------------------------

    metadata = {
        "title": title,
        "category": category,
        "tags": tag_list
    }

    yaml_text = yaml.dump(
        metadata,
        allow_unicode=True,
        sort_keys=False
    )

    # --------------------------------------------------------
    # Final markdown
    # --------------------------------------------------------

    final_text = (
        "---\n"
        + yaml_text
        + "---\n\n"
        + content
    )

    file_path.write_text(
        final_text,
        encoding="utf-8"
    )

    return file_path


def delete_note(file_path):

    if file_path.exists():
        file_path.unlink()


# ============================================================
# LOAD NOTES
# ============================================================

notes = []

for file_path in get_note_files():

    metadata, content = read_note(file_path)

    title = metadata.get(
        "title",
        file_path.stem.replace("-", " ").title()
    )

    category = metadata.get(
        "category",
        "General"
    )

    tags = metadata.get(
        "tags",
        []
    )

    if isinstance(tags, str):
        tags = [tags]

    notes.append({
        "file": file_path,
        "title": title,
        "category": category,
        "tags": tags,
        "content": content
    })


# ============================================================
# SESSION STATE
# ============================================================

if "selected_note" not in st.session_state:
    st.session_state.selected_note = None

if "page" not in st.session_state:
    st.session_state.page = "Home"


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 My Knowledge Base")

st.sidebar.divider()

# ------------------------------------------------------------
# Navigation
# ------------------------------------------------------------

if st.sidebar.button(
    "🏠 Home",
    use_container_width=True
):
    st.session_state.page = "Home"
    st.session_state.selected_note = None

if st.sidebar.button(
    "📝 Add New Note",
    use_container_width=True
):
    st.session_state.page = "Add Note"
    st.session_state.selected_note = None


st.sidebar.divider()

# ------------------------------------------------------------
# Categories
# ------------------------------------------------------------

st.sidebar.subheader("Categories")

categories = sorted(
    set(
        note["category"]
        for note in notes
    )
)

for category in categories:

    count = sum(
        1
        for note in notes
        if note["category"] == category
    )

    if st.sidebar.button(
        f"📁 {category} ({count})",
        use_container_width=True,
        key=f"cat_{category}"
    ):

        st.session_state.page = "Category"
        st.session_state.selected_category = category
        st.session_state.selected_note = None


# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "Home":

    st.title("📚 My Knowledge Base")

    st.write(
        "Your personal collection of notes, ideas and knowledge."
    )

    st.divider()

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    search = st.text_input(
        "🔍 Search your notes",
        placeholder="Search by title, category, tag or content..."
    )

    # --------------------------------------------------------
    # Filter
    # --------------------------------------------------------

    filtered_notes = notes

    if search:

        search_text = search.lower()

        filtered_notes = []

        for note in notes:

            searchable_text = " ".join([
                note["title"],
                note["category"],
                " ".join(note["tags"]),
                note["content"]
            ]).lower()

            if search_text in searchable_text:

                filtered_notes.append(note)

    # --------------------------------------------------------
    # Results
    # --------------------------------------------------------

    if search:

        st.subheader(
            f"Search Results ({len(filtered_notes)})"
        )

    else:

        st.subheader(
            f"All Notes ({len(filtered_notes)})"
        )

    if not filtered_notes:

        st.info(
            "No notes found."
        )

    else:

        for note in filtered_notes:

            with st.container(border=True):

                col1, col2 = st.columns(
                    [5, 1]
                )

                with col1:

                    st.subheader(
                        note["title"]
                    )

                    st.caption(
                        f"📁 {note['category']}"
                    )

                    if note["tags"]:

                        st.caption(
                            "🏷️ "
                            + ", ".join(note["tags"])
                        )

                    # Small preview

                    preview = note["content"]

                    preview = re.sub(
                        r"\n+",
                        " ",
                        preview
                    )

                    if len(preview) > 200:

                        preview = (
                            preview[:200]
                            + "..."
                        )

                    st.write(preview)

                with col2:

                    if st.button(
                        "📖 Read",
                        key=f"read_{note['file'].name}"
                    ):

                        st.session_state.selected_note = note[
                            "file"
                        ]

                        st.session_state.page = "Read"

                        st.rerun()


# ============================================================
# CATEGORY PAGE
# ============================================================

elif st.session_state.page == "Category":

    category = st.session_state.selected_category

    st.title(
        f"📁 {category}"
    )

    category_notes = [
        note
        for note in notes
        if note["category"] == category
    ]

    st.write(
        f"{len(category_notes)} notes"
    )

    st.divider()

    for note in category_notes:

        with st.container(border=True):

            st.subheader(
                note["title"]
            )

            if note["tags"]:

                st.caption(
                    "🏷️ "
                    + ", ".join(note["tags"])
                )

            preview = re.sub(
                r"\n+",
                " ",
                note["content"]
            )

            if len(preview) > 250:

                preview = preview[:250] + "..."

            st.write(preview)

            if st.button(
                "📖 Read Note",
                key=f"category_read_{note['file'].name}"
            ):

                st.session_state.selected_note = note[
                    "file"
                ]

                st.session_state.page = "Read"

                st.rerun()


# ============================================================
# READ NOTE
# ============================================================

elif st.session_state.page == "Read":

    file_path = st.session_state.selected_note

    if not file_path or not file_path.exists():

        st.error(
            "Note not found."
        )

        st.stop()

    metadata, content = read_note(
        file_path
    )

    title = metadata.get(
        "title",
        file_path.stem
    )

    category = metadata.get(
        "category",
        "General"
    )

    tags = metadata.get(
        "tags",
        []
    )

    st.caption(
        f"📁 {category}"
    )

    st.title(title)

    if tags:

        st.caption(
            "🏷️ "
            + ", ".join(tags)
        )

    st.divider()

    # --------------------------------------------------------
    # Display Markdown
    # --------------------------------------------------------

    st.markdown(
        content
    )

    st.divider()

    # --------------------------------------------------------
    # Buttons
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "← Back",
            use_container_width=True
        ):

            st.session_state.page = "Home"
            st.session_state.selected_note = None

            st.rerun()

    with col2:

        if st.button(
            "✏️ Edit",
            use_container_width=True
        ):

            st.session_state.page = "Edit"

            st.rerun()

    with col3:

        if st.button(
            "🗑️ Delete",
            use_container_width=True
        ):

            st.session_state.confirm_delete = True

    # --------------------------------------------------------
    # Delete confirmation
    # --------------------------------------------------------

    if st.session_state.get(
        "confirm_delete",
        False
    ):

        st.warning(
            "Are you sure you want to delete this note?"
        )

        c1, c2 = st.columns(2)

        with c1:

            if st.button(
                "Yes, Delete",
                use_container_width=True
            ):

                delete_note(
                    file_path
                )

                st.session_state.page = "Home"
                st.session_state.selected_note = None
                st.session_state.confirm_delete = False

                st.success(
                    "Note deleted."
                )

                st.rerun()

        with c2:

            if st.button(
                "Cancel",
                use_container_width=True
            ):

                st.session_state.confirm_delete = False

                st.rerun()


# ============================================================
# ADD NOTE
# ============================================================

elif st.session_state.page == "Add Note":

    st.title("📝 Add New Note")

    title = st.text_input(
        "Heading / Title",
        placeholder="Example: VWAP Convergence"
    )

    category = st.text_input(
        "Category",
        placeholder="Example: Trading"
    )

    tags = st.text_input(
        "Tags",
        placeholder="Example: VWAP, Entry, Strategy"
    )

    st.subheader("Note")

    content = st.text_area(
        "Write your note here using Markdown",
        height=400,
        placeholder="""# VWAP Convergence

## Concept

Write your notes here...

## Important Points

- Point 1
- Point 2
- Point 3
"""
    )

    if st.button(
        "💾 Save Note",
        type="primary",
        use_container_width=True
    ):

        if not title.strip():

            st.error(
                "Please enter a title."
            )

        elif not category.strip():

            st.error(
                "Please enter a category."
            )

        elif not content.strip():

            st.error(
                "Please enter some content."
            )

        else:

            file_path = save_note(
                title=title.strip(),
                category=category.strip(),
                tags=tags,
                content=content
            )

            st.success(
                f"Note saved: {file_path.name}"
            )

            st.session_state.page = "Home"

            st.rerun()


# ============================================================
# EDIT NOTE
# ============================================================

elif st.session_state.page == "Edit":

    file_path = st.session_state.selected_note

    if not file_path or not file_path.exists():

        st.error(
            "Note not found."
        )

        st.stop()

    metadata, content = read_note(
        file_path
    )

    title = st.text_input(
        "Heading / Title",
        value=metadata.get(
            "title",
            ""
        )
    )

    category = st.text_input(
        "Category",
        value=metadata.get(
            "category",
            "General"
        )
    )

    existing_tags = metadata.get(
        "tags",
        []
    )

    if isinstance(
        existing_tags,
        list
    ):

        existing_tags = ", ".join(
            existing_tags
        )

    tags = st.text_input(
        "Tags",
        value=existing_tags
    )

    content = st.text_area(
        "Note",
        value=content,
        height=500
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "💾 Save Changes",
            type="primary",
            use_container_width=True
        ):

            save_note(
                title=title.strip(),
                category=category.strip(),
                tags=tags,
                content=content
            )

            # If title changed, old file can be removed

            new_file = NOTES_DIR / (
                slugify(title) + ".md"
            )

            if (
                new_file != file_path
                and file_path.exists()
            ):

                file_path.unlink()

            st.session_state.selected_note = new_file
            st.session_state.page = "Read"

            st.rerun()

    with col2:

        if st.button(
            "Cancel",
            use_container_width=True
        ):

            st.session_state.page = "Read"

            st.rerun()