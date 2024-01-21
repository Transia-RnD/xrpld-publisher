#!/usr/bin/env python
# coding: utf-8

import time
import logging
from typing import Dict, Any, List  # noqa: F401

from testing_config import BaseTestConfig
from xrpld_publisher.publisher import (
    PublisherClient,
)
from xrpld_publisher.utils import from_days_to_expiration, from_date_to_effective

logger = logging.getLogger("app")


class TestPublisher(BaseTestConfig):
    vl_path: str = "tests/fixtures/test.json"

    def test_init(cls):
        client: PublisherClient = PublisherClient(vl_path=cls.vl_path)
        cls.assertIsNotNone(client.vl)
        cls.assertEqual(client.vl.blob.sequence, 2)
        cls.assertEqual(len(client.vl.blob.validators), 1)

    # def test_init_new_vl(cls):
    #     client: PublisherClient = PublisherClient()
    #     client.create_keys()
    #     cls.assertIsNotNone(client.vl)
    #     cls.assertEqual(client.vl.blob.sequence, 1)
    #     cls.assertEqual(len(client.vl.blob.validators), 0)

    # def test_add_validator(cls):
    #     client: PublisherClient = PublisherClient(vl_path=cls.vl_path)
    #     cls.assertEqual(client.vl.blob.sequence, 2)
    #     add_manifest: str = "JAAAAAFxIe3kW20uKHcjYwGFkZ7+Ax8FIorTwvHqmY8kvePtYG4nSHMhAjIn+/pQWK/OU9ln8Rux6wnQGY1yMFeaGR5gEcFSGxa1dkYwRAIgSAGa6gWCa2C9XxIMSoAB1qCZjjJMXGpl5Tb+81U5RDwCIG3GQHXPUjFkTMwEcuM8G6dwcWzEfB1nYa5MqxFAhOXscBJApcamLcUBNxmABeKigy+ZYTYLqMKuGtV9HgjXKA5oI9CNH0xA6R52NchP3rZyXWOWS0tan25o0rwQBNIY78k6Cg=="
    #     client.add_validator(add_manifest)
    #     cls.assertEqual(len(client.vl.blob.validators), 2)
    #     cls.assertEqual(
    #         client.vl.blob.validators[1].validation_public_key,
    #         "EDE45B6D2E287723630185919EFE031F05228AD3C2F1EA998F24BDE3ED606E2748",
    #     )
    #     cls.assertEqual(
    #         client.vl.blob.validators[1].manifest,
    #         add_manifest,
    #     )

    # def test_remove_validator(cls):
    #     client: PublisherClient = PublisherClient(vl_path=cls.vl_path)
    #     cls.assertEqual(client.vl.blob.sequence, 2)
    #     remove_pk: str = (
    #         "EDA164F4B36C2D730462D5F762BFA2808AA5092ABCECEBB27089525D1D054BE33B"
    #     )
    #     client.remove_validator(remove_pk)
    #     cls.assertEqual(len(client.vl.blob.validators), 0)

    def test_sign_vl(cls):
        client: PublisherClient = PublisherClient(vl_path=cls.vl_path)
        cls.assertEqual(client.vl.blob.sequence, 2)
        add_manifest: str = "JAAAAAFxIe3kW20uKHcjYwGFkZ7+Ax8FIorTwvHqmY8kvePtYG4nSHMhAjIn+/pQWK/OU9ln8Rux6wnQGY1yMFeaGR5gEcFSGxa1dkYwRAIgSAGa6gWCa2C9XxIMSoAB1qCZjjJMXGpl5Tb+81U5RDwCIG3GQHXPUjFkTMwEcuM8G6dwcWzEfB1nYa5MqxFAhOXscBJApcamLcUBNxmABeKigy+ZYTYLqMKuGtV9HgjXKA5oI9CNH0xA6R52NchP3rZyXWOWS0tan25o0rwQBNIY78k6Cg=="
        client.add_validator(add_manifest)
        effective: int = from_date_to_effective("01/01/2024")
        expiration: int = from_days_to_expiration(effective, 30)
        client.sign_unl("myvl.json", effective=effective, expiration=expiration)
        cls.assertEqual(len(client.vl.blob.validators), 2)
