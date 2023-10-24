import {
  PublisherClient,
  downloadUNL,
  fromDaysToExpiration,
} from '@transia/xrpld-publisher'

export async function main(): Promise<void> {
  try {
    const unlUrl = 'https://vl.test.xahauexplorer.com/'
    const manifest =
      'JAAAAAFxIe101ANsZZGkvfnFTO+jm5lqXc5fhtEf2hh0SBzp1aHNwXMh7TN9+b62cZqTngaFYU5tbGpYHC8oYuI3G3vwj9OW2Z9gdkAnUjfY5zOEkhq31tU4338jcyUpVA5/VTsANFce7unDo+JeVoEhfuOb/Y8WA3Diu9XzuOD4U/ikfgf9SZOlOGcBcBJAw44PLjH+HUtEnwX45lIRmo0x5aINFMvZsBpE9QteSDBXKwYzLdnSW4e1bs21o+IILJIiIKU/+1Uxx0FRpQbMDA=='
    const pk =
      'CC9E8B118E8E927DA82A66B9D931E1AB6309BA32F057F8B216600B347C552006'
    await downloadUNL(unlUrl)
    const addList: string[] = [
      'JAAAAAFxIe3kW20uKHcjYwGFkZ7+Ax8FIorTwvHqmY8kvePtYG4nSHMhAjIn+/pQWK/OU9ln8Rux6wnQGY1yMFeaGR5gEcFSGxa1dkYwRAIgSAGa6gWCa2C9XxIMSoAB1qCZjjJMXGpl5Tb+81U5RDwCIG3GQHXPUjFkTMwEcuM8G6dwcWzEfB1nYa5MqxFAhOXscBJApcamLcUBNxmABeKigy+ZYTYLqMKuGtV9HgjXKA5oI9CNH0xA6R52NchP3rZyXWOWS0tan25o0rwQBNIY78k6Cg==',
    ]
    const removeList: string[] = [
      'EDE8FA88589CF8825334609E97EC8BFA1F56FF95D9D75BBD29996416D41319BF20',
    ]
    const oldUNL = new PublisherClient('vl.json')
    const validators = oldUNL.vl.blob.validators
      .filter((validator) => !removeList.includes(validator.pk))
      .map((validator) => validator.manifest)
    const client = new PublisherClient(manifest)
    await Promise.all(
      addList
        .concat(validators)
        .map((manifest) => client.addValidator(manifest))
    )
    const expiration = fromDaysToExpiration(Date.now(), 365)
    client.signUnl(pk, 'myvl.json', { expiration })
  } catch (error) {
    console.error('An error occurred:', error)
  }
}

main()
