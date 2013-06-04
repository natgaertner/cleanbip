def ed_map_wrapper(ed_map_func):
    sdpat = re.compile(r'^(?:MA State Senate )(?P<names>.+)(?: District)$')
    hdpat = re.compile(r'^(?:MA State House )(?P<names>.+)(?: District)$')
    def ma_ed_map(ed):
        m = sdpat.match(ed)
        if m:
            ed = 'State Senate District ' + ' '.join(re.split(r'\s?(?:,|and|&)?\s?',m.groupdict()['names']))
        else:
            m = hdpat.match(ed)
            if m:
                ed = 'State House District ' + ' '.join(re.split(r'\s?(?:,|and|&)?\s?',m.groupdict()['names']))
        return ed_map_func(ed.lower())
    return ma_ed_map

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
