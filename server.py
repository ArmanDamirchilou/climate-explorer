"""Local-only web app; run with .venv/bin/python server.py."""

import argparse
import csv
import io
import json
import logging
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit

from climate import DataUnavailable, FIRST_YEAR, LAST_YEAR, PRESETS, ROOT, investigate


class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        super().end_headers()

    def respond(self, status, content, mime="application/json; charset=utf-8", filename=None):
        body = json.dumps(content, allow_nan=False).encode() if mime.startswith("application/json") else content.encode()
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlsplit(self.path)
        if parsed.path == "/api/config":
            return self.respond(200, {"presets": PRESETS, "first_year": FIRST_YEAR, "last_year": LAST_YEAR})
        reports = {"/api/validation": "results.json", "/api/dataset-check": "dataset-check.json", "/api/science-audit": "science-audit.json"}
        if parsed.path in reports:
            try:
                report = json.loads((ROOT / "evaluation" / reports[parsed.path]).read_text())
                return self.respond(200, report)
            except FileNotFoundError:
                return self.respond(404, {"error": "The saved evaluation is not available."})
            except (OSError, ValueError):
                logging.exception("Saved evaluation could not be read")
                return self.respond(500, {"error": "The saved evaluation could not be read. Restore it from the repository and restart the app."})
        if parsed.path in {"/api/climate", "/api/download"}:
            query = {key: values[0] for key, values in parse_qs(parsed.query).items()}
            try:
                result = investigate(query)
                if parsed.path == "/api/download":
                    buffer = io.StringIO()
                    writer = csv.writer(buffer)
                    # Tidy records preserve source and analysis metadata in every row.
                    writer.writerow(["year", "annual_value", "unit", "latitude", "longitude", "parameter", "aggregation", "source_url", "retrieved_utc"])
                    for row in result["annual"]:
                        writer.writerow([row["year"], row["value"], result["metadata"]["unit"], result["location"]["latitude"], result["location"]["longitude"], result["metadata"]["parameter"], result["metadata"]["aggregation"], result["provenance"]["request_url"], result["provenance"]["fetched_at"]])
                    return self.respond(200, buffer.getvalue(), "text/csv; charset=utf-8", "climate-explorer-annual.csv")
                return self.respond(200, result)
            except ValueError as error:
                return self.respond(400, {"error": str(error)})
            except DataUnavailable as error:
                return self.respond(502, {"error": str(error)})
            except Exception:
                logging.exception("Climate analysis failed")
                return self.respond(500, {"error": "Analysis could not finish. Please try again."})
        if parsed.path.startswith("/api/"):
            return self.respond(404, {"error": "Unknown endpoint."})
        return super().do_GET()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()
    handler = partial(Handler, directory=str(ROOT / "static"))
    server = ThreadingHTTPServer(("127.0.0.1", args.port), handler)
    print(f"Climate Explorer is running at http://127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
