import xlrd
import db_model as model
import dateparser
import re

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
                teamB_goals = int(sheet.cell(rowx=line, colx=col).value)
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



if __name__ == '__main__':
    folder = 'C:\\Users\\stanr\\Documents\\Projects\\PronoFoot\\Data\\Family Pronos\\Pronostics_L1_Saison_'
    seasons = ['2011-2012', '2012-2013', '2013-2014', '2014-2015', '2015-2016']

    files = [ folder + season + '.xls' for season in seasons ]
    competitions = [ 'Ligue 1 ' + season for season in seasons ]
    years = list(range(2011,2016))
    participants = [5,6,9,9,9]

    for file, competition, year, nb_participants in zip(files, competitions, years, participants):
        comp, matches = read_season(file, competition, year)
        #comp_d = comp.save(output=False, in_db='test_didi_2')
        #matches_d = matches.save(output=True, in_db='test_didi_2')




