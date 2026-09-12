from dataclasses import dataclass

from argus.runtime.environment import Environment


@dataclass(frozen=True)
class DataRootMarker:
    state_id: str
    data_root_id: str
    environment: Environment
    created_at: str

    def __post_init__(self) -> None:
        if not self.state_id:
            raise ValueError("state_id must not be empty")

        if not self.data_root_id:
            raise ValueError("data_root_id must not be empty")

        if not self.created_at:
            raise ValueError("created_at must not be empty")