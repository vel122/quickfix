import frappe
@frappe.whitelist()
def get_status_chart_data():
    cache = frappe.cache()
    key="job_status_chart"
    cached= cache.get(key)
    if cached:
        return cached
    data = frappe.db.sql("""SELECT status, COUNT(name) as count from `tabJob Card` GROUP BY status""",as_dict=True)
    labels = []
    values = []
    for d in data:
        labels.append(d.status)
        values.append(d.count)

    result= {
        "labels": labels,
        "datasets": [
            {
                "name": "Jobs",
                "values": values
            }
        ]
    }
    cache.set_value(key,result,expires_in_sec=300)
    return result
