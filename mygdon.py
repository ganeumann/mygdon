# Mygdon list
#
# to-do:
#    add date filters, number of deal filters
#    finish al angel code
#    pretty print
# pause between sections to fix failed cb calls!

import urllib2
import simplejson as json
import sys, csv

# 1. List of Midas list VCs in midas = [vc1,vc2,...]
midas = ["sequoia-capital",
  "andreessen-horowitz",
  "benchmark-2",
  "founders-fund",
  "accel-partners",
  "greylock",
  "baseline-ventures",    
  "meritech-capital-partners",
  "new-enterprise-associates",    
  "first-round-capital",
  "lowercase-capital",
  "floodgate",
  "union-square-ventures",  
  "institutional-venture-partners",
  "bessemer-venture-partners",
  "kleiner-perkins-caufield-byers",
  "insight-venture-partners",
  "norwest-venture-partners",   
  "bain-capital-ventures",
  "mayfield-fund",
  "spark-capital",
  "digital-sky-technologies-fo",       
  "battery-ventures",        
  "charles-river-ventures",
  "draper-fisher-jurvetson",
  "oak-investment-partners",
  "general-catalyst-partners",
  "felicis-ventures",
  "lakestar",
  "ggv-capital",
  "wing-vc",
  "dcm",
  "maveron", 
  "menlo-ventures",
  "tiger-global",
  "venrock",
  "khosla-ventures",
  "orbimed-advisors",
  "sv-angel",
  "lightspeed-venture-partners",
  "emergence-capital-partners",
  "the-social-capital-partnership",
  "morningside-group", 
  "index-ventures",
  "sherpa-ventures", 
  "polaris-partners",
  "summit-partners",
  "redpoint-ventures",
  "aspect-ventures"]


alias = {'benchmark-capital-2-deleted': 'benchmark-2',
			'juniper-networks-deleted': None,
			'morningside-ventures-deleted': 'morningside-group',
			'zhenfund-deleted': None,
			'floodgate-fund-deleted': 'floodgate',
			'u-s-venture-partners-deleted-2': 'u-s-venture-partners',
			'benchmark-1': 'benchmark-2',
			'benchmark': 'benchmark-2',
			"tim-draper-deleted": "timothy-draper", 
			"michael-lambert": "michael-lambert", 
			"openfund-deleted": None, 
			"u-s-venture-partners-2-deleted": "u-s-venture-partners", 
			"endeavour-vision": "", 
			"andreessen-horowitz-deleted-2": "andreessen-horowitz", 
			"first-american-bank": None,  
			"social-capital-partnership-deleted": "social-capital-partners",  
			"500startups-deleted": "500-startups", 
			"abingworth-management-ltd-deleted": "abingworth-management",  
			"highline-ventures-deleted": None, 
			"box-group-deleted": "boxgroup", 
			"cmea-ventures-deleted": "cmea-capital", 
			"university-of-california-berkeley-deleted": None,  
			"gary-vaynerchuck-deleted": None, 
			"john-maloney-4-deleted": "john-maloney"} 


def earlier(date1,date2):
	# return earlier of date1 and date2
	if date1<date2: return date1
	return date2

def getCBinfo(namespace, permalink):
	api_url = "http://api.crunchbase.com/v/1/%s/%s.js?api_key=juszeqhjb6rq4bcckzqb5kz7" % (namespace, permalink)
	try:
		rtn = json.loads(urllib2.urlopen(api_url).read(),strict=False)
	except:
		rtn = False
	return rtn

# for each VC, get all deals
def getVCcos(vcpl):
	# get all companies invested in and which round was first
	# in form [(companypl: round,...),...]
	if vcpl in alias: vcpl=alias[vcpl]
	if not vcpl: return False
	info = getCBinfo("financial-organization",vcpl)
	# if not info: info = getCBinfo("person",vcpl)
	if not info: return False
	if not info.has_key("investments"): return False
	companies = {}
	for i in info["investments"]:
		if i.has_key("funding_round"):
			copl = i["funding_round"]["company"]["permalink"]
			month = i["funding_round"]["funded_month"] or 0
			year = i["funding_round"]["funded_year"] or 2005
			invdate = year*100+month
			if not companies.has_key(copl) or invdate<companies[copl]: 
				companies[copl]=invdate
	return [(co,companies[co]) for co in companies]
	
def getCodata(copl):
	# get company data from cb and return in form [(investor, first investment date),...]
	# return {funder: round,...}
	# need first investment date
	if not copl: return False
	info = getCBinfo("company",copl)
	if not info: return False
	if not info.has_key("funding_rounds"): return False
	funders = {}
	for i in info["funding_rounds"]:
		if i.has_key("investments") and i["funded_year"]:
			month = i["funded_month"]
			if not month: month = 0
			year = i["funded_year"]
			invdate = year*100+month
			for j in i["investments"]:
				fupl = (j["financial_org"] and j["financial_org"]["permalink"]) # or (j["person"] and j["person"]["permalink"])
				if fupl: funders[fupl] = earlier(funders.get(fupl,invdate),invdate)
	return [(vc,funders[vc]) for vc in funders]
	
def whyvc(pl):
	# tell why a vc is ranked
	cos = []
	for i in co_data:
		ms = []
		for ovc, ovcd in co_data[i]:
			if ovc==pl:
				for j in m_cb:
					if type(m_cb[j])!=bool:
						for k in m_cb[j]:
							if k[0]==i:
								ms.append(j)
		if ms: print i,':',', '.join(ms)
	return

# 2. Get midas entries from cb, m_cb = {mvc: [(co,first round date),(co,first round),...],...}
# 2a. parse out all portfolio companies into mcos = = {co:date,co:date,...}


failures = []

m_cb = {}
mcos = {}
for i in midas:
	a = getVCcos(i)
	if not a:
		print "Failed on midas",i
		failures.append(i)
	else:
		m_cb[i] = a
		# create list of unique companies with earliest midas firm investment date, mcos = {co:date,co:date,...}
		for co,dt in m_cb[i]:
			mcos[co] = earlier(mcos.get(co,dt),dt)

print "Loaded Midas VCs. ",len(mcos)," companies to search."

# 3. Get all co entries {co: [(other vc, first round date),(other vc, first round date),...],...}
co_data = {}
mygdonvc = {}     # mygdonvc = {vc: mydon deals, vc: mygdon deals,...}
failures = []
for i in mcos:
	a = getCodata(i)
	if not a:
		print "Failed on company",i
		failures.append(i)
	else:
		co_data[i] = a
		for ovc,ovcd in co_data[i]:
			if ovc not in midas:
				if ovcd <= mcos[i]: mygdonvc[ovc]=mygdonvc.get(ovc,0) + 1

print "Loaded companies. ",len(mygdonvc)," potential Mygdons."

# remap deleted entries to extant ones

# 4. Get each vc entry, vc_ttl = {vc:# cos,vc:# cos,...}
vc_ttl = {}
failures = []
for i in mygdonvc:
	a = getVCcos(i)
	if not a:
		print "Failed on mygdon",i
		failures.append(i)
	else:
		vc_ttl[i] = len(a)

print "Loaded Mygdons."

topmygdon = []
# 5. Filter all
for i in mygdonvc:
	if i in vc_ttl and vc_ttl[i]>=20:
		topmygdon.append((i,mygdonvc[i],vc_ttl[i],mygdonvc[i]*1.0/vc_ttl[i]))
topmygdon.sort(key = lambda x: -x[3])