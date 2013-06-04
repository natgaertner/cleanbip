from collections import defaultdict
from state_abbr import states
import difflib
from reformat import ed_concat
class EdMapTemplate():
    district_patterns = {
            'judicial_district':('judicial district','district court',),
            'county_council':('County Commissioner Precinct','County Commission Precinct','County Comissioner District','Commissioner District', 'County Commissioner', 'CO Commission District','CO Commissioner District','County District','County Commissioner District','County - Commission District','County Commission District','County Committee District','County - Commissioner District','County - Comm District','County - Council District','County Council District','County - County Commissioner District','County - District','County Board District','County Board - District','- District', 'Commission District', '- County Commissioner District', 'County - County Commissioner - District'),
            'congressional_district':('Congressional','Congressional District'),
            'state_senate_district':('State Senate','State Senate District','State Senator','State Senator District'),
            'state_rep_district':('State House','State House of Representatives','State Representative','Legislature','Legislative','State House District','State House of Representatives District','State Representative District','Legislature District','Legislative District'),
            'school_district':('school district','county school board district','county school board','school board district', 'school board' 'county school board precinct','school board precinct','school district','county school district','school precinct','county - school board district','county - school board', 'county board of education','board of education','county board of education district','board of education district','county - board of education district'),
            'county':('county','LRG'),
            'state':states,
            'township':('township','(muni)','town of'),
            'ward':('ward',),
            'city_council':('city council','city of council', 'city council district'),
            }

    def __init__(self,districts,county_school_district_flag,county_judicial_district_flag):
        self.d_dict = defaultdict(lambda:[],districts.__dict__)
        self.judicial_district = self.d_dict['judicial_district']
        self.county_council = self.d_dict['county_council']
        self.congressional_district = self.d_dict['congressional_district']
        self.state_senate_district = self.d_dict['state_senate_district']
        self.state_rep_district = self.d_dict['state_rep_district']
        self.school_district = self.d_dict['school_district']
        self.county_school_district = self.d_dict['county_school_district']
        self.county_id = self.d_dict['county_id']
        self.state = districts.state
        self.district_patterns = dict(EdMapTemplate.district_patterns)

    def ed_map(self,ed):
        best_match = self.best_matches(ed)[-1]
        if best_match[2]+best_match[4] > .90:
            return best_match[3],best_match[0],ed_concat(best_match[3],best_match[0])[0],True
        else:
            return ed,'',ed_concat(ed,'')[0],False

    def best_matches(self,ed):
        ed = ed.lower()
        best_matches = [(name,)+max([(p,difflib.SequenceMatcher(None,ed,p.lower())) for p in patterns],key=lambda (p,seq):seq.ratio()) for name,patterns in EdMapTemplate.district_patterns.items()]
        best_matches = [(name,p,seq.ratio())+max([(d,score_non_matching(ed,p,seq.get_matching_blocks(),d.lower())) for d in self.d_dict[name]]+[(None,0)],key=lambda (d,score):score) for name,p,seq in best_matches]
        best_matches = sorted(best_matches,key=lambda (name,max_pattern,score,max_dist,dist_score):score+dist_score)
        return best_matches


def score_non_matching(a,b,matching_blocks,to_match):
    non_matching_a,non_matching_b = non_matching_blocks(a,b,matching_blocks)
    raw_score = difflib.SequenceMatcher(None,non_matching_a,to_match).ratio()
    scaled_score = raw_score*len(non_matching_a)/len(a)
    return scaled_score


def non_matching_blocks(a,b,matching_blocks):
    non_matching_a = ''
    non_matching_b = ''
    start_a = 0
    start_b = 0
    for mb in matching_blocks:
        non_matching_a += a[start_a:mb[0]]
        non_matching_b += b[start_b:mb[1]]
        start_a = mb[0]+mb[2]
        start_b = mb[1]+mb[2]
    return non_matching_a,non_matching_b
