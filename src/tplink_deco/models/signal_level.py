from dataclasses import dataclass


@dataclass(frozen=True)
class SignalLevel:
    band2_4: str
    band5: str
    band6: str

    @classmethod
    def from_api(cls, data: dict[str, str]) -> "SignalLevel":
        return cls(
            band2_4=data.get("band2_4", "0"),
            band5=data.get("band5", "0"),
            band6=data.get("band6", "0"),
        )
