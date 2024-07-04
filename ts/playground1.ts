import { decodeNodePublic } from 'xrpl'
import { generateManifest } from './dist/npm/src'

const nodeAddr = 'nHUZJhS1KShEGH3MjiwDjxWZJzZo3yKayfxj4Ru1jL2c99YdtPFM'
const secretKey = 'paRSac7hxxQHxWohWXFq3vxkAa62wgsaLG4FwYwZTfrsWvzcybK'
console.log(decodeNodePublic(nodeAddr).toString('hex').toUpperCase())

const manifest = generateManifest({
  Sequence: 3,
  Domain: 'domain.com',
  PublicKey:
    'ED9E9EAE342CD3B844390D588F13B50826AD9ACA2E074A5BEEB12D85506F68EAE9',
  SigningPubKey: '',
  SigningPrivateKey: secretKey,
  MasterPrivateKey: '',
})

console.log(manifest)
