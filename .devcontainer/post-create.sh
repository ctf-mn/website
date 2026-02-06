#!/usr/bin/env bash
set -e

uv tool install invoke
uv tool install ruff

uv sync --group local
npm install

echo "You are good to go! 🎉"
echo "You can run the following command to start the development server:"
echo "uvx invoke run"
