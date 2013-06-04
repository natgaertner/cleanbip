VOTER_FILE_DISTRICTS = (
'state',
'county_id',
'county_council',
#'city_council',
#'municipal_district',
'school_district',
'judicial_district',
'congressional_district',
'state_rep_district',
'state_senate_district',
'township',
#'ward'
)
def ed_map_wrapper(ed_map):
    shpatt = re.compile(r'VT State House District (?P<name>(?:[A-Za-z ]+-?)+)(?:$|[ -](?P<numbers>(?:\d+-?)*))')
    sspatt = re.compile(r'VT State Senate District (?P<name>.+)')
    shexceptions = {'essex':'esx','windham':'wdh','windsor':'wdr','grand isle':'gi'}
    def vt_ed_map(ed):
        m = shpatt.match(ed)
        n = sspatt.match(ed)
        if m:
            names = '-'.join((n[0:3] if n.lower() not in shexceptions else shexceptions[n.lower()]) for n in m.groupdict()['name'].split('-'))
            numbers = ('-' + m.groupdict()['numbers']) if  m.groupdict()['numbers'] != None else ''
            ed = 'VT State House District ' + names + numbers
        elif n:
            name = n.groupdict()['name']
            if name.lower() == 'grand isle':
                ed = 'VT State Senate District Chittenden-Grand Isle'
        return ed_map(ed)
    return vt_ed_map
