from __future__ import annotations

from locust import HttpUser, between, task

from load_tests.config import get_config
from load_tests.scenarios import (
    DIAMOND_PAGES,
    LEVEL3_PAGES,
    LEVEL4_PAGES,
    SILVER_PAGES,
    VISITOR_PAGES,
    login,
    post_cvc_progress,
    post_english_foundation_progress,
    post_sounds_progress,
    run_steps,
)
from load_tests.users import credentials_for


CONFIG = get_config()


class BaseAbczUser(HttpUser):
    host = CONFIG.base_url
    wait_time = between(1, 4)
    abstract = True


class VisitorUser(BaseAbczUser):
    weight = 30

    @task
    def browse_public_pages(self):
        run_steps(self.client, VISITOR_PAGES)


class SilverUser(BaseAbczUser):
    weight = 30

    def on_start(self):
        username, password = credentials_for("silver")
        login(self.client, username, password)

    @task(4)
    def browse_sounds(self):
        run_steps(self.client, SILVER_PAGES)

    @task(1)
    def save_sounds_progress(self):
        post_sounds_progress(self.client)


class LevelThreeUser(BaseAbczUser):
    weight = 15

    def on_start(self):
        username, password = credentials_for("level3")
        login(self.client, username, password)

    @task(4)
    def browse_cvc(self):
        run_steps(self.client, LEVEL3_PAGES)

    @task(1)
    def save_cvc_progress(self):
        post_cvc_progress(self.client)


class LevelFourUser(BaseAbczUser):
    weight = 15

    def on_start(self):
        username, password = credentials_for("level4")
        login(self.client, username, password)

    @task(4)
    def browse_level_four(self):
        run_steps(self.client, LEVEL4_PAGES)

    @task(1)
    def save_english_foundation_progress(self):
        post_english_foundation_progress(self.client)


class DiamondUser(BaseAbczUser):
    weight = 10

    def on_start(self):
        username, password = credentials_for("diamond")
        login(self.client, username, password)

    @task(5)
    def browse_full_path(self):
        run_steps(self.client, DIAMOND_PAGES)

    @task(1)
    def save_mixed_progress(self):
        post_sounds_progress(self.client)
        post_cvc_progress(self.client)
        post_english_foundation_progress(self.client)
