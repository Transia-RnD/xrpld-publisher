#!/usr/bin/env python
# coding: utf-8

import time
import logging
from typing import Dict, Any, List  # noqa: F401

from testing_config import BaseTestConfig

from xrpl.core.addresscodec import decode_node_public_key

from xrpld_publisher.validator import (
    ValidatorClient,
)
from xrpld_publisher.utils import decode_blob

logger = logging.getLogger("app")


class TestValidator(BaseTestConfig):
    def test_init(cls):
        client: ValidatorClient = ValidatorClient(name="test")
        cls.assertIsNotNone(client)
        cls.assertEqual(client.keystore_path, "keystore")
        cls.assertEqual(client.key_path, "keystore/test/key.json")

    def test_get_keys(cls):
        client: ValidatorClient = ValidatorClient(name="test-v-get")
        cls.assertEqual(client.get_keys(), None)

    def test_create_keys(cls):
        client: ValidatorClient = ValidatorClient(name="test-v-create")
        client.create_keys()
        keys = client.get_keys()
        cls.assertEqual(keys["key_type"], "ed25519")
        cls.assertIsNotNone(keys["public_key"])
        cls.assertEqual(keys["revoked"], False)
        cls.assertIsNotNone(keys["secret_key"])
        cls.assertEqual(keys["token_sequence"], 0)

    def test_set_domain(cls):
        client: ValidatorClient = ValidatorClient(name="test-v-domain")
        client.create_keys()
        client.set_domain("domain.com")
        keys = client.get_keys()
        cls.assertEqual(keys["domain"], "domain.com")
        cls.assertEqual(keys["key_type"], "ed25519")
        cls.assertIsNotNone(keys["public_key"])
        cls.assertEqual(keys["revoked"], False)
        cls.assertIsNotNone(keys["secret_key"])
        cls.assertEqual(keys["token_sequence"], 1)

    def test_create_read_token(cls):
        client: ValidatorClient = ValidatorClient(name="test-v-token")
        client.create_keys()
        client.set_domain("domain.com")
        client.create_token()
        token = client.read_token()
        cls.assertIsNotNone(token)

    def test_create_read_manifest(cls):
        client: ValidatorClient = ValidatorClient(name="test-v-manifest")
        client.create_keys()
        client.set_domain("domain.com")
        client.create_token()
        manifest = client.read_manifest()
        cls.assertIsNotNone(manifest)
