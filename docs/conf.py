# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Sphinx configuration for the Omniverse Performance guide."""

import os
import sys

# -- Path setup ----------------------------------------------------------------
sys.path.insert(0, os.path.abspath("_extensions"))

# -- Project information -------------------------------------------------------
project = "Omniverse Performance"
copyright = "2026, NVIDIA Corporation"
author = "NVIDIA Corporation"
version = "1.0"
release = "1.0.0"

# -- General configuration -----------------------------------------------------
extensions = [
    "myst_parser",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinxcontrib.mermaid",
]

# MyST Parser settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "attrs_inline",
    "attrs_block",
    "tasklist",
    "substitution",
]

myst_heading_anchors = 3
# Open external (off-site) links in a new browser tab so readers keep the guide
# open. MyST built-in (adds target="_blank" + rel="noopener"); internal
# cross-references are unaffected.
myst_links_external_new_tab = True

# Autosection label settings
autosectionlabel_prefix_document = True

# Source settings
source_suffix = {
    ".md": "markdown",
    ".rst": "restructuredtext",
}
master_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "README.md", ".venv", "cache"]

# -- HTML output ---------------------------------------------------------------
html_theme = "nvidia_sphinx_theme"
html_title = "Omniverse Performance"
html_short_title = "Omniverse Performance"

html_theme_options = {
    "collapse_navigation": False,
    "navigation_depth": 4,
    "show_toc_level": 2,
}

html_static_path = ["_static"]
html_css_files = ["custom.css"]

# -- Mermaid configuration -----------------------------------------------------
mermaid_d3_zoom = False
mermaid_init_js = """
mermaid.initialize({
    startOnLoad: true,
    flowchart: {
        useMaxWidth: false
    }
});
"""

# -- Copy button configuration -------------------------------------------------
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Link checking -------------------------------------------------------------
# This guide is mostly pointers out to Omniverse / OpenUSD documentation, and
# those URLs move. `sphinx-build -b linkcheck` (wired into CI) flags dead or
# redirected links so we catch them before a reader does.
#
# Anchor checking is disabled because most target pages are client-rendered
# (the in-page anchors are added by JavaScript, so a raw fetch can't see them);
# leaving it on produces noisy false negatives. We still validate that the page
# itself resolves.
linkcheck_anchors = False
linkcheck_timeout = 30
linkcheck_retries = 2
linkcheck_workers = 5
# Treat the common "moved permanently to the same place" redirects as OK.
linkcheck_allowed_redirects = {
    r"https://docs\.omniverse\.nvidia\.com/.*": r"https://docs\.omniverse\.nvidia\.com/.*",
    r"https://openusd\.org/.*": r"https://openusd\.org/.*",
    r"https://github\.com/.*": r"https://github\.com/.*",
}
# Known-flaky or auth-gated hosts can be added here to keep the report signal-rich.
linkcheck_ignore: list[str] = []
