# XRPLD Publisher

The XRPLD Publisher is a JavaScript/TypeScript library that provides functionality for managing and publishing XRPL validator lists (VLs). It includes a client for interacting with the XRPLD Publisher API and a client for managing validator keys and generating VL manifests.

## Installation

To install the XRPLD Publisher library, run the following command:

```
yarn add @transia/xrpld-publisher
```

## Usage

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

// Read the token
const manifest = client.readToken()

// Read the manifest
const manifest = client.readManifest()
```

The validator keys and generated files are stored in the `keystore` directory. For example, the keys for `node1` would be stored in `keystore/node1/key.json`, the token would be stored in `keystore/node1/token.txt`, and the manifest would be stored in `keystore/node1/manifest.txt`.

### Publisher Client

The `PublisherClient` class provides methods for managing and publishing VLs.

```typescript
import { PublisherClient } from '@transia/xrpld-publisher'

// Create a new instance of the PublisherClient
const client = PublisherClient()
client.createKeys()

// Create an existing instance of the PublisherClient
const client = PublisherClient(vl_path="my/dir/vl.json")

// Add a validator to the VL
client.addValidator("manifest")

// Remove a validator from the VL
client.removeValidator("public_key")

// Sign the VL with a private key and generate a signed VL
const effective: number = fromDateToEffective("01/01/2022")
const expiration: number = fromDaysToExpiration(effective, 30) // Days
client.signUnl("myvl.json", { effective, expiration })
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
