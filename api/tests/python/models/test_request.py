from flask import jsonify
from unittest import mock
import pytest


def test_get_queued_oldest(client, app):

    # SETUP #####
    # add NR to database
    from namex.models import Request as RequestDAO, State, User
    nr = RequestDAO()
    nr.nrNum='NR 0000001'
    nr.stateCd = State.DRAFT
    nr.save_to_db()

    user = User(username='testUser', firstname='first', lastname='last', sub='idir/funcmunk', iss='keycloak')
    user.save_to_db()

    nr_oldest, new_req = RequestDAO.get_queued_oldest(user)

    # Tests ####
    assert nr.nrNum == nr_oldest.nrNum


def test_get_queued_oldest_multirow(client, app):

    # add NR to database
    from namex.models import Request as RequestDAO, State, User
    nr_first = RequestDAO()
    nr_first.nrNum='NR 0000001'
    nr_first.stateCd = State.DRAFT
    nr_first.save_to_db()

    for i in range(2,12):
        nr = RequestDAO()
        nr.nrNum = 'NR {0:07d}'.format(i)
        nr.stateCd = State.DRAFT
        nr.save_to_db()

    user = User(username='testUser', firstname='first', lastname='last', sub='idir/funcmunk', iss='keycloak')
    user.save_to_db()

    nr_oldest, new_req = RequestDAO.get_queued_oldest(user)

    # Tests ####
    assert nr_first.nrNum == nr_oldest.nrNum
    assert nr_oldest.json()


def test_get_queued_empty_queue(client, app):

    # SETUP #####
    # add NR to database
    from namex.models import Request as RequestDAO, User
    from namex.exceptions import BusinessException

    user = User(username='testUser', firstname='first', lastname='last', sub='idir/funcmunk', iss='keycloak')
    user.save_to_db()

    with pytest.raises(BusinessException) as e_info:
        nr_oldest, new_req = RequestDAO.get_queued_oldest(user)

def test_name_search_populated_by_name():
    """Tests changing a name updates the nameSearch column."""
    from namex.models import Name, Request as RequestDAO, State

    name = Name()
    name.choice = 1
    name.name = 'TEST'
    name.state = 'NE'

    nr = RequestDAO()
    nr.nrNum='NR 0000001'
    nr.stateCd = State.DRAFT
    nr.names.append(name)
    nr.save_to_db()

    test = RequestDAO.find_by_id(nr.id)
    # sanity check
    names = test.names.all()
    assert len(names) == 1
    assert names[0].name == 'TEST'

    # check nameSearch
    assert nr.nameSearch == '|1TEST1|'

    # alter name
    name.name = 'CHANGED'
    name.save_to_db()

    # check nameSearch
    assert nr.nameSearch == '|1CHANGED1|'

def test_has_consumed_name():
    """Assert has_consumed_name."""
    from namex.models import Name, Request as RequestDAO, State
    name = Name()
    name.choice = 1
    name.name = 'TEST'
    name.state = 'APPROVED'

    nr = RequestDAO()
    nr.nrNum='NR 0000001'
    nr.stateCd = State.CONSUMED
    nr.names.append(name)
    nr.save_to_db()

    assert nr.has_consumed_name is True


def test_is_expired():
    """Assert is_expired."""
    from namex.models import Name, Request as RequestDAO, State

    name = Name()
    name.choice = 1
    name.name = 'TEST'
    name.state = 'APPROVED'

    nr = RequestDAO()
    nr.nrNum='NR 0000001'
    nr.stateCd = State.EXPIRED
    nr.names.append(name)
    nr.save_to_db()

    assert nr.is_expired is True
