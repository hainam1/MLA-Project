"""Runtime utilities shared by CLI entry points."""

from .hardware import TorchDeviceStatus, inspect_torch_device, select_device
from .logging import configure_logging

__all__ = [
    "TorchDeviceStatus",
    "configure_logging",
    "inspect_torch_device",
    "select_device",
]
