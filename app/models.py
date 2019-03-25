from dataclasses import dataclass


@dataclass
class User:
    oauth_token: str = None
    username: str = None
    profile_url: str = None
    repo_url: str = None

    @property
    def authorized(self):
        return self.oauth_token is not None

    @property
    def forked(self):
        return self.repo_url is not None

    def reset(self):
        self.oauth_token = self.username = self.profile_url = self.repo_url = None
