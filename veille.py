import feedparser
import telegram
import time
import os
from datetime import datetime, timedelta

# 🔹 Configuration
TELEGRAM_BOT_TOKEN = "TON_BOT_TOKEN"
TELEGRAM_CHAT_ID = "TON_CHAT_ID"
HISTORY_FILE = "articles_envoyes.txt"  # Fichier pour stocker les articles envoyés

# 🔹 Liste des flux RSS
RSS_FEEDS = [
    "https://feeds.feedburner.com/securityweek",
    "https://krebsonsecurity.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://blogs.cisco.com/feed",
]

# 🔹 Initialiser le bot Telegram
bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)

# 🔹 Charger les articles déjà envoyés
def load_sent_articles():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        return set(line.strip() for line in file)

# 🔹 Sauvegarder les articles envoyés
def save_sent_articles(sent_articles):
    with open(HISTORY_FILE, "a", encoding="utf-8") as file:
        for article in sent_articles:
            file.write(article + "\n")

# 🔹 Récupérer les articles récents et vérifier s'ils sont déjà envoyés
def get_recent_articles():
    now = datetime.utcnow()
    sent_articles = load_sent_articles()
    new_articles = []
    
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries:
            article_id = entry.link  # Utiliser l'URL comme identifiant unique
            published_time = datetime(*entry.published_parsed[:6])  # Convertir en datetime
            
            if article_id not in sent_articles and now - published_time < timedelta(days=1):  # Articles des dernières 24h
                new_articles.append((entry.title, entry.link, article_id))
    
    return new_articles

# 🔹 Envoyer les articles sur Telegram
def send_articles():
    articles = get_recent_articles()
    if articles:
        sent_articles = []
        for title, link, article_id in articles:
            message = f"📰 *{title}*\n🔗 {link}"
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
            sent_articles.append(article_id)  # Ajouter à la liste des articles envoyés
        
        # Sauvegarder les articles envoyés
        save_sent_articles(sent_articles)
    else:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="📢 Aucune nouvelle importante aujourd'hui.")

# 🔹 Exécuter le script
if __name__ == "__main__":
    send_articles()
