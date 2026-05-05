import sqlite3
import os
import re
from rapidfuzz import fuzz

class Bot:

    def __init__(self, user_id):
        self.user_id = user_id
        self.conn = sqlite3.connect("data/bot.db", check_same_thread=False)
        self.cursor = self.conn.cursor()

    def clean_text(self, text: str) -> str:
        text = text.lower()

        # Türkçe karakter düzeltme
        replacements = {
            "ç": "c",
            "ğ": "g",
            "ı": "i",
            "ö": "o",
            "ş": "s",
            "ü": "u"
        }

        for k, v in replacements.items():
            text = text.replace(k, v)

        text = re.sub(r"[^\w\s]", "", text)
        return text

    def tokenize(self, text: str):
        return text.split()

    def get_reply(self, message: str):
        message = self.clean_text(message)
        words = self.tokenize(message)

        best_intent_id = None
        best_score = 0

        # 1. aliases tablosunu çek
        self.cursor.execute(
            "SELECT intent_id, text FROM aliases WHERE user_id = ?",
            (self.user_id,)
        )
        aliases = self.cursor.fetchall()

        for intent_id, alias in aliases:
            clean_alias = self.clean_text(alias)

            score = fuzz.partial_ratio(clean_alias, message)

            if score > best_score:
                best_score = score
                best_intent_id = intent_id

        # eşik
        if best_score > 60 and best_intent_id:
            # 2. responses çek
            self.cursor.execute(
                "SELECT text FROM responses WHERE intent_id = ? AND user_id = ?",
                (best_intent_id, self.user_id)
            )
            results = self.cursor.fetchall()

            responses = [r[0] for r in results]

            return {
                "text": " ".join(responses),
                "confidence": best_score
            }
        return None