import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { join } from 'node:path'

const backendDirectory = join(process.cwd(), 'backend')
const virtualEnvironmentPython =
  process.platform === 'win32'
    ? join(backendDirectory, '.venv', 'Scripts', 'python.exe')
    : join(backendDirectory, '.venv', 'bin', 'python')
const python = existsSync(virtualEnvironmentPython)
  ? virtualEnvironmentPython
  : 'python'

const child = spawn(python, process.argv.slice(2), {
  cwd: backendDirectory,
  env: {
    ...process.env,
    PYTHONIOENCODING: 'utf-8',
    PYTHONUTF8: '1',
  },
  stdio: 'inherit',
})

for (const signal of ['SIGINT', 'SIGTERM']) {
  process.on(signal, () => child.kill(signal))
}

child.on('error', (error) => {
  console.error(`无法启动 Python：${error.message}`)
  process.exitCode = 1
})

child.on('exit', (code, signal) => {
  process.exitCode = signal ? 1 : (code ?? 1)
})
