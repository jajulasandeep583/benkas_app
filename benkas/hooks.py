# Copyright (c) 2024, Benkas and Contributors
# License: GPL-3.0 — see LICENSE for details

app_name        = "benkas"
app_title       = "Benkas"
app_publisher   = "Benkas"
app_description = "Benkas — Configurable Progressive Web App on Frappe v16"
app_email       = "admin@benkas.com"
app_license     = "GNU General Public License (v3)"
app_version     = "1.0.0"

source_link  = "https://github.com/jajulasandeep583/benkas_app"
app_logo_url = "/assets/benkas/images/logo.svg"

# Only frappe is required — no ERPNext dependency (pure Frappe app)
required_apps = ["frappe"]

# ── v16: app home + apps-screen entry ─────────────────────────────────────────
# app_home tells Frappe where to send users when they click the app icon
app_home = "/benkas"

# add_to_apps_screen adds a tile on the Frappe v16 apps launcher grid
add_to_apps_screen = [
    {
        "name":           "benkas",
        "logo":           "/assets/benkas/images/logo.svg",
        "title":          "Benkas",
        "route":          "/benkas",
        "has_permission": "benkas.api.pwa.check_app_permission",
    }
]

# ── Website ────────────────────────────────────────────────────────────────────
# This is THE key hook:
#   www/benkas.html → yoursite.com/benkas  (Frappe serves it automatically)
#   The rule below makes ALL sub-paths like /benkas/home, /benkas/profile
#   also render from the same www/benkas.html — Vue Router handles sub-routing
website_route_rules = [
    {"from_route": "/benkas/<path:app_path>", "to_route": "benkas"},
]

# ── Boot injection (v16 pattern) ───────────────────────────────────────────────
# Injects mt_config into window.frappe.boot on every desk page load
extend_bootinfo = "benkas.api.pwa.extend_boot"

# ── Installation hooks ─────────────────────────────────────────────────────────
after_install  = "benkas.install.after_install"
before_migrate = "benkas.install.before_migrate"
after_migrate  = "benkas.install.after_migrate"

# ── Push notifications (Web Push) ─────────────────────────────────────────────
# New Workflow Action → push "Approval required" to everyone who can act;
# new Notification Log → mirror Frappe's in-app notification as a push.
doc_events = {
    "Workflow Action": {
        "after_insert": "benkas.api.push.notify_workflow_action",
    },
    "Notification Log": {
        "after_insert": "benkas.api.push.notify_notification_log",
    },
}

# ── Jinja ─────────────────────────────────────────────────────────────────────
jinja = {
    "methods": [
        "benkas.api.pwa.get_pwa_boot_context",
    ]
}
