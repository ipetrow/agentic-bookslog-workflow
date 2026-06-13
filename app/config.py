from dataclasses import dataclass
import os
import sys
import logging

@dataclass(frozen=True)
class Settings:
    database_path: str

def get_settings() -> Settings:
    return Settings(
        database_path=os.environ["DATABASE_PATH"]
    ) 