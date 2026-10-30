
import argparse
import queue
import threading
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64; rv:19.0) "
    "Gecko/20100101 Firefox/19.0"
)

EXTENSIONS = [".php", ".bak", ".orig", ".inc"]
THREADS = 10
TIMEOUT = 5

# Only run against a local lab by default.
TARGET = "http://127.0.0.1/"
WORDLIST = str(Path.home() / "Downloads" / "all.txt")


def extend_words(word, words):
    word = word.strip().lstrip("/")

    if not word:
        return

    if "." in word:
        words.put(word)
    else:
        words.put(word + "/")

    for extension in EXTENSIONS:
        words.put(word + extension)


def get_words(wordlist, resume=None):
    words = queue.Queue()
    found_resume = resume is None

    with open(wordlist, encoding="utf-8") as file:
        for line in file:
            word = line.strip()

            if not word:
                continue

            if not found_resume:
                if word == resume:
                    found_resume = True
                    print(f"Resuming after: {resume}")
                continue

            extend_words(word, words)

    if not found_resume:
        raise ValueError(f"Resume word not found: {resume}")

    return words


def dir_bruter(words, target, stats, lock):
    headers = {"User-Agent": AGENT}

    with requests.Session() as session:
        session.headers.update(headers)

        while True:
            try:
                path = words.get_nowait()
            except queue.Empty:
                break

            try:
                url = urljoin(target.rstrip("/") + "/", path)
                response = session.get(
                    url,
                    timeout=TIMEOUT,
                    allow_redirects=False,
                )

                with lock:
                    stats["checked"] += 1

                    if response.status_code != 404:
                        print(
                            f"[{response.status_code}] {url}"
                        )
                        stats["reported"] += 1

                response.close()

            except requests.RequestException as error:
                with lock:
                    stats["errors"] += 1
                print(f"Request failed: {error}", file=sys.stderr)

            finally:
                words.task_done()


def main():
    parser = argparse.ArgumentParser(
        description="Directory discovery for an authorized local lab."
    )
    parser.add_argument("--target", default=TARGET)
    parser.add_argument("--wordlist", default=WORDLIST)
    parser.add_argument("--resume", default=None)
    parser.add_argument("--threads", type=int, default=THREADS)
    args = parser.parse_args()

    parsed = urlparse(args.target)

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        parser.error("Target must be a valid HTTP or HTTPS URL.")

    if parsed.hostname not in ("127.0.0.1", "localhost", "::1"):
        parser.error(
            "This learning version is restricted to localhost."
        )

    if not 1 <= args.threads <= 20:
        parser.error("Threads must be between 1 and 20.")

    if not Path(args.wordlist).is_file():
        parser.error(f"Wordlist not found: {args.wordlist}")

    words = get_words(args.wordlist, args.resume)
    total = words.qsize()

    print(f"Queued {total} paths.")
    print(f"Target: {args.target}")
    input("Press Enter to start the local lab scan...")

    stats = {"checked": 0, "reported": 0, "errors": 0}
    lock = threading.Lock()
    workers = []

    for _ in range(args.threads):
        worker = threading.Thread(
            target=dir_bruter,
            args=(words, args.target, stats, lock),
        )
        worker.start()
        workers.append(worker)

    for worker in workers:
        worker.join()

    print("\nScan complete.")
    print(f"Requests checked: {stats['checked']}")
    print(f"Non-404 responses: {stats['reported']}")
    print(f"Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
