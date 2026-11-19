#!/usr/bin/env python3
"""Unit tests for scripts/monitor.py hardening (no network)."""
import importlib.util, hashlib, pathlib, sys
spec = importlib.util.spec_from_file_location("monitor", pathlib.Path(__file__).with_name("monitor.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def expect(exc, fn):
    try: fn()
    except exc: return
    raise AssertionError("expected %s" % exc)

# 1 slug uniqueness for the 37 Venetian structure PDFs
urls = [f"https://www.venetianlasvegas.com/content/dam/vlvweb/casino/poker/deepstack/2026/structures/dse_nov_2026-structure_{i}.pdf" for i in range(1,38)]
assert len({m.slug(u) for u in urls}) == 37
assert len({m.slug(u) for u in ["https://x.com/booking?arrival_date=2026-11-18&departure_date=2026-11-22","https://x.com/booking?arrival_date=2026-11-18&departure_date=2026-11-25"]}) == 2
# 2 bot challenge rejected
expect(ValueError, lambda: m.validate_response("https://www.caesars.com/hotel", b"<html><head><title>Pardon Our Interruption</title></head></html>"))
# 3 PDF validation: challenge HTML for a .pdf URL rejected, real PDF accepted & hashed raw
expect(ValueError, lambda: m.validate_response("https://x/flyer.pdf", b"<html><title>Pardon Our Interruption</title></html>"))
d,kind,text = m.fingerprint("https://x/flyer.pdf", b"%PDF-1.7 binary\x00\xff")
assert kind=="pdf" and text is None and d==hashlib.sha256(b"%PDF-1.7 binary\x00\xff").hexdigest()
# 4 booking-widget date churn does not change fingerprint
a=b"<html><body><header>Select Dates Thu, Nov 19 Sun, Nov 22 arrival_date=2026-11-20&departure_date=2026-11-22</header><p>Resort fee $55</p><script>var x=1</script></body></html>"
b=b"<html><body><header>Select Dates Fri, Nov 20 Mon, Nov 23 arrival_date=2026-11-21&departure_date=2026-11-23</header><p>Resort fee $55</p><script>var x=2</script></body></html>"
assert m.fingerprint("https://x/resort-fee.html", a)[0]==m.fingerprint("https://x/resort-fee.html", b)[0]
# 5 visible text change does change fingerprint
c=a.replace(b"$55", b"$60")
assert m.fingerprint("https://x/resort-fee.html", a)[0]!=m.fingerprint("https://x/resort-fee.html", c)[0]
# 6 soft-404 rejected
expect(ValueError, lambda: m.validate_response("https://x/page", b"<html><head><title>Page Not Found</title></head></html>"))
print("test_monitor: all tests passed")
