import json
import os
import re

BOT_NAME = "ShopBot"
FAQ_FILE = "faq.json"

# ---------------------------------------------------------------
# Default intents (used when faq.json is missing or invalid)
# Each intent: name, regex patterns, response
# ---------------------------------------------------------------
DEFAULT_INTENTS = [
    {
        "name": "greeting",
        "patterns": [r"\b(hi|hello|hey|namaste|good (morning|afternoon|evening))\b"],
        "response": "Hello! Main {bot} hoon. Aap business hours, products, shipping ya returns ke baare me pooch sakte hain.",
    },
    {
        "name": "hours",
        "patterns": [r"\b(hours?|timings?|time|open|close|closing|opening|schedule)\b"],
        "response": "Hum Monday-Saturday, 9:00 AM se 8:00 PM tak open rehte hain. Sunday ko band.",
    },
    {
        "name": "returns",
        "patterns": [r"\b(return|returns|refund|exchange|replace(ment)?|money back)\b"],
        "response": "Return policy: delivery ke 7 din ke andar unused product return kar sakte hain. Refund 5-7 working days me aata hai.",
    },
    {
        "name": "shipping",
        "patterns": [r"\b(ship(ping)?|deliver(y|ed)?|courier|track(ing)?|dispatch)\b"],
        "response": "Delivery 3-5 working days me hoti hai. Rs. 499 se upar ke orders par free shipping milti hai.",
    },
    {
        "name": "payment",
        "patterns": [r"\b(pay(ment)?|upi|card|cod|cash on delivery|net ?banking)\b"],
        "response": "Hum UPI, credit/debit card, net banking aur Cash on Delivery accept karte hain.",
    },
    {
        "name": "products",
        "patterns": [r"\b(products?|items?|catalog(ue)?|sell|available|laptops?|phones?|headphones?)\b"],
        "response": "Hamare paas electronics (phones, laptops, headphones) aur accessories available hain. Website par full catalogue dekh sakte hain.",
    },
    {
        "name": "price",
        "patterns": [r"\b(price|prices|cost|costs|discount|offers?|sale|cheap)\b"],
        "response": "Prices product ke hisaab se alag hoti hain. Abhi selected items par 10-20% discount chal raha hai.",
    },
    {
        "name": "contact",
        "patterns": [r"\b(contact|phone number|call|email|support|help ?desk|customer care|address)\b"],
        "response": "Support: support@shopeasy.example | Phone: 1800-123-4567 (9 AM - 8 PM).",
    },
    {
        "name": "thanks",
        "patterns": [r"\b(thanks?|thank you|thx|shukriya|dhanyavaad)\b"],
        "response": "Aapka swagat hai! Aur kuch madad chahiye to poochiye.",
    },
]

EXIT_PATTERN = re.compile(r"\b(bye|goodbye|exit|quit)\b")
NAME_PATTERN = re.compile(r"\b(?:my name is|i am|i'm|mera naam)\s+([a-z]+)")

FALLBACK_REPLIES = [
    "Sorry, mujhe ye samajh nahi aaya. Kya aap dobara alag tarike se bata sakte hain?",
    "Hmm, is baare me meri pass jaankari nahi hai. Aap hours, products, shipping, returns ya payment ke baare me pooch sakte hain.",
]


def load_intents(path=FAQ_FILE):
    """Load intents from JSON; fall back to defaults on any problem."""
    if not os.path.exists(path):
        return DEFAULT_INTENTS
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        intents = data["intents"] if isinstance(data, dict) else data
        valid = []
        for item in intents:
            if "name" in item and "patterns" in item and "response" in item:
                valid.append(item)
        if not valid:
            raise ValueError("no valid intents found")
        print(f"[info] {len(valid)} intents loaded from {path}")
        return valid
    except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as e:
        print(f"[warning] {path} load nahi ho paayi ({e}). Default intents use ho rahe hain.")
        return DEFAULT_INTENTS


def compile_intents(intents):
    """Pre-compile regex patterns for speed; skip bad regexes safely."""
    compiled = []
    for item in intents:
        regexes = []
        for p in item["patterns"]:
            try:
                regexes.append(re.compile(p, re.IGNORECASE))
            except re.error:
                print(f"[warning] Invalid regex skipped in '{item['name']}': {p}")
        if regexes:
            compiled.append((item["name"], regexes, item["response"]))
    return compiled


def normalize(text):
    """Lowercase, strip, collapse spaces, remove stray punctuation."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s'@.]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def find_intents(text, compiled):
    """Return list of (intent_name, response) for ALL intents matched (multi-intent)."""
    matches = []
    for name, regexes, response in compiled:
        if any(r.search(text) for r in regexes):
            matches.append((name, response))
    return matches


class ChatBot:
    def __init__(self):
        self.state = "CHATTING"
        self.compiled = compile_intents(load_intents())
        self.state = "START"          # START -> CHATTING -> EXIT
        self.user_name = None
        self.last_intent = None
        self.fallback_count = 0

    def respond(self, raw):
        text = normalize(raw)

        # Empty input
        if not text:
            return "Kuch type kijiye, main sun raha hoon. :)"

        # Exit commands
        if EXIT_PATTERN.search(text):
            self.state = "EXIT"
            who = f" {self.user_name.title()}" if self.user_name else ""
            return f"Bye{who}! Aapka din shubh ho."

        # Capture user's name (conversation memory)
        m = NAME_PATTERN.search(text)
        if m:
            self.user_name = m.group(1)
            return f"Nice to meet you, {self.user_name.title()}! Main aapki kya madad kar sakta hoon?"

        matches = find_intents(text, self.compiled)

        # Greeting only when it is the sole intent (otherwise answer the real question)
        if len(matches) > 1:
            matches = [x for x in matches if x[0] not in ("greeting", "thanks")] or matches

        if matches:
            self.state = "CHATTING"
            self.fallback_count = 0
            self.last_intent = matches[-1][0]
            parts = [resp.format(bot=BOT_NAME) for _, resp in matches]
            return "\n".join(f"- {p}" for p in parts) if len(parts) > 1 else parts[0]

        # Context follow-up: "and?", "more", "details"
        if self.last_intent and re.search(r"\b(more|details?|and|also|aur)\b", text):
            return "Aur detail ke liye support@shopeasy.example par likhiye ya naya sawaal poochiye."

        # Fallback
        reply = FALLBACK_REPLIES[min(self.fallback_count, len(FALLBACK_REPLIES) - 1)]
        self.fallback_count += 1
        return reply


def main():
    bot = ChatBot()
    print("=" * 55)
    print(f"  {BOT_NAME} - ShopEasy Customer Support")
    print("  'bye', 'exit' ya 'quit' likh kar band karein")
    print("=" * 55)
    print(f"{BOT_NAME}: Namaste! Main {BOT_NAME} hoon. Aapki kya madad kar sakta hoon?")

    while bot.state != "EXIT":
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print(f"\n{BOT_NAME}: Chat band ho gayi. Bye!")
            break
        except Exception as e:  # unexpected input error
            print(f"{BOT_NAME}: Kuch error aa gaya ({e}). Dobara try karein.")
            continue

        try:
            print(f"{BOT_NAME}: {bot.respond(user_input)}")
        except Exception as e:
            print(f"{BOT_NAME}: Internal error: {e}. Dobara try karein.")


if __name__ == "__main__":
    main()