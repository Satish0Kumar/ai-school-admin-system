"""
patch_plotly_dark.py
Run once from project root: python patch_plotly_dark.py
Replaces hardcoded plot_bgcolor/paper_bgcolor/font color in all page files.
"""
import re
from pathlib import Path

FILES = [
    "frontend/pages/1_📊_Dashboard.py",
    "frontend/pages/3_👤_Student_Profile.py",
    "frontend/pages/4_🎯_Predictions.py",
    "frontend/pages/8_🧠_Behavioral_Dashboard.py",
    "frontend/pages/9_📝_Marks_Entry.py",
    "frontend/pages/10_🔁_Batch_Analysis.py",
    "frontend/pages/11_📧_Parent_Portal.py",
    "frontend/pages/12_📈_Analytics.py",
]

# Adds import at top of file if not already there
IMPORT_LINE = "from frontend.utils.ui_helpers import get_plotly_layout\n"

# Regex: matches plot_bgcolor/paper_bgcolor/font color lines INSIDE update_layout()
PATTERNS_TO_REMOVE = [
    r"\s*plot_bgcolor\s*=\s*['\"].*?['\"],?\n",
    r"\s*paper_bgcolor\s*=\s*['\"].*?['\"],?\n",
    r"\s*font\s*=\s*dict\s*\(\s*color\s*=\s*['\"]#[0-9a-fA-F]+['\"].*?\),?\n",
]

def patch_file(filepath):
    path = Path(filepath)
    if not path.exists():
        print(f"  ⚠️  SKIP (not found): {filepath}")
        return

    content = path.read_text(encoding="utf-8")
    original = content

    # 1. Add import if missing
    if "get_plotly_layout" not in content:
        # Insert after last existing import block
        insert_after = "from frontend.utils.ui_helpers import inject_theme_css"
        if insert_after in content:
            content = content.replace(
                insert_after,
                insert_after + "\nfrom frontend.utils.ui_helpers import get_plotly_layout"
            )
        else:
            # Fallback: add after first import line
            content = IMPORT_LINE + content

    # 2. Strip hardcoded plot_bgcolor / paper_bgcolor / font color from update_layout calls
    for pattern in PATTERNS_TO_REMOVE:
        content = re.sub(pattern, "\n", content)

    # 3. Append **get_plotly_layout() to every fig.update_layout( call
    #    Strategy: find update_layout( blocks and inject the helper
    #    We use a simple marker: if update_layout has no get_plotly_layout yet, add it
    def inject_helper(match):
        full = match.group(0)
        if "get_plotly_layout" in full:
            return full  # already patched
        # Insert **get_plotly_layout() as first argument
        return full.replace(
            "update_layout(",
            "update_layout(**get_plotly_layout(),\n        "
        )

    content = re.sub(
        r'\.update_layout\s*\(',
        lambda m: m.group(0).replace(
            "update_layout(",
            "update_layout(**get_plotly_layout(), "
        ) if "get_plotly_layout" not in m.group(0) else m.group(0),
        content
    )

    if content != original:
        path.write_text(content, encoding="utf-8")
        print(f"  ✅ Patched: {filepath}")
    else:
        print(f"  ℹ️  No changes: {filepath}")

print("\n🔧 Patching Plotly charts for dark mode...\n")
for f in FILES:
    patch_file(f)
print("\n✅ Done! Restart Streamlit to see changes.\n")
