# Copyright (c) 2026, Velmurugan and contributors
# For license information, please see license.txt

from warnings import filters
import frappe
from frappe import _




def execute(filters: dict | None = None):
	columns = get_columns(filters)
	data = get_data(filters)

	total_jobs = sum(d["total_jobs"] for d in data)
	total_revenue = sum(d["revenue"] for d in data)
	best_technician = max(data, key=lambda x: x["completion_rate"] if x["total_jobs"] > 0 else 0)

	report_summary = [
		{"label": _("Total Jobs"), "value": total_jobs},
		{"label": _("Total Revenue"), "value": total_revenue, "currency": "currency"},
		{"label": _("Best Technician"), "value": best_technician["technician"] if best_technician["total_jobs"] > 0 else _("N/A")},
	]

	chart= {
		"data": {
			"labels": [d["technician"] for d in data],
			"datasets": [
				{
					"name": _("Total Jobs"),
					"values": [d["total_jobs"] for d in data]
				},
				{
					"name": _("Completed Jobs"),
					"values": [d["completed"] for d in data]
				}
			]
		},
		"type": "bar",
		"height": 300,
	}
	return columns, data, None, chart, report_summary

def get_columns(filters: dict | None = None):
	cols =  [
		{
			"label": _("Technician"),
			"fieldname": "technician",
			"fieldtype": "Link",
			"options": "Technician",
		},
		{
			"label": _("Total Jobs"),
			"fieldname": "total_jobs",
			"fieldtype": "Int",
		},
		{
			"label": _("Completed"),
			"fieldname": "completed",
			"fieldtype": "Int",
		},
		{
			"label": _("Avg Turnaround Days"),
			"fieldname": "avg_turnaround_days",
			"fieldtype": "Int",
		},
		{
			"label": _("Revenue"),
			"fieldname": "revenue",
			"fieldtype": "currency",
		},
		{
			"label": _("Completion Rate (%)"),
			"fieldname": "completion_rate",
			"fieldtype": "percent",
		}
	]

	for dt in frappe.get_all("Device Type", fields=["name"]):
		cols.append({
			"label": dt.name,
			"fieldname": dt.name.lower().replace(" ", "_"),
			"fieldtype": "Int",
			"width": 100
		})
	return cols
	

def get_data(filters: dict | None = None):
	job_card = frappe.get_list(
		"Job Card",
		fields=["assigned_technician", "status", "creation", "final_amount", "device_type", "modified"],
		filters={"creation": ["between", [filters["from_date"], filters["to_date"]]]}
	)
	technician_data = {}
	for job in job_card:
		tech = job.assigned_technician
		if tech not in technician_data:
			technician_data[tech] = {
				"technician": tech,
				"total_jobs": 0,
				"completed": 0,
				"turnaround": [],
				"revenue": 0,
			}
		
		technician_data[tech]["total_jobs"] += 1
		if job.status == "Ready for Delivery":
			technician_data[tech]["completed"] += 1
			turnaround_days = (job.modified - job.creation).days
			technician_data[tech]["turnaround"].append(turnaround_days)
			technician_data[tech]["revenue"] += job.final_amount

		if job.device_type:
			key = job.device_type.lower().replace(" ", "_")
			technician_data[tech].setdefault(key, 0)
			technician_data[tech][key] += 1

	data = []
	for t in technician_data.values():
		if t["total_jobs"]:
			t["completion_rate"] = (t["completed"] / t["total_jobs"]) * 100
		else:
			t["completion_rate"] = 0

		if t["turnaround"]:
			t["avg_turnaround_days"] = sum(t["turnaround"]) / len(t["turnaround"])
		else:
			t["avg_turnaround_days"] = 0

		data.append(t)

	return data


@frappe.whitelist()
def generate_prepared_report(filters=None):

    frappe.enqueue(
        method="quickfix.service_center.report.technician_performance.technician_performance.execute",
        queue="long",
        timeout=600,
        filters=filters
    )

    return "Technician Performance report started in background"