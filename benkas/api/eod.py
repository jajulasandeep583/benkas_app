# Copyright (c) 2026, Benkas and Contributors — GPL-3.0
"""Mobile EOD (End-of-Day) — file a Daily Progress Log from the phone.

Thin wrapper over benkas_erp's Daily Progress Log: this app only gathers the
inputs; ALL validation + rollups happen server-side in benkas_erp's doc_events
(validate / on_submit), so the phone gets identical behaviour to the desk.

Requires benkas_erp to be installed on the site (guarded).
"""

import base64
import json

import frappe
from frappe import _


def _available():
    return bool(frappe.db.exists("DocType", "Daily Progress Log")) \
        and bool(frappe.db.exists("DocType", "Progress Status"))


@frappe.whitelist()
def get_eod_meta():
    """Sections (each with its tasks) + the status options for the dropdowns."""
    if not _available():
        return {"available": False}

    sections = []
    for s in frappe.get_all("Plant Section", filters={"is_active": 1},
                            fields=["name", "section_name", "project_task"],
                            order_by="section_code asc"):
        tasks = frappe.get_all("Task", filters={"parent_task": s.project_task},
                               fields=["name", "subject", "progress"],
                               order_by="subject asc") if s.project_task else []
        sections.append({
            "name": s.name, "label": s.section_name or s.name,
            "tasks": [{"name": t.name, "subject": t.subject,
                       "progress": t.progress or 0} for t in tasks],
        })

    statuses = [
        {"name": r.name, "is_stopped": int(r.is_stopped or 0), "color": r.color or "Grey"}
        for r in frappe.get_all("Progress Status",
                                fields=["name", "is_stopped", "color"],
                                order_by="display_order asc, name asc")
    ]
    return {"available": True, "sections": sections, "statuses": statuses,
            "today": frappe.utils.today()}


def _save_photo(data_uri):
    """base64 data URI -> a File; returns its URL (or None)."""
    if not data_uri or "," not in data_uri:
        return None
    header, b64 = data_uri.split(",", 1)
    ext = "png" if "image/png" in header else "jpg"
    fname = f"eod-{frappe.generate_hash(length=8)}.{ext}"
    f = frappe.get_doc({
        "doctype": "File", "file_name": fname, "is_private": 0,
        "content": b64, "decode": True,
    }).insert(ignore_permissions=True)
    return f.file_url


@frappe.whitelist()
def submit_eod(payload):
    """Build + submit a Daily Progress Log. Perms + validation are enforced by
    Frappe / benkas_erp exactly as on the desk (no ignore_permissions on the log)."""
    if not _available():
        frappe.throw(_("The daily log is not available on this site."))

    data = json.loads(payload) if isinstance(payload, str) else payload

    doc = frappe.new_doc("Daily Progress Log")
    doc.plant_section = data.get("section")
    doc.log_date = data.get("log_date") or frappe.utils.today()

    if data.get("no_work_today"):
        doc.no_work_today = 1
        doc.no_work_reason = (data.get("no_work_reason") or "").strip()
    else:
        for r in (data.get("task_rows") or []):
            if not r.get("task"):
                continue
            doc.append("task_progress", {
                "task": r.get("task"),
                "status": r.get("status"),
                "percent_complete": r.get("percent_complete"),
                "work_description": (r.get("work_description") or "").strip(),
            })
        for p in (data.get("photos") or []):
            url = _save_photo(p.get("data_uri"))
            if url:
                doc.append("photos", {"image": url, "caption": p.get("caption"),
                                      "activity_task": p.get("activity_task") or None})

    doc.insert()   # enforces create permission + runs benkas_erp validate()
    doc.submit()   # runs on_submit rollups (task %, section %, material issue)
    frappe.db.commit()
    return {"name": doc.name, "section": doc.plant_section}
