# Copyright (c) 2026, Benkas and Contributors
# License: GPL-3.0
"""
Git-tracked setup for the PWA's native-looking portal Web Pages.

Run with:
    bench --site <site> execute benkas.setup.web_pages.create_pages

Two site-info pages rendered full-screen inside the Benkas PWA:
  /benkas-about    — what this system is (the Ramshy Bio plant project)
  /benkas-notices  — standing site notices (gate, PPE, EOD reminders)

Each is content_type=HTML, full_width, title hidden, and injects CSS that hides
the Frappe website navbar/footer so it feels native inside the app iframe.
"""

import frappe

# ── Shared chrome: hides website navbar/footer + sets the app's base look ──────
_BASE_CSS = """
<style>
  :root { --bk-primary:#6366f1; --bk-ink:#1e293b; --bk-sub:#64748b; --bk-bg:#f8fafc; }
  .navbar, .web-footer, footer, .footer, #navbar-collapse,
  .page-head, .breadcrumb-container, .navbar-fixed-top { display:none !important; }
  body, html { margin:0 !important; padding:0 !important; background:var(--bk-bg) !important; }
  .main-section, .page_content, .container, [id^='page-'] {
    padding:0 !important; margin:0 !important; max-width:100% !important;
  }
  * { box-sizing:border-box; }
  .bk-page {
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,sans-serif;
    color:var(--bk-ink); -webkit-font-smoothing:antialiased;
  }
</style>
"""


def _about_html() -> str:
    return _BASE_CSS + """
<div class="bk-page">
  <style>
    .bk-hero { background:linear-gradient(135deg,#16324f 0%,#1f4e79 60%,#6366f1 100%);
      color:#fff; padding:46px 22px 40px; text-align:center; position:relative; overflow:hidden; }
    .bk-hero::after{content:"";position:absolute;inset:0;
      background:radial-gradient(circle at 20% 0%,rgba(255,255,255,.18),transparent 45%);}
    .bk-wordmark{font-size:30px;font-weight:900;letter-spacing:-.5px;position:relative;}
    .bk-wordmark .a{opacity:.85;}
    .bk-tag{margin-top:8px;font-size:14px;opacity:.92;font-weight:500;position:relative;}
    .bk-stats{display:flex;gap:12px;justify-content:center;flex-wrap:wrap;
      margin:-26px 16px 0;position:relative;z-index:2;}
    .bk-stat{background:#fff;border:1px solid #eef2f7;border-radius:18px;
      padding:16px 20px;min-width:96px;text-align:center;box-shadow:0 6px 20px rgba(15,23,42,.06);}
    .bk-stat b{display:block;font-size:24px;font-weight:900;color:var(--bk-primary);letter-spacing:-1px;}
    .bk-stat span{font-size:11.5px;color:var(--bk-sub);font-weight:600;text-transform:uppercase;letter-spacing:.4px;}
    .bk-sec{padding:28px 18px 4px;}
    .bk-sec-title{font-size:13px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;
      color:#94a3b8;margin-bottom:14px;}
    .bk-cards{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
    .bk-card{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:16px;
      box-shadow:0 1px 10px rgba(15,23,42,.03);}
    .bk-ico{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;
      justify-content:center;font-size:21px;margin-bottom:10px;}
    .bk-card h3{margin:0 0 4px;font-size:14.5px;font-weight:800;}
    .bk-card p{margin:0;font-size:12.5px;color:var(--bk-sub);line-height:1.5;}
    .bk-body{padding:8px 20px 40px;font-size:14px;line-height:1.7;color:#475569;}
  </style>

  <div class="bk-hero">
    <div class="bk-wordmark">Ben<span class="a">kas</span> ERP</div>
    <div class="bk-tag">Ramshy Bio Pvt. Ltd. — Ethanol Plant Construction Monitoring</div>
  </div>

  <div class="bk-stats">
    <div class="bk-stat"><b>12</b><span>Sections</span></div>
    <div class="bk-stat"><b>1</b><span>Gate</span></div>
    <div class="bk-stat"><b>EOD</b><span>Daily Log</span></div>
  </div>

  <div class="bk-sec">
    <div class="bk-sec-title">What this app does</div>
    <div class="bk-cards">
      <div class="bk-card">
        <div class="bk-ico" style="background:#e7eefc;color:#2456c0;">🚪</div>
        <h3>Gate &amp; Attendance</h3>
        <p>Scan every person in and out; attendance and manpower are counted automatically.</p>
      </div>
      <div class="bk-card">
        <div class="bk-ico" style="background:#eef2ff;color:#6366f1;">📋</div>
        <h3>Daily Progress (EOD)</h3>
        <p>File the day's log per section — task %, workers, material and photos.</p>
      </div>
      <div class="bk-card">
        <div class="bk-ico" style="background:#fff7ed;color:#f59e0b;">📦</div>
        <h3>Material &amp; Quality</h3>
        <p>Requests, weighbridge GRNs with invoice proof, quality checks and stock.</p>
      </div>
      <div class="bk-card">
        <div class="bk-ico" style="background:#fdeaea;color:#c0271e;">🦺</div>
        <h3>Safety &amp; Assets</h3>
        <p>Permits, violations, generators and power — all logged with photos.</p>
      </div>
    </div>
  </div>

  <div class="bk-body">
    Benkas ERP keeps the plant build honest and in one place — who was on site, what each
    section achieved, what material was used and how safety is tracked. Managed by
    <b>Benkas Engineering — Project Monitoring Cell</b>. This page is editable from the desk under
    <b>Web Page → About This Project</b>.
  </div>
</div>
"""


def _notices_html() -> str:
    return _BASE_CSS + """
<div class="bk-page">
  <style>
    .nt-head{padding:26px 18px 6px;}
    .nt-head h1{margin:0;font-size:24px;font-weight:900;letter-spacing:-.5px;color:#0f172a;}
    .nt-head p{margin:4px 0 0;font-size:13px;color:var(--bk-sub);}
    .nt-list{padding:14px 16px 40px;display:flex;flex-direction:column;gap:12px;}
    .nt-item{background:#fff;border:1px solid #e2e8f0;border-radius:18px;padding:16px;
      box-shadow:0 1px 10px rgba(15,23,42,.03);position:relative;}
    .nt-item.pin{border-color:rgba(99,102,241,.4);}
    .nt-top{display:flex;align-items:center;gap:8px;margin-bottom:8px;}
    .nt-badge{font-size:10.5px;font-weight:800;text-transform:uppercase;letter-spacing:.4px;
      padding:3px 9px;border-radius:999px;}
    .b-safety{background:#fee2e2;color:#dc2626;} .b-gate{background:#e7eefc;color:#2456c0;}
    .b-eod{background:#eef2ff;color:#6366f1;} .b-it{background:#ecfeff;color:#0891b2;}
    .nt-date{margin-left:auto;font-size:11.5px;color:#94a3b8;font-weight:600;}
    .nt-pinflag{font-size:11px;font-weight:800;color:#6366f1;}
    .nt-item h3{margin:0 0 4px;font-size:15px;font-weight:800;color:#1e293b;}
    .nt-item p{margin:0;font-size:13px;color:#475569;line-height:1.55;}
  </style>

  <div class="nt-head">
    <h1>📣 Site Notices</h1>
    <p>Standing instructions for everyone on site</p>
  </div>

  <div class="nt-list">
    <div class="nt-item pin">
      <div class="nt-top">
        <span class="nt-pinflag">📌 Pinned</span>
        <span class="nt-badge b-safety">Safety</span>
      </div>
      <h3>PPE is mandatory inside the plant</h3>
      <p>Helmet and safety shoes at all times; harness for work at height. Violations are logged
         with a photo — repeat breaches are reported to your contractor.</p>
    </div>

    <div class="nt-item">
      <div class="nt-top">
        <span class="nt-badge b-gate">Gate</span>
      </div>
      <h3>Scan in and out — every time</h3>
      <p>Show your ID card at the Scan Station on entry (with a photo) and on exit. Only scanned
         people count as present for the day.</p>
    </div>

    <div class="nt-item">
      <div class="nt-top">
        <span class="nt-badge b-eod">EOD</span>
      </div>
      <h3>Section Incharges: file the Daily EOD every evening</h3>
      <p>Open Daily EOD, pick each task you touched, set the status, type what happened, adjust the
         %, add photos and submit. It takes two minutes on your phone.</p>
    </div>

    <div class="nt-item">
      <div class="nt-top">
        <span class="nt-badge b-it">App</span>
      </div>
      <h3>Install the app on your phone</h3>
      <p>Open the site in your browser and choose "Add to Home screen" to install Benkas ERP as an
         app with notifications.</p>
    </div>
  </div>
</div>
"""


# ── Page definitions ───────────────────────────────────────────────────────────
PAGES = [
    {
        "route": "benkas-about",
        "title": "About This Project",
        "html": _about_html,
        "module": {"label": "About Project", "icon": "info", "color": "#16324f", "order": 20},
    },
    {
        "route": "benkas-notices",
        "title": "Site Notices",
        "html": _notices_html,
        "module": {"label": "Site Notices", "icon": "bell", "color": "#ec4899", "order": 21},
    },
]

# Old midhunatech-era routes/tiles to clean up on update.
_RETIRED_ROUTES = ["mt-about", "mt-notices"]
_RETIRED_MODULE_KEYS = ["mt_about", "mt_notices"]


def create_pages():
    """Create/update the site-info Web Pages and link them into the PWA config
    as iframe modules. Also retires the old midhunatech-era About/Notices pages."""
    # retire old pages + tiles
    for route in _RETIRED_ROUTES:
        old = frappe.db.get_value("Web Page", {"route": route}, "name")
        if old:
            frappe.delete_doc("Web Page", old, ignore_permissions=True, force=True)
    cfg = frappe.get_doc("Benkas PWA Config")
    cfg.set("modules", [m for m in cfg.get("modules", []) if m.module_name not in _RETIRED_MODULE_KEYS])
    cfg.save(ignore_permissions=True)

    for p in PAGES:
        name = frappe.db.get_value("Web Page", {"route": p["route"]}, "name")
        doc = frappe.get_doc("Web Page", name) if name else frappe.new_doc("Web Page")
        doc.update({
            "title": p["title"],
            "route": p["route"],
            "published": 1,
            "content_type": "HTML",
            "full_width": 1,
            "show_title": 0,
            "show_sidebar": 0,
            "main_section_html": p["html"](),
        })
        doc.save(ignore_permissions=True)
        print(f"  ✔ Web Page  /{p['route']}  ->  {doc.name}")

    _link_modules()
    frappe.db.commit()
    print("Done. Visit /benkas-about and /benkas-notices, or open the PWA home grid.")


def _link_modules():
    """Add the pages as iframe_url modules in Benkas PWA Config (idempotent)."""
    cfg = frappe.get_doc("Benkas PWA Config")
    existing = {row.module_name for row in cfg.get("modules", [])}
    for p in PAGES:
        key = p["route"].replace("-", "_")
        if key in existing:
            continue
        m = p["module"]
        cfg.append("modules", {
            "module_name": key,
            "label": m["label"],
            "icon": m["icon"],
            "color": m["color"],
            "route_path": f"/{p['route']}",
            "module_type": "iframe_url",
            "target_url": f"/{p['route']}",
            "display_order": m["order"],
            "is_enabled": 1,
        })
        print(f"  ✔ Module    {m['label']}  ->  iframe /{p['route']}")
    cfg.save(ignore_permissions=True)
