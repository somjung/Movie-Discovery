"""Run the local development server: ``python -m web``.

Optional environment variables:
  PORT       listen port (default 5000)
  WEB_DEBUG  set to 1 to enable Flask debug/reload mode
"""

import os

from web import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1",
            port=int(os.environ.get("PORT", "5000")),
            debug=os.environ.get("WEB_DEBUG") == "1")
