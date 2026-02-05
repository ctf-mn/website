#!/usr/bin/env bash
set -e

uv tool install invoke
uv sync --group local
npm install -g tailwindcss

echo "You are good to go! 🎉"
echo "You can run the following command to start the development server:"
echo "uvx invoke run"
