#!/usr/bin/env python3
"""Phase 2 fixed — fingerprint + bot score validation."""

import asyncio, json, sys
sys.path.insert(0, "/home/zen/slice")
from slice import StealthBrowser, generate_profile

async def main():
    profile = generate_profile(os="windows")
    sb = await StealthBrowser.launch(profile=profile)
    
    # === NowSecure ===
    print("=" * 60)
    print("  NOWSECURE")
    print("=" * 60)
    p1 = await sb.new_page("https://nowsecure.nl")
    await asyncio.sleep(5)
    body = await p1.evaluate("document.body.innerText")
    passed = "passed" in body.lower()
    print(f"  Body: {body[:300]}")
    print(f"  Verdict: {'✓ PASSED' if passed else '✗ UNCLEAR'}")
    png = await p1.screenshot()
    with open("/tmp/nowsecure_result.png", "wb") as f: f.write(png)
    await p1.close()
    
    # === Bot score ===
    print("\n" + "=" * 60)
    print("  BOT.INCOLUMITAS.COM")
    print("=" * 60)
    p2 = await sb.new_page("https://bot.incolumitas.com")
    await asyncio.sleep(6)
    body2 = await p2.evaluate("document.body.innerText")
    for line in body2.split("\n"):
        l = line.strip()
        if l and any(w in l.lower() for w in ["score", "0.", "bot"]):
            print(f"  > {l[:120]}")
    png2 = await p2.screenshot()
    with open("/tmp/bot_score.png", "wb") as f: f.write(png2)
    await p2.close()
    
    # === Fingerprint consistency on BrowserLeaks ===
    print("\n" + "=" * 60)
    print("  BROWSERLEAKS — FINGERPRINT CHECK")
    print("=" * 60)
    p3 = await sb.new_page("https://browserleaks.com/canvas")
    await asyncio.sleep(4)
    
    checks = {
        "navigator.webdriver": "navigator.webdriver",
        "plugins.length": "navigator.plugins.length",
        "languages": "JSON.stringify(navigator.languages)",
        "platform": "navigator.platform",
        "userAgent": "navigator.userAgent",
        "hardwareConcurrency": "navigator.hardwareConcurrency",
        "deviceMemory": "navigator.deviceMemory",
        "screen.width": "screen.width",
        "screen.height": "screen.height",
        "colorDepth": "screen.colorDepth",
        "timezone": "Intl.DateTimeFormat().resolvedOptions().timeZone",
    }
    
    for label, js in checks.items():
        try:
            val = await p3.evaluate(js)
            print(f"  {label:25s} = {str(val)[:80]}")
        except Exception as e:
            print(f"  {label:25s} = ERROR: {e}")
    
    webdriver_val = await p3.evaluate("navigator.webdriver")
    wd_ok = webdriver_val is None or webdriver_val == False
    print(f"\n  webdriver hidden: {'✓ YES' if wd_ok else '✗ NO — DETECTED!'}")
    
    png3 = await p3.screenshot()
    with open("/tmp/browserleaks_result.png", "wb") as f: f.write(png3)
    await p3.close()
    
    # === Rapid-fire test — 5 pages back-to-back ===
    print("\n" + "=" * 60)
    print("  RAPID-FIRE — 5 pages in sequence")
    print("=" * 60)
    rapid_targets = [
        ("GitHub", "https://github.com"),
        ("HN", "https://news.ycombinator.com"),
        ("Reddit", "https://old.reddit.com"),
        ("Amazon", "https://www.amazon.com"),
        ("Wikipedia", "https://en.wikipedia.org"),
    ]
    for name, url in rapid_targets:
        t0 = asyncio.get_event_loop().time()
        p = await sb.new_page(url)
        await asyncio.sleep(2)
        title = await p.evaluate("document.title")
        dt = round(asyncio.get_event_loop().time() - t0, 2)
        print(f"  ✓ {name:12s} | {dt}s | {title[:50]}")
        await p.close()
    
    await sb.close()
    print("\n  All done. Screenshots in /tmp/")

asyncio.run(main())
