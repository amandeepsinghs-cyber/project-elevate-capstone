#!/usr/bin/env python3
"""Local server for Project Elevate Quizzes that persists wrong answers to wrong_answers_bank.json.

Supports both direct http://127.0.0.1:8765 usage and CORS requests from file:// model_armor_quiz.html.
"""

from datetime import datetime
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json
import os

PORT = 8765
DIR = os.path.dirname(os.path.abspath(__file__))
BANK_FILE = os.path.join(DIR, "wrong_answers_bank.json")


def read_bank():
  if not os.path.exists(BANK_FILE):
    return {"updatedAt": None, "questions": []}
  try:
    with open(BANK_FILE, "r", encoding="utf-8") as f:
      data = json.load(f)
      if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
        return {"updatedAt": None, "questions": []}
      return data
  except Exception:
    return {"updatedAt": None, "questions": []}


def merge_and_write_bank(incoming_questions):
  """Merges incoming questions with existing disk bank so a wrong question is NEVER lost."""
  current = read_bank()
  by_key = {
      (q.get("topic", "Model Armor"), q["id"]): q
      for q in current.get("questions", [])
      if isinstance(q, dict) and "id" in q
  }
  for q in incoming_questions:
    if isinstance(q, dict) and "id" in q:
      by_key[(q.get("topic", "Model Armor"), q["id"])] = q
  merged_list = sorted(by_key.values(), key=lambda x: (str(x.get("topic", "")), x["id"]))
  payload = {
      "updatedAt": datetime.now().isoformat(timespec="seconds"),
      "questions": merged_list,
  }
  with open(BANK_FILE, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2, ensure_ascii=False)
  return payload


class QuizRequestHandler(SimpleHTTPRequestHandler):

  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=DIR, **kwargs)

  def _send_cors_headers(self):
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")

  def do_OPTIONS(self):
    self.send_response(204)
    self._send_cors_headers()
    self.end_headers()

  def do_GET(self):
    if self.path in ("/", ""):
      self.path = "/model_armor_quiz.html"
      return super().do_GET()
    if self.path == "/api/mistakes":
      data = read_bank()
      body = json.dumps(data, indent=2).encode("utf-8")
      self.send_response(200)
      self._send_cors_headers()
      self.send_header("Content-Type", "application/json")
      self.send_header("Cache-Control", "no-store")
      self.end_headers()
      self.wfile.write(body)
      return
    return super().do_GET()

  def do_POST(self):
    if self.path == "/api/mistakes":
      length = int(self.headers.get("Content-Length", "0"))
      raw = self.rfile.read(length).decode("utf-8") if length else "{}"
      data = json.loads(raw)
      questions_list = data.get("questions", [])
      saved = merge_and_write_bank(questions_list)
      body = json.dumps(saved, indent=2).encode("utf-8")
      self.send_response(200)
      self._send_cors_headers()
      self.send_header("Content-Type", "application/json")
      self.end_headers()
      self.wfile.write(body)
      return
    self.send_error(404, "Not found")

  def log_message(self, format, *args):
    pass


if __name__ == "__main__":
  server = HTTPServer(("127.0.0.1", PORT), QuizRequestHandler)
  print(f"Serving Project Elevate Quiz at http://127.0.0.1:{PORT}/model_armor_quiz.html")
  print(f"Wrong answers are saved permanently to: {BANK_FILE}")
  server.serve_forever()
