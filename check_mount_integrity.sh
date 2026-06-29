#!/usr/bin/env bash
# Thin child-mount reality check.
# This is check-only. It does not modify files.

FAIL=0

printf '%s\n' 'Child Mount Reality-Check'

if [ -f README.md ]; then
  printf '%s\n' 'pass README.md exists'
else
  printf '%s\n' 'FAIL README.md missing'
  FAIL=1
fi

if [ -f AGENTS.md ]; then
  printf '%s\n' 'pass AGENTS.md exists'
else
  printf '%s\n' 'WARN AGENTS.md missing'
fi

if [ -f brain.manifest.yaml ]; then
  printf '%s\n' 'pass brain.manifest.yaml exists'
else
  printf '%s\n' 'WARN brain.manifest.yaml missing'
fi

if [ "$FAIL" -eq 0 ]; then
  printf '%s\n' 'complete'
  exit 0
else
  printf '%s\n' 'partial change required'
  exit 1
fi
