from __future__ import annotations

from html import escape


def prescription_html(rx: dict, hospital_name: str = "SurgiScore Clinic") -> str:
    patient = rx.get("patient", {})
    items = rx.get("items", [])
    rows = []
    for index, item in enumerate(items, 1):
        directions = " · ".join(
            str(v) for v in [
                item.get("dose"), item.get("dose_unit"), item.get("route"), item.get("frequency"),
                f"{item.get('duration_days')} days" if item.get("duration_days") else None,
            ] if v
        )
        rows.append(
            f"<tr><td>{index}</td><td><strong>{escape(item.get('medication_name') or '')}</strong> "
            f"{escape(item.get('strength') or '')} {escape(item.get('dosage_form') or '')}<br>"
            f"<span>{escape(directions)}</span><br>"
            f"<small>{escape(item.get('instructions_ar') or '')}</small></td></tr>"
        )
    return f"""<!doctype html>
<html lang='ar'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Prescription #{rx.get('id')}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;margin:32px;color:#1d1d1f}}
.header{{display:flex;justify-content:space-between;border-bottom:2px solid #111;padding-bottom:16px}}
.card{{border:1px solid #ddd;border-radius:14px;padding:16px;margin-top:16px}}
table{{width:100%;border-collapse:collapse;margin-top:16px}}td{{border-bottom:1px solid #eee;padding:12px;vertical-align:top}}
.footer{{margin-top:32px;display:flex;justify-content:space-between}}
@media print{{button{{display:none}}body{{margin:16px}}}}
</style></head><body dir='rtl'>
<div class='header'><div><h2>{escape(hospital_name)}</h2><div>وصفة طبية / Prescription</div></div><div>#{rx.get('id')}</div></div>
<div class='card'>
<strong>المريض:</strong> {escape(patient.get('full_name') or '')}<br>
<strong>MRN:</strong> {escape(patient.get('mrn') or '')}<br>
<strong>التاريخ:</strong> {escape(str(rx.get('signed_at') or rx.get('created_at') or ''))}<br>
<strong>الاستطباب:</strong> {escape(rx.get('indication') or '')}
</div>
<table>{''.join(rows)}</table>
<div class='card'><strong>ملاحظات:</strong><br>{escape(rx.get('notes') or '')}</div>
<div class='footer'><div>Prescriber: {escape(rx.get('signed_by') or rx.get('prescribed_by') or '')}</div><div>Signature: __________________</div></div>
<script>window.onload=()=>{{}}</script>
</body></html>"""
