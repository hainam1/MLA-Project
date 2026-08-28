"""Validate actual accelerator execution, not only CUDA discovery."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import torch


@dataclass(frozen=True)
class TorchDeviceStatus:
    cuda_reported: bool
    cuda_usable: bool
    selected_device: str
    device_name: str | None = None
    compute_capability: str | None = None
    reason: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


def inspect_torch_device() -> TorchDeviceStatus:
    reported = torch.cuda.is_available()
    if not reported:
        return TorchDeviceStatus(False, False, "cpu", reason="CUDA is not reported")
    try:
        name = torch.cuda.get_device_name(0)
        major, minor = torch.cuda.get_device_capability(0)
        tensor = torch.zeros(1, device="cuda")
        _ = tensor + 1
        torch.cuda.synchronize()
        return TorchDeviceStatus(
            True,
            True,
            "cuda",
            device_name=name,
            compute_capability=f"sm_{major}{minor}",
        )
    except (RuntimeError, AssertionError) as exc:
        return TorchDeviceStatus(
            True,
            False,
            "cpu",
            device_name=torch.cuda.get_device_name(0),
            reason=str(exc).splitlines()[0],
        )


def select_device(requested: str = "auto") -> torch.device:
    if requested not in {"auto", "cpu", "cuda"}:
        raise ValueError("device must be one of: auto, cpu, cuda")
    if requested == "cpu":
        return torch.device("cpu")
    status = inspect_torch_device()
    if requested == "cuda" and not status.cuda_usable:
        raise RuntimeError(status.reason or "CUDA is unavailable")
    return torch.device("cuda" if status.cuda_usable else "cpu")
