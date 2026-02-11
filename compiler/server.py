"""
Development server — ``serve`` subcommand.

Serves a CTF challenge directory on a local port, applying compiler
directives on-the-fly for every request so you always see the latest
version without an explicit build step.
"""

from __future__ import annotations

import mimetypes
import posixpath
import urllib.parse
from functools import partial
from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn

from compiler.directives import apply_directive, detect_directive


class _ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle each request in a separate thread to avoid blocking."""

    daemon_threads = True


class _CompilerHandler(SimpleHTTPRequestHandler):
    """HTTP handler that applies directives before serving responses."""

    # Set by the factory wrapper
    source_root: Path

    def __init__(self, *args, source_root: Path, **kwargs):
        self.source_root = source_root
        super().__init__(*args, directory=str(source_root), **kwargs)

    # ------------------------------------------------------------------
    # Override send_head so we can intercept directive-bearing files.
    # ------------------------------------------------------------------
    def send_head(self):  # noqa: C901
        path = self._translate_path(self.path)

        if path is None:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        file_path = Path(path)

        # If the path is a directory, look for index.html inside it
        if file_path.is_dir():
            # Redirect to add trailing slash (matches nginx / Apache behaviour
            # and ensures relative links in directory listings resolve correctly)
            parsed = urllib.parse.urlparse(self.path)
            if not parsed.path.endswith("/"):
                new_url = parsed.path + "/"
                if parsed.query:
                    new_url += "?" + parsed.query
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                self.send_header("Location", new_url)
                self.end_headers()
                return None

            index = file_path / "index.html"
            if index.is_file():
                file_path = index
            else:
                # No index — fall back to built-in directory listing
                return super().send_head()

        if not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        # Check for a compiler directive
        directive = detect_directive(file_path)

        if directive == "no_include":
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None

        if directive is None:
            # No directive — serve normally via the base class
            return super().send_head()

        # Apply the directive
        try:
            rel = file_path.relative_to(self.source_root)
            url_prefix = "/" + rel.parent.as_posix()
            if not url_prefix.endswith("/"):
                url_prefix += "/"

            body = apply_directive(file_path, directive, url_prefix)
        except Exception as exc:
            self.send_error(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                f"Directive error: {exc}",
            )
            return None

        encoded = body.encode("utf-8")

        # Guess content type
        ctype, _ = mimetypes.guess_type(file_path.name)
        if ctype is None:
            ctype = "application/octet-stream"

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        self.wfile.write(encoded)
        return None  # we already wrote the body

    # ------------------------------------------------------------------
    # Swallow broken-pipe errors raised when the client disconnects
    # before we finish writing the response.
    # ------------------------------------------------------------------
    def handle_one_request(self):
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True

    # ------------------------------------------------------------------
    # Path translation helper (mirrors SimpleHTTPRequestHandler logic but
    # returns an absolute path rooted at source_root).
    # ------------------------------------------------------------------
    def _translate_path(self, path: str) -> str | None:
        # Strip query string / fragment
        path = urllib.parse.urlparse(path).path
        path = urllib.parse.unquote(path)
        # Normalise
        path = posixpath.normpath(path)

        parts = path.split("/")
        parts = [p for p in parts if p and p != ".."]

        result = self.source_root
        for part in parts:
            result = result / part

        # Security: make sure we haven't escaped the root
        try:
            result.resolve().relative_to(self.source_root.resolve())
        except ValueError:
            return None

        return str(result)

    # Quieter logging
    def log_message(self, fmt, *args):
        directive = ""
        # Quick peek to annotate the log
        try:
            translated = self._translate_path(self.path)
            if translated:
                d = detect_directive(Path(translated))
                if d:
                    directive = f"  [{d}]"
        except Exception:
            pass
        try:
            print(f"  {self.address_string()} {fmt % args}{directive}")
        except (BrokenPipeError, ConnectionResetError):
            pass


def serve(source: Path, port: int = 8000, bind: str = "0.0.0.0") -> None:
    """Start the dev server rooted at *source* on *bind*:*port*."""
    source = source.resolve()
    handler = partial(_CompilerHandler, source_root=source)

    httpd = _ThreadingHTTPServer((bind, port), handler)
    print(f"Serving {source} at http://{bind}:{port}  (Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        httpd.shutdown()
