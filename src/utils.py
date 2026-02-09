import yaml
from pathlib import Path
from typing import Dict, Any
from .models import UserData, PrinterProfiles, PrinterProfile

CONFIG_DIR = Path("config")

def load_user_data(path: Path = CONFIG_DIR / "user_data.yaml") -> UserData:
    """Loads user data from YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"User data file not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return UserData(**data)

def load_printer_profiles(path: Path = CONFIG_DIR / "printer_profiles.yaml") -> PrinterProfiles:
    """Loads printer profiles from YAML file."""
    if not path.exists():
        raise FileNotFoundError(f"Printer profiles file not found at {path}")
    
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    return PrinterProfiles(**data)

def get_profile(name: str = "default_a4") -> PrinterProfile:
    """Helper to get a specific printer profile."""
    profiles = load_printer_profiles()
    if name not in profiles.profiles:
        raise ValueError(f"Profile '{name}' not found. Available: {list(profiles.profiles.keys())}")
    return profiles.profiles[name]
