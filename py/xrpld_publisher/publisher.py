#!/usr/bin/env python
# coding: utf-8

import base64
import os
from typing import Dict, Any, List  # noqa: F401
import subprocess
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from xrpl.core.binarycodec.main import decode
from xrpl.core.keypairs import generate_seed, derive_keypair
from xrpld_publisher.utils import (
    encode_blob,
    read_json,
    write_json,
    read_txt,
    write_file,
    from_date_to_effective,
    from_days_to_expiration,
)
from xrpld_publisher.models import Validator, VL, Blob
from xrpld_publisher.validator import sign, generate_manifest


class PublisherClient(object):
    vl_path: str = ""
    vl: VL = None
    keystore_path: str = ""
    key_path: str = ""
    eph_path: str = ""

    def __init__(cls, vl_path: str = None) -> None:
        cls.keystore_path = "keystore"
        cls.key_path = os.path.join(cls.keystore_path, "vl/key.json")
        cls.eph_path = os.path.join(cls.keystore_path, "vl/eph.json")
        os.makedirs(cls.keystore_path, exist_ok=True)

        if vl_path:
            try:
                cls.vl_path = vl_path
                vl_dict: Dict[str, Any] = read_json(vl_path)
                cls.vl = VL.from_json(vl_dict)
                cls.vl.blob.sequence += 1
                return None
            except Exception as e:
                raise e

        cls.vl_path: str = "vl.json"
        cls.vl = VL()
        cls.vl.manifest = cls.read_manifest()
        cls.vl.blob = Blob()
        cls.vl.blob.sequence = 1
        pass

    def get_keys(cls):
        try:
            return read_json(cls.key_path)
        except Exception as e:
            return None

    def get_ephkeys(cls):
        try:
            return read_json(cls.eph_path)
        except Exception as e:
            return None

    def read_manifest(cls) -> str:
        try:
            manifest_path = os.path.join(cls.keystore_path, "vl/manifest.txt")
            manifest = read_txt(manifest_path)
            return manifest[0]
        except Exception as e:
            return None

    def create_keys(cls) -> str:
        os.makedirs(os.path.join(cls.keystore_path, "vl"), exist_ok=True)
        # Eph Keys
        eph_seed = generate_seed()
        eph_keypair = derive_keypair(eph_seed)
        write_json(
            {
                "public_key": eph_keypair[0],
                "private_key": eph_keypair[1],
            },
            cls.eph_path,
        )

        # VL Keys
        seed = generate_seed()
        keypair = derive_keypair(seed)

        write_json(
            {
                "public_key": keypair[0],
                "private_key": keypair[1],
            },
            cls.key_path,
        )

        manifest = generate_manifest(
            {
                "Sequence": 1,
                "PublicKey": keypair[0],
                "SigningPubKey": eph_keypair[0],
                "SigningPrivateKey": eph_keypair[1],
                "MasterPrivateKey": keypair[1],
            }
        )
        manifest_path = os.path.join(cls.keystore_path, "vl/manifest.txt")
        write_file(manifest["base64"], manifest_path)
        cls.vl_path: str = "vl.json"
        cls.vl = VL()
        cls.vl.manifest = manifest
        cls.vl.blob = Blob()
        cls.vl.blob.sequence = 1

    def add_validator(cls, manifest: str):
        if not cls.vl:
            raise ValueError("invalid vl")

        if not cls.vl.blob:
            raise ValueError("invalid blob")

        encoded = base64.b64decode(manifest).hex()
        decoded: Dict[str, Any] = decode(encoded)
        public_key: str = decoded["PublicKey"].upper()
        # Check if the validator is already in the list
        for validator in cls.vl.blob.validators:
            if validator.pk == public_key:
                raise ValueError("Validator is already in the list")

        new_validator: Validator = Validator()
        new_validator.pk = public_key
        new_validator.manifest = manifest
        cls.vl.blob.validators.append(new_validator)

    def remove_validator(cls, public_key: str):
        if not cls.vl:
            raise ValueError("invalid VL")

        if not cls.vl.blob:
            raise ValueError("invalid Blob")

        validators = cls.vl.blob.validators
        # Find the validator with the specified public key
        for validator in validators:
            if validator.pk == public_key:
                validators.remove(validator)
                break
        else:
            raise ValueError("validator not found")

        cls.vl.blob.validators = validators

    def sign_unl(cls, path: str, effective: str = None, expiration: int = None) -> None:
        if not cls.vl:
            raise ValueError("invalid vl")

        if len(cls.vl.blob.validators) == 0:
            raise ValueError("must have at least 1 validator")

        if not effective:
            effective: int = from_date_to_effective("01/01/2000")

        if not expiration:
            expiration: int = from_days_to_expiration(time.time(), 30)

        validators: List[str] = [
            {"manfest": v.manifest, "validation_public_key": v.pk}
            for v in cls.vl.blob.validators
        ]

        blob = encode_blob(
            {
                "sequence": cls.vl.blob.sequence,
                "effective": effective,
                "expiration": expiration,
                "validators": validators,
            }
        )

        manifest = cls.read_manifest()
        keys = cls.get_keys()
        eph_keys = cls.get_ephkeys()
        signature = sign(blob, eph_keys["private_key"])
        write_json(
            {
                "blob": blob.decode("utf-8"),
                "manifest": manifest,
                "signature": signature,
                "public_key": keys["public_key"],
                "version": 1,
            },
            path,
        )
