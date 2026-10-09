from conftest import NOW, check

from betdex import BetDexClient


def test_categories(client: BetDexClient):
    """
    Categories can be listed and fetched by id.
    """
    categories = check(client.get_categories()).categories
    assert categories
    assert check(client.get_category(categories[0].id)).categories[0].id == categories[0].id


def test_subcategories(client: BetDexClient):
    """
    Subcategories filter by category and can be fetched with their participants.
    """
    category = client.get_categories().categories[0]
    subcategories = check(client.get_subcategories([category.id])).subcategories
    assert subcategories and all(s.category.ids == [category.id] for s in subcategories)
    one = subcategories[0]
    assert check(client.get_subcategory(one.id)).subcategories[0].name == one.name
    assert check(client.get_subcategory_participants(one.id)).participants is not None


def test_lookups_by_external_reference(client: BetDexClient):
    """
    Subcategories, event groups, participants and events can be found by external reference.
    """
    subcategories = client.get_subcategories()
    ref = subcategories.external_references[0]
    found = check(client.get_subcategory_by_reference(ref.source, ref.external_reference))
    assert found.subcategories

    groups = client.get_event_groups()
    ref = groups.external_references[0]
    found = check(client.get_event_group_by_reference(ref.source, ref.external_reference))
    assert found.event_groups

    participants = client.get_subcategory_participants(subcategories.subcategories[0].id)
    if participants.external_references:
        ref = participants.external_references[0]
        found = check(client.get_participants_by_reference(ref.source, ref.external_reference))
        assert found.participants

    assert check(client.get_events_by_reference("FFT", "no-such-reference")).events == []


def test_event_groups(client: BetDexClient):
    """
    Event groups can be listed, fetched by id and filtered by subcategory.
    """
    groups = check(client.get_event_groups()).event_groups
    assert groups
    assert check(client.get_event_group(groups[0].id)).event_groups[0].id == groups[0].id
    subcategory_id = groups[0].subcategory.ids[0]
    filtered = check(client.get_event_groups([subcategory_id])).event_groups
    assert all(g.subcategory.ids == [subcategory_id] for g in filtered)


def test_events(client: BetDexClient):
    """
    Events filter by date range and can be fetched with their participants.
    """
    page = check(client.get_events(active=True, from_date_time=NOW, starting="Range", size=10))
    assert page.events and page.meta.page.page_size == 10
    event = page.events[0]
    assert check(client.get_event(event.id)).events[0].name == event.name
    check(client.get_event_participants(event.id))
