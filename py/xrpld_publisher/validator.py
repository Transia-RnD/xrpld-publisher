#!/usr/bin/env python
# coding: utf-8

import os
from typing import Dict, Any, List  # noqa: F401
import binascii
import base64

from xrpld_publisher.utils import (
    read_json,
    read_txt,
    write_json,
    write_file,
    encode_blob,
)
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

from xrpl.core.addresscodec.codec import _encode, _decode
from xrpl.core.addresscodec import encode_node_public_key, decode_node_public_key
from xrpl.core.binarycodec import encode
from xrpl.core.keypairs import sign as _sign, generate_seed, derive_keypair
from xrpl.constants import CryptoAlgorithm

DER_PRIVATE_KEY_PREFIX = bytes.fromhex("302E020100300506032B657004220420")
DER_PUBLIC_KEY_PREFIX = bytes.fromhex("302A300506032B6570032100")
VALIDATOR_HEX_PREFIX_ED25519 = "ED"


class KeystoreInterface:
    def __init__(
        self,
        domain=None,
        key_type="ed25519",
        manifest=None,
        public_key="",
        revoked=False,
        secret_key="",
        token_sequence=0,
    ):
        self.domain = domain
        self.key_type = key_type
        self.manifest = manifest
        self.public_key = public_key
        self.revoked = revoked
        self.secret_key = secret_key
        self.token_sequence = token_sequence

    def to_dict(self):
        return {
            "domain": self.domain,
            "key_type": self.key_type,
            "manifest": self.manifest,
            "public_key": self.public_key,
            "revoked": self.revoked,
            "secret_key": self.secret_key,
            "token_sequence": self.token_sequence,
        }


class ManifestInterface:
    def __init__(
        self,
        Sequence,
        PublicKey,
        SigningPubKey,
        Domain=None,
        SigningPrivateKey="",
        MasterPrivateKey="",
    ):
        self.Sequence = Sequence
        self.PublicKey = PublicKey
        self.SigningPubKey = SigningPubKey
        self.Domain = Domain
        self.SigningPrivateKey = SigningPrivateKey
        self.MasterPrivateKey = MasterPrivateKey


class ManifestResponse:
    def __init__(self, base64="", xrpl=""):
        self.base64 = base64
        self.xrpl = xrpl


def generate_keystore() -> KeystoreInterface:
    private_key = ed25519.Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    public_key_hex = (
        VALIDATOR_HEX_PREFIX_ED25519
        + public_bytes[len(DER_PUBLIC_KEY_PREFIX) :].hex().upper()
    )

    secret_key = _encode(
        private_bytes[len(DER_PRIVATE_KEY_PREFIX) :],
        [0x20],
        32,
    )

    return KeystoreInterface(
        key_type="ed25519",
        secret_key=secret_key,
        public_key=encode_node_public_key(bytes.fromhex(public_key_hex)),
        revoked=False,
        token_sequence=0,
    )


def sign(message, secret) -> bytes:
    # Convert message to bytes if it's a string
    if isinstance(message, str):
        message = message.encode("utf-8").upper()

    # Try to decode the secret, assuming it's base64 encoded
    try:
        decoded = _decode(secret, bytes([0x20]))
        secret = VALIDATOR_HEX_PREFIX_ED25519 + decoded.hex()
    except Exception as err:
        # ignore
        pass

    return _sign(message, secret).upper()


def generate_manifest(manifest):
    verify_fields = [b"MAN\x00"]

    # Sequence (soeREQUIRED)
    sequence_buffer = (0x24).to_bytes(1, byteorder="big") + manifest[
        "Sequence"
    ].to_bytes(4, byteorder="big")
    verify_fields.append(sequence_buffer)

    # PublicKey (soeREQUIRED)
    public_key_buffer = (
        (0x71).to_bytes(1, byteorder="big")
        + len(bytes.fromhex(manifest["PublicKey"])).to_bytes(1, byteorder="big")
        + bytes.fromhex(manifest["PublicKey"])
    )
    verify_fields.append(public_key_buffer)

    # SigningPubKey (soeOPTIONAL)
    signing_pub_key_buffer = (
        (0x73).to_bytes(1, byteorder="big")
        + len(bytes.fromhex(manifest["SigningPubKey"])).to_bytes(1, byteorder="big")
        + bytes.fromhex(manifest["SigningPubKey"])
    )
    verify_fields.append(signing_pub_key_buffer)

    # Domain (soeOPTIONAL)
    if "Domain" in manifest:
        domain_length = len(manifest["Domain"]) // 2
        domain_buffer = bytearray([0x77, domain_length])
        domain_buffer += bytes.fromhex(manifest["Domain"])
        verify_fields.append(domain_buffer)

    verify_data = b"".join(verify_fields)

    # Signature (soeOPTIONAL)
    ephemeral_signature = sign(verify_data, manifest["SigningPrivateKey"])

    # MasterSignature (soeREQUIRED)
    master_signature = sign(verify_data, manifest["MasterPrivateKey"])

    json_dict = {
        "Sequence": manifest["Sequence"],
        "PublicKey": manifest["PublicKey"],
        "SigningPubKey": manifest["SigningPubKey"],
        "Signature": ephemeral_signature,
        "MasterSignature": master_signature,
    }
    if "Domain" in manifest:
        json_dict["Domain"] = manifest["Domain"]

    manifest_buffer = bytes.fromhex(encode(json_dict))

    return {
        "base64": base64.b64encode(manifest_buffer).decode("utf-8"),
        "xrpl": manifest_buffer.hex().upper(),
    }


class ValidatorClient(object):
    name: str = ""  # node1 | node2 | signer
    keystore_path: str = ""
    bin_path: str = ""
    key_path: str = ""

    def __init__(cls, name: str) -> None:
        cls.name = name
        cls.keystore_path = "keystore"
        cls.key_path = os.path.join(cls.keystore_path, f"{cls.name}/key.json")
        os.makedirs(cls.keystore_path, exist_ok=True)

    def get_keys(cls):
        try:
            return read_json(cls.key_path)
        except Exception as e:
            print(e)
            return None

    def create_keys(cls) -> str:
        os.makedirs(os.path.join(cls.keystore_path, cls.name), exist_ok=True)
        write_json(generate_keystore().to_dict(), cls.key_path)

    def set_domain(cls, domain: str) -> None:
        keys = cls.get_keys()
        keys["domain"] = domain
        keys["token_sequence"] += 1

        attestation = sign(
            f"[domain-attestation-blob:{keys['domain']}:{keys['public_key']}]",
            keys["secret_key"],
        )
        name_path = os.path.join(cls.keystore_path, cls.name)
        write_file(attestation, f"{name_path}/attestation.txt")
        write_json(keys, cls.key_path)

    def create_token(cls) -> str:
        keys = cls.get_keys()
        seed = generate_seed(algorithm=CryptoAlgorithm.SECP256K1)
        keypair = derive_keypair(seed)
        keys["token_sequence"] += 1

        manifest = generate_manifest(
            {
                "Sequence": keys["token_sequence"],
                "Domain": keys["domain"].encode("utf-8").hex(),
                "PublicKey": decode_node_public_key(keys["public_key"]).hex().upper(),
                "SigningPubKey": keypair[0],
                "SigningPrivateKey": keypair[1],
                "MasterPrivateKey": keys["secret_key"],
            }
        )
        keys["manifest"] = manifest["xrpl"]

        token = encode_blob(
            {
                "validation_secret_key": keypair[1][2:],
                "manifest": manifest["base64"],
            }
        )

        token_path = os.path.join(cls.keystore_path, f"{cls.name}/token.txt")
        write_file(token.decode("utf-8"), token_path)
        manifest_path = os.path.join(cls.keystore_path, f"{cls.name}/manifest.txt")
        write_file(manifest["base64"], manifest_path)
        write_json(keys, cls.key_path)

    def read_token(cls) -> str:
        token_path = os.path.join(cls.keystore_path, f"{cls.name}/token.txt")
        token = read_txt(token_path)
        return token[0]

    def read_manifest(cls) -> str:
        manifest_path = os.path.join(cls.keystore_path, f"{cls.name}/manifest.txt")
        manifest = read_txt(manifest_path)
        return manifest[0]
