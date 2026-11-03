from app.domain.detection import Evaluation, Status
from app.domain.ranking import rank_locations


def ev(status: Status, pct: float | None = None) -> Evaluation:
    usual = None if status is Status.NOT_ENOUGH else 10.0
    return Evaluation(0, usual, None, None, pct, status, False, 8)


def test_rank_order_with_ties():
    items = [
        ("West", ev(Status.HIGHER, 1.0)),
        ("Zed", ev(Status.NOT_ENOUGH)),
        ("North", ev(Status.NORMAL, 0.0)),
        ("South", ev(Status.LOWER, -0.6)),
        ("Alpha", ev(Status.NOT_ENOUGH)),
        ("Bravo", ev(Status.LOWER, -0.6)),  # ties with South: by name
        ("East", ev(Status.LOWER, -0.8)),
    ]
    ranked = [name for name, _ in rank_locations(items)]
    # lower by pct then name; higher+normal mixed by name; not_enough last by name
    assert ranked == ["East", "Bravo", "South", "North", "West", "Alpha", "Zed"]
