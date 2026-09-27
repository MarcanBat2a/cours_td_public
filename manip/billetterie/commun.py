"""Petit socle HTTP partagé par le guichet et le catalogue (bibliothèque standard)."""
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")


def heure(ts: float) -> str:
    return datetime.fromtimestamp(ts, PARIS).strftime("%H:%M:%S")


class Gestionnaire(BaseHTTPRequestHandler):
    routes: dict = {}
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        print(f"{heure(datetime.now().timestamp())} {self.command} {self.path} {args[1] if len(args) > 1 else ''}")

    def _traiter(self):
        url = urlparse(self.path)
        self.requete = parse_qs(url.query)
        longueur = int(self.headers.get("Content-Length") or 0)
        brut = self.rfile.read(longueur) if longueur else b""
        try:
            self.corps = json.loads(brut) if brut else {}
        except json.JSONDecodeError:
            return self.repondre(400, {"erreur": "corps JSON illisible"})
        for (methode, prefixe), fonction in self.routes.items():
            if methode == self.command and (url.path == prefixe or url.path.startswith(prefixe + "/")):
                reste = url.path[len(prefixe):].strip("/")
                return fonction(self, reste)
        return self.repondre(404, {"erreur": f"route inconnue : {self.command} {url.path}"})

    do_GET = do_POST = do_PUT = _traiter

    def repondre(self, code: int, donnees) -> None:
        texte = json.dumps(donnees, ensure_ascii=False, indent=2) + "\n"
        brut = texte.encode()
        try:
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(brut)))
            self.end_headers()
            self.wfile.write(brut)
        except (BrokenPipeError, ConnectionResetError):
            # Le client a abandonné avant la réponse (timeout) : elle se perd.
            print("  (réponse perdue : le client ne l'attendait plus)")
            self.close_connection = True

    def abandonner(self) -> None:
        """Ne jamais répondre : la connexion se ferme sans un octet."""
        self.close_connection = True


def servir(routes: dict, port: int = 8000) -> None:
    Gestionnaire.routes = routes
    serveur = ThreadingHTTPServer(("0.0.0.0", port), Gestionnaire)
    serveur.daemon_threads = True
    print(f"Écoute sur le port {port}")
    serveur.serve_forever()
