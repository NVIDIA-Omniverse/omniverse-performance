# SPDX-FileCopyrightText: Copyright (c) 2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Makefile for Omniverse Performance documentation
#
# Build with: make docs-html
# Live preview: make docs-live

SPHINXOPTS    ?=
SPHINXBUILD   ?= uv run --group docs sphinx-build
SPHINXAUTOBLD ?= uv run --group docs sphinx-autobuild
SOURCEDIR     = .
BUILDDIR      = _build

.PHONY: help docs-html docs-live docs-clean docs-linkcheck

help:
	@echo "Available targets:"
	@echo "  docs-html      - Build HTML documentation"
	@echo "  docs-live      - Live-reload development server"
	@echo "  docs-clean     - Remove build artifacts"
	@echo "  docs-linkcheck - Check all external links"

docs-html:
	$(SPHINXBUILD) -b html $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html
	@echo ""
	@echo "Build finished. Open $(BUILDDIR)/html/index.html"

docs-live:
	$(SPHINXAUTOBLD) $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/html \
		--port 8000 \
		--open-browser

docs-clean:
	rm -rf $(BUILDDIR)

docs-linkcheck:
	$(SPHINXBUILD) -b linkcheck $(SPHINXOPTS) $(SOURCEDIR) $(BUILDDIR)/linkcheck
