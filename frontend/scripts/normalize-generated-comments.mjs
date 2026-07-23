import { readFile, writeFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'

const schemaPath = fileURLToPath(
  new URL('../src/api/schema.d.ts', import.meta.url),
)
const source = await readFile(schemaPath, 'utf8')
const normalized = source
  .replace(/\/\*\*[\s\S]*?\*\//gu, (comment) =>
    /[\u3400-\u9fff]/u.test(comment) ? comment : '',
  )
  .replace(/[ \t]+$/gmu, '')
  .replace(/\n{3,}/gu, '\n\n')

await writeFile(schemaPath, normalized, 'utf8')
