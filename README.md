### Quickfix

Electronics Repair Management System

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app quickfix
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/quickfix
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

mit

### A2
1)site_config.json - stores site specific config details like db name,pass,type etc...
common_site_config.json - common for sites stored in a bench , stores workers,webport etc...
If we accidently put a secret like dbname and db pass , it would lead to data loss all sites can access.

2)web - handles incoming requests
worker - starts background jobs
scheduler - runs specific events
socketio - for real time communication
if a worker crashes , job is queued


## B1
1)When a browser hits /api/method/quickfix.api.get_job_summary..frappe.handler.handle handles this request ,
frappe imports the path , check if it is whitelisted and executes

2)When a browser hits /api/resource/Job Card/JC-2024-0001 - it is handled by REST API for doctypes
3) when browser hits /track-job, it is handled by website route rules defined in www folder

## session and csrf
1) the frappe csrf token  comes from current logged in user session , if we reject it , frappe rejects with csrf error
2)it shows details like session id, user name,ip address etc...

## Error visisbility
with developer mode 1 - the browser receives full error traceback
with developer mode 0 - only error , it is best for production, it doesnot expose code

In production full error are stored in Error log

## Permission 

Frappe.permission error


## B2 part A
1)tabJob Card
  tab Scheduled Job log
  tab scheduled Job type

  tab indicates table 

  so tab+Doctypename
2)name,customer name,assigned technician,status,creation

## B2 Part D 
1) docstatus 0 - Draft
   docstatus 1 - submitted
   docstatus 2 - cancelled
2)cannot call doc.save() in submitted document , only fiels with allow on submit can be updated
  cannot call doc.submit() in cancelled doc
3)the error "Document has been modified after you open" raises when another user update the same document after it was loaded.
prevent concurrent by modified timestamp

## B2 Part E
bug - calling self.save inside validate 
bug - calling another save

correct version

def validate(self):
    self.total = sum(r.amount for r in self.items)
def on_submit(self):
    doc=frappe.get_doc("Spare part",self.part)
    doc.stock_qty-=self.qty
    doc.save()


### Child table internals
1)parent
  parent name
  parent type
  idx
2)tabPart Usage Entry
3)idx values, restarts from first

### Renaming
1)if we rename , linked fields automatically updates. Track changes doesnt track,it is for about field change in specific doc
2)setting a field as unique in doc, that no two records can have same name - database level
  in validate, frappe.db.exists checks if the value is in db - before saving - application level

### D2 permission query
using frappe.get_all in whitelist function allow all user to access and get information - no permission chevks
always use frappe.get_list - it would check permissions
in hooks write 
  permission_query_conditions={"doctype":"......}
  for the doc, who has access

## upgrade friction

doc events is safer than override doctype class because, if we need to add custom logic without modifying core , doc events is better,
because we can write and configure by controller methods.
but in override doctype class , we need to completly override and extend our logic which is risk in some cases- if we not call super()

## doc events

1)two validate handlers in jobcard , one in main other in docevents 
    first controller logic will execute
    if controller raises error, doc events not runs
2) "*" and specific controller
both run.....first doctype specific controller will run and then wildcard

## on update()
calling self.save in onUpdate cause recursion, it never ends..on update will call save,if again save - it is recursion


## asset hooks
web_incluse js is for web pages
app_include js is for desk pages

doctype tree js- is used when doctype represents hierarchical data
example - account,item group when one parent , multiple children

During bench build frontend js and css comiples and stored in assets folder of sites.

## print format vs web (jinja)
print format provides doc for rendering
web needs context specific

## override whitelisted method
we use override whitelist method when we want to change the core whitelist function and move the traffic to our custom logic
we use monkey patching when we want to modify changes at run time 


when two apps register same override whitelisted function , the last installed win
signature mismatch happens when custom function not have same parameters as original function, in this case it raise type error

## fixtures
if we have custom field name (grand)..later frappe updates new field named (grand).....
name collision occurs, rename custom fieldname and if exported as fixtures remove and migrate

patch 2 depends on depend 1 , so order is important
if merged . there is no access when code tries

## monkey patch
_qf_patched is used because it ensure patch run only once
isolation improve maintainability ,if it used in init.py , then it run on every import

correct escalation - doc events, override doctype class,override whitelisted methods
doc events extends logic, override doctype class extend core controller logoc, override whitelist extends API

## H1
1)frappe.call inside the validate client event (before_save handler)

validate happens before save , frappe.call is asynchronous 
so it will not work

2)use refresh for async data fecth

## H3 
tree doctype - is a hierarchical data, for parent child relationships, one parent more child
tree doctype js - is for customizing tree doc features

## H4
client script - stored in db not in app code .
shipped js - stored in app code not in db , easier for production
js only hides the field in UI, but in DB it still exists.
api call can fetch the data.

## I1
fstring in sql is dangerous beacuse it can lead to sql injection attack
parameterized string will prevent by using %s and %(variable)s

## prepared report 
prepared report cache the result, if the user changes anything after report is craeted, user see the outdated data
this is called staleness
prepared report - for large data
script report - for small data

## Report builder
report builder - is appropriate when we need to show the report just by UI, without need of code
script report - required when we want to do calculations,complex logics etc...

Report builder is not suitable for production because, production needs calculations,logics..so it is not suitable for.





