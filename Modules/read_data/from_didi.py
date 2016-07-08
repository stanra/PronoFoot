import xlrd
import db_model as model
import db_client
import dateparser
import re
from collections import Counter

def read_season(file, comp_name, year):

    competitions = model.Collection('competitions')
    competitions.append(model.Document('competition', name=comp_name, year=year, participants=['non', 'implemented']))

    xls_file = xlrd.open_workbook(file)
    sheet = xls_file.sheet_by_name('Pronos')

    participants = find_participants(sheet)

    all_matches = model.Collection('matches')
    for day in range(1, 39):
        read_day(sheet, comp_name, day, participants, all_matches)

    return competitions, all_matches


def read_day(sheet, competition, day, participants, collection):

    line = 4 + (day-1)*(10+4)

    temp = sheet.cell(rowx=line,colx=0).value

    _, date = re.split(r'[ ]*[,:][ ]*',temp)
    line += 2

    for line in range(line+1, line+11):
        teamA = sheet.cell(rowx=line, colx=0).value
        teamB = sheet.cell(rowx=line, colx=3).value
        teamA_goals = sheet.cell(rowx=line, colx=1).value
        teamB_goals = sheet.cell(rowx=line, colx=2).value

        match = model.Document('match', team_A=teamA, team_B=teamB, home=teamA,
                               day=day, date=dateparser.parse(date), pronos=[], competition=competition,
                               result=model.Document(
                                   'result', team_A_goals=int(teamA_goals), team_B_goals=int(teamB_goals))
                               )

        for i,par in enumerate(participants):
            col = 4 + i * 2

            try:
                teamA_goals = int(sheet.cell(rowx=line, colx=col).value)
            except ValueError:
                teamA_goals = None
            try:
                teamB_goals = int(sheet.cell(rowx=line, colx=col+1).value)
            except ValueError:
                teamB_goals = None

            prono = model.Document('prono', participant_name = par,
                                   team_A_goals = teamA_goals,
                                   team_B_goals = teamB_goals )
            match['pronos'].append(prono)

        collection.append(match)

def find_participants(sheet):
    participants = []
    line = 6
    col = 4
    while True:
        par = sheet.cell(rowx=line, colx=col).value
        if not par:
            break
        participants.append(par)
        col += 2
    return participants


def give_points(db_name):
    matches = db_client.get_collection(db_name, 'matches')
    cur = matches.find()
    for match in cur:
        real_A = match['result']['team_A_goals']
        real_B = match['result']['team_B_goals']
        diff = real_A - real_B
        for prono in match['pronos']:
            participant_name = prono['participant_name']
            guess_A = prono['team_A_goals']
            guess_B = prono['team_B_goals']
            played = False
            result = False
            score = False
            points = 0
            if guess_A is None or guess_B is None:
                pass
            else:
                played = True
                if (guess_A - guess_B) == diff:
                    result = True
                    if (real_A == guess_A) and (real_B == guess_B):
                        score = True

                elif (guess_A - guess_B) * diff > 0:
                    result = True
                    if (real_A == guess_A) and (real_B == guess_B):
                        score = True

            if result:
                points +=1
            if score:
                points +=2

            matches.update_one(
                {'_id':match['_id'], "pronos.participant_name":participant_name},
                {
                    '$set': {
                        'pronos.$.played':played,
                        'pronos.$.result':result,
                        'pronos.$.score':score,
                        'pronos.$.points':points
                    }
                 }
            )


def count_points(db_name, comp_name):
    """
    adds a field 'pronos' which is a list of emdded documents with : participant_name, total_points, total_played

    """
    total_points = Counter()
    total_played = Counter()
    total_result = Counter()
    total_score = Counter()

    for match in db_client.get_collection(db_name,'matches').find({'competition':comp_name}):
        for prono in match['pronos']:
            total_points[prono['participant_name']] += prono['points']
            if prono['played']:
                total_played[prono['participant_name']] += 1
            if prono['result']:
                total_result[prono['participant_name']] += 1
            if prono['score']:
                total_score[prono['participant_name']] += 1

    pronos = []
    for k in total_played:
        pronos.append({'participant_name':k, 'total_points':total_points[k], 'total_played':total_played[k],
                       'total_result':total_result[k], 'total_score':total_score[k]})

    db_client.get_collection(db_name, 'competitions').update_one(
        {'name':comp_name},
        {'$set': {
                'pronos':pronos}
        }
    )


def count_points_each_competition(db_name):
    for comp in db_client.get_collection(db_name,'competitions').find():
        count_points(db_name,comp['name'])



if __name__ == '__main__':

    #folder = 'C:\\Users\\stanr\\Documents\\Projects\\PronoFoot\\Data\\Family Pronos\\Pronostics_L1_Saison_'
    #seasons = ['2011-2012', '2012-2013', '2013-2014', '2014-2015', '2015-2016']

    #files = [ folder + season + '.xls' for season in seasons ]
    #competitions = [ 'Ligue 1 ' + season for season in seasons ]
    #years = list(range(2011,2016))
    #participants = [5,6,9,9,9]

    #for file, competition, year, nb_participants in zip(files, competitions, years, participants):
    #    comp, matches = read_season(file, competition, year)
    #    comp_d = comp.save(output=False, in_db='test_didi_4')
    #    matches_d = matches.save(output=True, in_db='test_didi_4')


#    give_points('test_didi_4')

    count_points_each_competition('test_didi_4')
