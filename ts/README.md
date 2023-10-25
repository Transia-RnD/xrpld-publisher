# XRPLD Publisher

The XRPLD Publisher is a JavaScript/TypeScript library that provides functionality for managing and publishing XRPL validator lists (VLs). It includes a client for interacting with the XRPLD Publisher API and a client for managing validator keys and generating VL manifests.

## Installation

To install the XRPLD Publisher library, run the following command:

```
yarn add @transia/xrpld-publisher
```

## Usage

### Download the binary builds

First we need to download the binary builds for both the `validators-list` and `validator-keys`.

Download the build folder that corresponds to your operating system from [releases].(https://github.com/Transia-RnD/xrpld-publisher/releases)

> If you don't see your operating system you will need to build them yourself for [source](https://github.com/Transia-RnD/validator-list). You can use this [guide](https://github.com/Transia-RnD/validator-list/blob/main/doc/validator-list-guide.md)

Save them into the root of your project under the `bin` directory.

### Generate Publisher List Keys

When first setting up a validator list, use the `validator-list` tool to
generate the publisher key pair:

```
  $ ./bin/validator-list wizard
```

1. Enter `1` for `Create validator list publisher keys`
2. Enter a name for the keys.

Sample output:
```
  Select a name for this credential set: keystore

  Publisher keys stored in privkeys.txt and pubkeys.txt
  Ephemeral keys stored in keystore/
```

Keep the key files in a secure but recoverable location, such as an encrypted
USB flash drive. Do not modify its contents.

Use ephkey1.txt key and manifest to generates validator lists.

* Add the hex-encoded public key from your [pubkeys.txt file](#validator-list-publisher-keys) to `[validator_list_keys]`

### Validator Client

The `ValidatorClient` class provides methods for managing validator keys and generating VL manifests.

```typescript
import { ValidatorClient } from '@transia/xrpld-publisher'

// Create a new instance of the ValidatorClient
const client = ValidatorClient("node1")

// Generate validator keys
client.createKeys()

// Set the domain for the validator
client.setDomain("example.com")

// Generate a token for the validator
client.createToken()

// Generate a VL manifest for the validator
client.createManifest()

// Read the VL manifest
const manifest = client.readManifest()
```

The validator keys and generated files are stored in the `keystore` directory. For example, the keys for `node1` would be stored in `keystore/node1/key.json`, the token would be stored in `keystore/node1/token.txt`, and the manifest would be stored in `keystore/node1/manifest.txt`.

### Publisher Client

The `PublisherClient` class provides methods for managing and publishing VLs.

```typescript
import { PublisherClient } from '@transia/xrpld-publisher'

// Create a new instance of the PublisherClient
const client = PublisherClient(manifest="manifest")

// Create an existing instance of the PublisherClient
const client = PublisherClient(vl_path="my/dir/vl.json")

// Add a validator to the VL
client.addValidator("manifest")

// Remove a validator from the VL
client.removeValidator("public_key")

// Sign the VL with a private key and generate a signed VL
const effective: number = fromDateToEffective("01/01/2022")
const expiration: number = fromDaysToExpiration(Date.now(), 30)
client.signUnl("private_key", "myvl.json", { effective, expiration })
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
