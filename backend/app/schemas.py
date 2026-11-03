"""Pydantic response models (PLAN.md 3.4). Field names are the API contract.

`import datetime as dt` because a field named `date` typed `date` shadows the type and breaks Pydantic.
"""

import datetime as dt
from typing import Literal

from pydantic import BaseModel

from app.domain.detection import Status


class Health(BaseModel):
    status: Literal["ok", "error"]
    db: Literal["ok", "error"]


class AccountSummary(BaseModel):
    id: int
    name: str
    industry: str
    timezone: str
    location_count: int
    latest_complete_week: dt.date | None


class AccountRef(BaseModel):
    id: int
    name: str
    timezone: str


class Week(BaseModel):
    start: dt.date  # Monday
    end: dt.date  # Sunday


class Baseline(BaseModel):
    method: Literal["median_mad"]
    weeks_used: int
    start: dt.date | None  # Monday of the oldest history week
    end: dt.date | None  # Sunday of the newest history week


class Metric(BaseModel):
    total: int
    usual: float | None
    lower: float | None
    upper: float | None
    pct_vs_usual: float | None
    status: Status
    low_volume: bool


class LocationMetric(Metric):
    location: str
    history_weeks: int


class Day(BaseModel):
    date: dt.date
    weekday: Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    total: int
    usual: float | None


class WeeklyInsight(BaseModel):
    account: AccountRef
    week: Week
    baseline: Baseline
    summary: Metric
    days: list[Day]
    locations: list[LocationMetric]
    data_notes: list[str]
