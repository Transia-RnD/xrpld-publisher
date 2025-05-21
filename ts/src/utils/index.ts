import * as fs from 'fs'
import axios from 'axios'
import { unixTimeToRippleTime } from 'xrpl'

export function fromDateToEffective(date_str: string): number {
  const effectiveTs = new Date(date_str).getTime()
  return unixTimeToRippleTime(effectiveTs)
}

export function fromDaysToExpiration(ts: number, days: number): number {
  return ts + 86400 * days // expires in x days
}

export function convertStringToTimestamp(dateStr: string): number {
  const timestamp = Date.parse(dateStr)
  return timestamp
}

export function encodeBlob(blob: object): string {
  const compactJson = JSON.stringify(blob)
  const pythonStyleJson = compactJson.replace(/:/g, ': ').replace(/,/g, ', ')
  return Buffer.from(pythonStyleJson, 'utf-8').toString('base64')
}

export function decodeBlob(blob: string): object {
  return JSON.parse(Buffer.from(blob, 'base64').toString('utf8'))
}
export function readTxt(path: string): string[] {
  return fs.readFileSync(path, 'utf8').split('\n')
}

export function readFile(path: string): string {
  return fs.readFileSync(path, 'utf8')
}

export function readJson(path: string): object {
  return JSON.parse(fs.readFileSync(path, 'utf8'))
}

export function writeJson(data: object, path: string): boolean {
  fs.writeFileSync(path, JSON.stringify(data))
  return true
}

export async function downloadUNL(url: string): Promise<any> {
  const response = await axios.get(url)

  // Check if the request was successful
  if (response.status !== 200) {
    throw new Error(`HTTP error! status: ${response.status}`)
  }

  writeJson(response.data, 'vl.json')
}
