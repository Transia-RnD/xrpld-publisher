import * as fs from 'fs'
import { promises as fsPromises } from 'fs'
import path from 'path'
import 'dotenv/config'

import {
  decodeBlob,
  encodeBlob,
  fromDateToEffective,
  fromDaysToExpiration,
  readJson,
  readTxt,
} from './utils'
import { VL, Blob } from './types'
import { decode } from 'xrpl'
import { generateManifest, sign } from './validator'
import { generateSeed, deriveKeypair } from 'ripple-keypairs'

export class PublisherClient {
  binPath: string
  vlPath: string
  vl: VL
  keystorePath = ''
  keyPath = ''
  ephPath = ''

  constructor(vlPath: string = null) {
    this.keystorePath = path.join(process.cwd(), `keystore`)
    this.keyPath = path.join(this.keystorePath, `vl/key.json`)
    this.ephPath = path.join(this.keystorePath, `vl/eph.json`)
    if (!fs.existsSync(this.keystorePath)) {
      fs.mkdirSync(this.keystorePath, { recursive: true })
    }
    if (vlPath) {
      try {
        this.vlPath = vlPath
        const vlJson = fs.readFileSync(vlPath, 'utf8')
        this.vl = JSON.parse(vlJson)
        this.vl.blob = decodeBlob(this.vl.blob as unknown as string) as Blob
        this.vl.blob.sequence += 1
        return this
      } catch (error) {
        throw error
      }
    }

    this.vlPath = path.join(process.cwd(), 'vl.json')
    this.vl = {
      manifest: this.readManifest(),
      blob: {
        sequence: 1,
        validators: [],
        expiration: '',
      },
    }
  }

  getKeys(): any {
    try {
      return readJson(this.keyPath)
    } catch (e) {
      // console.log(e)
      return null
    }
  }

  getEphKeys(): any {
    try {
      return readJson(this.ephPath)
    } catch (e) {
      // console.log(e)
      return null
    }
  }

  readManifest(): string {
    const manifestPath = path.join(this.keystorePath, `vl/manifest.txt`)
    const manifest = readTxt(manifestPath)
    return manifest[0]
  }

  async createKeys(): Promise<void> {
    const keyPathDir = path.join(this.keystorePath, 'vl')
    if (!fs.existsSync(keyPathDir)) {
      await fsPromises.mkdir(keyPathDir, { recursive: true })
    }

    // Empherical Keypair
    const ephSeed = generateSeed({ algorithm: 'ed25519' })
    const ephKeypair = deriveKeypair(ephSeed)
    await fsPromises.writeFile(
      this.ephPath,
      JSON.stringify(ephKeypair, null, 2)
    )

    // VL Keypair
    const seed = generateSeed({ algorithm: 'ed25519' })
    const keypair = deriveKeypair(seed)
    await fsPromises.writeFile(this.keyPath, JSON.stringify(keypair, null, 2))

    const manifest = generateManifest({
      Sequence: 1,
      PublicKey: keypair.publicKey,
      SigningPubKey: ephKeypair.publicKey,
      SigningPrivateKey: ephKeypair.privateKey,
      MasterPrivateKey: keypair.privateKey,
    })
    await fsPromises.writeFile(`${keyPathDir}/manifest.txt`, manifest.base64)
    this.vlPath = path.join(process.cwd(), 'vl.json')
    this.vl = {
      manifest: manifest.base64,
      blob: {
        sequence: 1,
        validators: [],
        expiration: '',
      },
    }
  }

  public addValidator(manifest: string): void {
    if (!this.vl) {
      throw new Error('Invalid VL')
    }

    if (!this.vl.blob) {
      throw new Error('Invalid Blob')
    }

    const encoded = Buffer.from(manifest, 'base64').toString('hex')
    const decoded = decode(encoded)
    const publicKey = (decoded.PublicKey as string).toUpperCase()
    const newValidator = {
      validation_public_key: publicKey,
      manifest: manifest,
    }
    this.vl.blob.validators.push(newValidator)
  }

  public removeValidator(publicKey: string): void {
    if (!this.vl) {
      throw new Error('Invalid VL')
    }

    if (!this.vl.blob) {
      throw new Error('Invalid Blob')
    }

    const validators = this.vl.blob.validators

    const index = validators.findIndex(
      (validator: any) => validator.validation_public_key === publicKey
    )
    if (index !== -1) {
      validators.splice(index, 1)
    } else {
      throw new Error('Validator not found')
    }

    this.vl.blob.validators = validators
  }

  async signUnl(
    path: string,
    options: { effective?: number; expiration?: number } = {}
  ): Promise<void> {
    let { effective, expiration } = options
    if (!this.vl) {
      throw new Error('Invalid VL')
    }

    if (this.vl.blob.validators.length === 0) {
      throw new Error('Must have at least 1 validator')
    }

    if (!effective) {
      effective = fromDateToEffective('01/01/2000')
    }

    if (!expiration) {
      expiration = fromDaysToExpiration(Date.now(), 30)
    }

    const blob = encodeBlob({
      sequence: this.vl.blob.sequence,
      effective: effective,
      expiration: expiration,
      validators: this.vl.blob.validators,
    })

    const manifest = this.readManifest()
    const keys = this.getKeys()
    const ephKeys = this.getEphKeys()
    const signature = sign(Buffer.from(blob, 'base64'), ephKeys.privateKey)
    await fsPromises.writeFile(
      path,
      JSON.stringify(
        {
          blob: blob,
          manifest,
          signature,
          public_key: keys.publicKey,
          version: 1,
        },
        null,
        2
      )
    )
  }
}
