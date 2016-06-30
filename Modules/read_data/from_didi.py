import xlrd
from db_client import model


def read_season(file, comp_name, year, country, nb_participants):
    competition = model.Document(name=comp_name, year=year, country=country)
    # todo : add comptetion in the competitions collection

    xls_file = xlrd.open_workbook(file)
    sheet = xls_file.sheet_by_name('Pronos')


    # to do : all match day in same collection right ?
    match_day = read_day(sheet, day, nb_participants, comp_name);

    for day in range(1, 39):
        match_day = read_day(sheet, day)


def read_day(sheet, day, nb_participants, competition):

    line = 4 + (day-1)*(10+3)

    temp = sheet.cell(rowx=line,colx=0).value

    if not temp:
        return False

    _, date = temp.split(' : ')

    line = line+2
    participants = []
    for i in range(0,nb_participants):
        col = 4 + i * 2
        participants.append(sheet.cell(rowx=line, colx=col).value)


    all_matches = model.Collection('matches')

    for line in range(line+1, line+11):
        teamA = sheet.cell(rowx=line, colx=0).value
        teamB = sheet.cell(rowx=line, colx=3).value
        teamA_goals = sheet.cell(rowx=line, colx=1).value
        teamB_goals = sheet.cell(rowx=line, colx=2).value

        match = model.Document(teamA=teamA, teamB=teamB, teamA_goals=teamA_goals, teamB_goals=teamB_goals,
                               day=day, date=date, pronos={}, competition=competition)

        for i,par in enumerate(participants):
            col = 4 + i * 2
            prono = model.Document(teamA_goals = sheet.cell(rowx=line, colx=col),
                                   teamB_goals = sheet.cell(rowx=line, colx=col+1) )
            match['pronos'][par] = prono

        all_matches.add(match)

        return all_matches

        # TODO : add the match in the 'matches' collection

# Todo : figure by myself what is the number of participants ?



