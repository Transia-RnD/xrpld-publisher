# XRPLD Publisher

The XRPLD Publisher is a Python library that provides functionality for managing and publishing XRPL validator lists (VLs). It includes a client for interacting with the XRPLD Publisher API and a client for managing validator keys and generating VL manifests.

## Installation

To install the XRPLD Publisher library, run the following command:

```
pip install xrpld-publisher
```

## Usage

### Download the First we need to download the binary builds for both the `validators-list` and `validator-keys`.
 builds

First we need to download the binary builds for both the `validators-list` and `validator-keys`.

Download the build folder that corresponds to your operating system.

> If you don't see your operating system you will need to build them yourself.

Save them into the root of your project under the `bin` directory.

### Generate Publisher List Keys

When first setting up a validator list, use the `validator-list` tool to
generate the publisher key pair:

```
  $ ./bin/validator-list
```

1. Enter `1` for `Create validator list publisher keys`
2. Enter a name for the keys.

Sample output:
```
  Select a name for this credential set: my-publisher-keys

  Publisher keys stored in privkeys.txt and pubkeys.txt
  Ephemeral keys stored in my-publisher-keys/
```

Keep the key files in a secure but recoverable location, such as an encrypted
USB flash drive. Do not modify its contents.

Use ephkey1.txt key and manifest to generates validator lists.

* Add the hex-encoded public key from your [pubkeys.txt file](#validator-list-publisher-keys) to `[validator_list_keys]`


### Validator Client

The `ValidatorClient` class provides methods for managing validator keys and generating VL manifests.

```python
from xrpld_publisher.validator import ValidatorClient

# Create a new instance of the ValidatorClient
client = ValidatorClient("node1")

# Generate validator keys
keys = client.create_keys()

# Set the domain for the validator
client.set_domain("example.com")

# Generate a token for the validator
token = client.create_token()

# Generate a VL manifest for the validator
manifest = client.create_manifest()

# Read the VL manifest
manifest = client.read_manifest()
```

The validator keys and generated files are stored in the `keystore` directory. For example, the keys for `node1` would be stored in `keystore/node1/key.json`, the token would be stored in `keystore/node1/token.txt`, and the manifest would be stored in `keystore/node1/manifest.txt`.

### Publisher Client

The `PublisherClient` class provides methods for managing and publishing VLs.

```python
from xrpld_publisher.publisher import PublisherClient

# Create a new instance of the PublisherClient
client = PublisherClient(manifest="manifest")

# Create an existing instance of the PublisherClient
client = PublisherClient(vl_path="my/dir/vl.json")

# Add a validator to the VL
client.add_validator("manifest")

# Remove a validator from the VL
client.remove_validator("public_key")

# Sign the VL with a private key and generate a signed VL
effective: int = from_date_to_effective("01/01/2022")
expiration: int = from_days_to_expiration(time.time(), 30)
signed_vl = client.sign_unl("private_key", "myvl.json", effective=effective, expiration=expiration)
```

The VL file is stored in the `vl_path` directory.

## Models

The XRPLD Publisher library includes the following models:

- `Validator`: Represents a validator in a VL.
- `Blob`: Represents a blob in a VL.
- `VL`: Represents a VL.

These models can be used to create and manipulate VLs programmatically.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
