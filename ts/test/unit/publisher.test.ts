import {
  PublisherClient,
  fromDateToEffective,
  fromDaysToExpiration,
} from '../../dist/npm/src'

describe('xrpld-publisher - PublisherClient', () => {
  const vlPath = 'test/fixtures/test.json'

  it('init vl', async () => {
    const client = new PublisherClient(vlPath)
    expect(client.vl.blob.sequence).toBe(2)
    expect(client.vl.blob.validators.length).toBe(1)
  })
  it('init new vl', async () => {
    const client = new PublisherClient()
    await client.createKeys()
    expect(client.vl.blob.sequence).toBe(1)
    expect(client.vl.blob.validators.length).toBe(0)
  })
  it('add validator', async () => {
    const client = new PublisherClient(vlPath)
    expect(client.vl.blob.sequence).toBe(2)
    const addManifest =
      'JAAAAAFxIe3kW20uKHcjYwGFkZ7+Ax8FIorTwvHqmY8kvePtYG4nSHMhAjIn+/pQWK/OU9ln8Rux6wnQGY1yMFeaGR5gEcFSGxa1dkYwRAIgSAGa6gWCa2C9XxIMSoAB1qCZjjJMXGpl5Tb+81U5RDwCIG3GQHXPUjFkTMwEcuM8G6dwcWzEfB1nYa5MqxFAhOXscBJApcamLcUBNxmABeKigy+ZYTYLqMKuGtV9HgjXKA5oI9CNH0xA6R52NchP3rZyXWOWS0tan25o0rwQBNIY78k6Cg=='
    client.addValidator(addManifest)
    expect(client.vl.blob.validators.length).toBe(2)
    expect(client.vl.blob.validators[1].pk).toBe(
      'EDE45B6D2E287723630185919EFE031F05228AD3C2F1EA998F24BDE3ED606E2748'
    )
    expect(client.vl.blob.validators[1].manifest).toBe(addManifest)
  })
  it('removel validator', async () => {
    const client = new PublisherClient(vlPath)
    expect(client.vl.blob.sequence).toBe(2)
    const removePk =
      'EDA164F4B36C2D730462D5F762BFA2808AA5092ABCECEBB27089525D1D054BE33B'
    client.removeValidator(removePk)
    expect(client.vl.blob.validators.length).toBe(0)
  })
  it('sign vl', async () => {
    const client = new PublisherClient(vlPath)
    expect(client.vl.blob.sequence).toBe(2)
    const addManifest =
      'JAAAAAFxIe3kW20uKHcjYwGFkZ7+Ax8FIorTwvHqmY8kvePtYG4nSHMhAjIn+/pQWK/OU9ln8Rux6wnQGY1yMFeaGR5gEcFSGxa1dkYwRAIgSAGa6gWCa2C9XxIMSoAB1qCZjjJMXGpl5Tb+81U5RDwCIG3GQHXPUjFkTMwEcuM8G6dwcWzEfB1nYa5MqxFAhOXscBJApcamLcUBNxmABeKigy+ZYTYLqMKuGtV9HgjXKA5oI9CNH0xA6R52NchP3rZyXWOWS0tan25o0rwQBNIY78k6Cg=='
    client.addValidator(addManifest)
    const effective: number = fromDateToEffective('01/01/2022')
    const expiration: number = fromDaysToExpiration(effective, 30) // Days
    client.signUnl('myvl.json', { effective, expiration })
    expect(client.vl.blob.validators.length).toBe(2)
  })
})
