#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Compatibility Tool
Ensures emoji and Chinese characters display correctly in the Windows console.
"""
import sys


def setup_console_encoding():
    """Configure console for UTF-8 encoding (Windows-specific) and enable real-time output."""
    if sys.platform == 'win32':
        try:
            import io
            # Force line buffering and immediate writing to prevent output delays.
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout = io.TextIOWrapper(
                    sys.stdout.buffer, encoding='utf-8',
                    line_buffering=True, write_through=True
                )
            if hasattr(sys.stderr, 'buffer'):
                sys.stderr = io.TextIOWrapper(
                    sys.stderr.buffer, encoding='utf-8',
                    line_buffering=True, write_through=True
                )
        except Exception:
            # If configuration fails, do not disrupt program execution.
            pass


def safe_print(*args, **kwargs):
    """
    A safe print function that automatically flushes to avoid Windows buffer issues.
    """
    print(*args, **kwargs)
    if sys.platform == 'win32':
        try:
            sys.stdout.flush()
            sys.stderr.flush()
        except Exception:
            pass


# Automatic setup (executed on import).
setup_console_encoding()
