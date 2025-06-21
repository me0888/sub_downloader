import os
import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, CouldNotRetrieveTranscript
import time

def fetch_proxies():
    url = "https://free-proxy-list.net/"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    proxies = []
    for row in soup.select("table#proxylisttable tbody tr"):
        tds = row.find_all("td")
        if tds[6].text.strip() == "yes":  # HTTPS support
            proxies.append(f"http://{tds[0].text.strip()}:{tds[1].text.strip()}")
    return proxies

def is_proxy_working(proxy):
    try:
        r = requests.get("https://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
        return r.status_code == 200
    except:
        return False

def get_working_proxies():
    proxies = fetch_proxies()
    working = []
    for proxy in proxies:
        if is_proxy_working(proxy):
            print(f"[✓] Working proxy found: {proxy}")
            working.append(proxy)
            if len(working) >= 5:  # Ограничим список до 5 для ротации
                break
    if not working:
        print("[!] No working proxies found")
    return working

def fetch_subtitles_with_proxy(video_id, proxy):
    try:
        proxies = {
            "http": proxy,
            "https": proxy,
        }
        session = requests.Session()
        session.proxies.update(proxies)
        # YouTubeTranscriptApi не поддерживает напрямую сессии, поэтому придется вручную переопределять request:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except (TranscriptsDisabled, NoTranscriptFound) as e:
        raise e
    except Exception as e:
        print(f"[!] Proxy {proxy} failed: {e}")
        return None

def fetch_subtitles_with_scraperapi(video_id, api_key):
    # Используем ScraperAPI для проксирования
    url = f"http://api.scraperapi.com/?api_key={api_key}&url=https://www.youtube.com/watch?v={video_id}"
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"[!] ScraperAPI request failed with code {r.status_code}")
            return None
        # Теперь можно пробовать получить субтитры через обычный метод, но используя cookies или session ScraperAPI — упрощенно:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return transcript
    except Exception as e:
        print(f"[!] ScraperAPI fetch failed: {e}")
        return None

def get_subtitles(video_id):
    working_proxies = get_working_proxies()
    for proxy in working_proxies:
        subs = fetch_subtitles_with_proxy(video_id, proxy)
        if subs:
            print(f"[✓] Subtitles fetched using proxy {proxy}")
            return subs
        time.sleep(1)  # Не спамить слишком быстро
    
    # Если прокси не сработали, используем ScraperAPI
    scraper_api_key = os.getenv("SCRAPER_API_KEY")
    if scraper_api_key:
        subs = fetch_subtitles_with_scraperapi(video_id, scraper_api_key)
        if subs:
            print("[✓] Subtitles fetched using ScraperAPI")
            return subs
    else:
        print("[!] SCRAPER_API_KEY env var not set")
    
    raise Exception("Failed to fetch subtitles with proxies and ScraperAPI")

if __name__ == "__main__":
    video_id = "5GJI5VoGizQ"
    try:
        subtitles = get_subtitles(video_id)
        for entry in subtitles:
            print(f"{entry['start']:.2f}s: {entry['text']}")
    except Exception as e:
        print(f"[!] Error: {e}")
