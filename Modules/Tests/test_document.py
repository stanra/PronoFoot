import pytest

def test_document_init():
    from db_model import Document
    temp = Document(a=12, c='string')
    assert (temp['a'] == 12) and (temp['c'] == 'string')


def test_new_field():
    from db_model import Document
    temp = Document(a=12)
    temp['c'] = 'string'
    assert (temp['a'] == 12) and (temp['c'] == 'string')


def test_has_key():
    from db_model import Document
    temp = Document(a=12)
    temp['c'] = 'string'
    assert temp.has_key('a') and temp.has_key('c')


def test_not_has_key():
    from db_model import Document
    temp = Document()
    assert not temp.has_key('a')


def test_no_added_field():
    from db_model import Document
    temp = Document()
    with pytest.raises(KeyError):
        temp['c']


class TestSaveInput:

    def test_safe_competition(self):
        from db_model import Document
        temp = Document('competition', name='Name', year=2015, participants=['Stan', 'Pierre'])
        temp.save(safe_input=True)
        assert True

    def test_missing_type(self):
        from db_model import Document, ModelError
        temp = Document(name='Name', year=2015, participants=['Stan', 'Pierre'])
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

    def test_competition_missing_field(self):
        from db_model import Document, ModelError
        temp = Document('competition', name='Name', participants=['Stan', 'Pierre'])
        with pytest.raises(ModelError):
            data = temp.save(safe_input=True)

    def test_wrong_field(self):
        from db_model import Document, ModelError
        temp = Document('competition', name='Name', year=2015, participants=['Stan', 'Pierre'], wrong_one='unexpected')
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

    def test_competition_wrong_type(self):
        from db_model import Document, ModelError
        temp = Document('competition', name='Name', year=2015, participants='Stan')
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

    def test_competition_wrong_type_2(self):
        from db_model import Document, ModelError
        temp = Document('competition', name='Name', year='2015', participants='Stan')
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

    def test_competition_unsafe(self):
        from db_model import Document
        temp = Document('competition', name='Name', participants=['Stan', 'Pierre'])
        temp.save(safe_input=False)
        assert True

    def test_inlist_type(self):
        from db_model import Document, ModelError
        temp = Document('competition', name='Name', year='2015', participants=['Stan', 12])
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

    def test_embedded_doc_ok(self):
        from db_model import Document, ModelError
        import datetime
        temp = Document('match', team_A='a', team_B='b', home='b',  date=datetime.datetime.now(),
                        competition = 'c', day=1,
                        result=Document('result', team_A_goals=1, team_B_goals=2),
                        pronos=[Document('prono', participant_name='a', team_A_goals=1, team_B_goals=1)])
        temp.save(safe_input=True)

    def test_embedded_doc_error(self):
        from db_model import Document, ModelError
        import datetime
        temp = Document('match', teamA='a', teamB='b', home='b',  date=datetime.datetime.now(),
                        competition='c', day=1,
                        result=Document(team_A_goals=1, team_B_goals=2),
                        pronos=[Document('prono', participant_name='a', team_A_goals=1, team_B_goals=1)])
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

    def test_embedded_doc_error2(self):
        from db_model import Document, ModelError
        import datetime
        temp = Document('match', teamA='a', teamB='b', home='b', date=datetime.datetime.now(),
                        competition = 'c', day=1,
                        result=Document('result',team_A_goals=1, team_B_goals=2),
                        pronos=[Document('prono', participant_name=12, team_A_goals='1', team_B_goals=1)])
        with pytest.raises(ModelError):
            temp.save(safe_input=True)

# todo write test for each specific document (too tiring, too many changes in the future...)
# todo : if the message to print for the error is defined more definitely, should test that good error message is given
