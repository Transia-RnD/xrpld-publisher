import { ValidatorClient } from '../../dist/npm/src'

describe('xrpld-publisher - Validator', () => {
  it('init validator', async () => {
    const client = new ValidatorClient('test-v')
    expect(client.keystorePath).toBe(
      '/Users/denisangell/projects/xrpl-labs/xrpld-publisher/ts/keystore'
    )
    expect(client.keyPath).toBe(
      '/Users/denisangell/projects/xrpl-labs/xrpld-publisher/ts/keystore/test-v/key.json'
    )
  })
  it('get keys', async () => {
    const client = new ValidatorClient('test-v-get')
    expect(client.getKeys()).toBe(null)
  })
  it('create keys', async () => {
    const client = new ValidatorClient('test-create')
    await client.createKeys()
    const keys = client.getKeys()
    expect(keys.key_type).toBe('ed25519')
    expect(keys.public_key).not.toBeNull()
    expect(keys.revoked).toBe(false)
    expect(keys.secret_key).not.toBeNull()
    expect(keys.token_sequence).toBe(0)
  })
  it('set domain', async () => {
    const client = new ValidatorClient('test-v-domain')
    await client.createKeys()
    await client.setDomain('domain.com')
    const keys = client.getKeys()
    expect(keys.domain).toBe('domain.com')
    expect(keys.key_type).toBe('ed25519')
    expect(keys.manifest).not.toBeNull()
    expect(keys.public_key).not.toBeNull()
    expect(keys.revoked).toBe(false)
    expect(keys.secret_key).not.toBeNull()
    expect(keys.token_sequence).toBe(1)
  })
  it('create/read token', async () => {
    const client = new ValidatorClient('test-v-token')
    await client.createKeys()
    await client.setDomain('domain.com')
    await client.createToken()
    expect(await client.readToken()).not.toBeNull()
  })
  it('create/read manifest', async () => {
    const client = new ValidatorClient('test-v-manifest')
    await client.createKeys()
    await client.setDomain('domain.com')
    await client.createToken()
    expect(await client.readManifest()).not.toBeNull()
  })
})
