

# Look at this : http://code.activestate.com/recipes/551763/  could  be a sol. Or __getitem__ / __setitem__

class Document:
    def __init__(self, is_collection=False, **kwargs):
        self.fields = kwargs
        self.is_collection = is_collection

    def edit_field(self, name, value):
        self.fields[name]=value

    def edit_fields(self, **kwargs):
        for k in self.fields:
            val = kwargs.pop(k, None)
            if val is not None:
                self.fields[k] = val

        self.fields = {**self.fields, **kwargs}

    # il faut gerer le cas des embded collections!
    def save_into(self, collection):
        pass

    def __getitem__(self, item):
        return self.fields[item]

    def __setitem__(self, key, value):
        self.fields[key]=value


class Collection:
    def __init__(self, name, auto_save=False):
        self.documents = []
        self.auto_save = auto_save
        self.name=name

    def add(self, document):
        self.documents.append(document)

    def save(self):
        pass

    def __getitem__(self, item):
        return self.documents[item]


# Note : All I have under that is rather useless.
# I will add any document as a general document.

class Match(Document):
    def __init__(self, teamA, teamB, local_team, date, competition, day, **kwargs):
        super(Match,self).__init__(is_collection=True,
                                   teamA=teamA, teamB=teamB, local_team=local_team, date=date, competition=competition,
                                   day=day, **kwargs)

    # Context is a context document
    def add_context(self, team, context):
        self.edit_field(team + '_context', context)

    # result is a result document
    def add_result(self, result):
        self.fields['result'] = result


class Result(Document):
    def __init__(self, teamA_goals, teamB_goals, winner=None, **kwargs):
        if winner is None:
            if teamA_goals > teamB_goals:
                winner='A'
            elif teamB_goals > teamA_goals:
                winner='B'
            else:
                winner='D'
        super(Result,self).__init__(teamA_goals=teamA_goals, teamB_goals=teamB_goals, winner=winner,**kwargs)


class Club(Document):
    def __init__(self, name, short_name=None, **kwargs):
        if not short_name:
            short_name=name[0:3]
        super(Club,self).__init__(is_collection=True,
                                  name=name, short_name=short_name, **kwargs)

    # Season is a ClubSeason document
    def add_season(self, season_name, season):
        self.fields['seasons'][season_name]=season


class ClubSeason(Document):
    def __init__(self, status='NONE', **kwargs):
        super(ClubSeason,self).__init__(status=status, players=[],**kwargs)

    def update_stats(self, rank, goals_for, goals_against, total_played, last_played):
        self.edit_fields(rank=rank, goals_for=goals_for, goals_against=goals_against,
                                            total_played=total_played, last_played=last_played)

    def add_player(self, name, **kwargs):
        self.fields['players'].append(Document(name=name, **kwargs))


class Competition(Document):

    def __init__(self, name, year, country, **kwargs):
        super(Competition, self).__init__(name=name, year=year, country=country, **kwargs)



    def add_ranking(self, day, date_updated, status):
        pass
        # TODO


class Ranking(Document):
    def __init__(self, day, date_updated, matchs_played, matchs_lefts, **kwargs):
        super(Ranking, self).__init__(self, day=day, date_updated=date_updated,matchs_played=matchs_played,
                                      matchs_lefts=matchs_lefts, teams=[], **kwargs)

    def add_team_ranking(self, rank, team, points, goals_for, goals_against, **kwargs):
        self.fields['teams'].append(Document(rank=rank, team=team, points=points, goals_for=goals_for,
                                             goals_against=goals_against, **kwargs))




# TODO : Need functions tu update elements already in the database!
