"""
Digital Body Architecture for Chappy

A containerized body system that gives Chappy sensory inputs, motor outputs,
and nervous system feedback loops. This creates a complete embodied AI system.

Architecture:
- SENSORY: Vision, Audio, Text, System monitoring
- MOTOR: Speech, Display, Actions, Hardware control
- NERVOUS: Proprioception, Pain/pleasure, Homeostasis, Reflexes
- CONTAINERS: Podman pod with specialized containers for each system
"""

from .sensory import SensorySystem
from .motor import MotorSystem
from .nervous import NervousSystem
from .containers import ContainerManager

__all__ = ['SensorySystem', 'MotorSystem', 'NervousSystem', 'ContainerManager']