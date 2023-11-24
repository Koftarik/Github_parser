from dataclasses import dataclass


@dataclass
class Config:
    github_access_token: str = 'your token here'
    db_uri: str = 'sqlite:///data.db'
