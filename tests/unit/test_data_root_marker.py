import pytest

from argus.runtime.data_root_marker import DataRootMarker
from argus.runtime.environment import Environment


def test_data_root_marker_can_be_created() -> None:
    marker = DataRootMarker(
        state_id="state-test-001",
        data_root_id="data-test-001",
        environment=Environment.TEST,
        created_at="2026-09-12T14:00:00+09:00",
    )

    assert marker.state_id == "state-test-001"
    assert marker.data_root_id == "data-test-001"
    assert marker.environment is Environment.TEST
    assert marker.created_at == "2026-09-12T14:00:00+09:00"


@pytest.mark.parametrize(
    "field_name",
    [
        "state_id",
        "data_root_id",
        "created_at",
    ],
)
def test_data_root_marker_rejects_empty_required_fields(
    field_name: str,
) -> None:
    values = {
        "state_id": "state-test-001",
        "data_root_id": "data-test-001",
        "environment": Environment.TEST,
        "created_at": "2026-09-12T14:00:00+09:00",
    }

    values[field_name] = ""

    with pytest.raises(ValueError):
        DataRootMarker(**values)