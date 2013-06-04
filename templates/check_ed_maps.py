import csv
from ed_map_template_new import EdMapTemplate
from process_units.November_2012.va import districts
#from process_units.November_2012.ma import districts_fixed
emt = EdMapTemplate(districts,False,False)
#emt = EdMapTemplate(districts_fixed,False,False)
f = open('/home/gaertner/Dropbox/noBIP/office_holders/June_2013/VA Office Holders.csv')
#f = open('/home/gaertner/Dropbox/BIP Production/candidates/2012/MA Candidates.csv')
oh_csv = csv.DictReader(f)
g = open('test.csv','w')
#test_csv = csv.DictWriter(g,fieldnames='ed,type,filler,dist,score,dist_score'.split(','))
test_csv = csv.DictWriter(g,fieldnames=['ed','type','dist'])
for row in oh_csv:
    ed_match,dist = emt.ed_map(row['Electoral District'])
    #test_csv.writerow({'ed':row['Electoral District'],'type':ed_match[-1][0],'filler':ed_match[-1][1],'dist':ed_match[-1][3],'score':ed_match[-1][2],'dist_score':ed_match[-1][4]})
    test_csv.writerow({'ed':row['Electoral District'],'type':ed_match,'dist':dist})
