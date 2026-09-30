import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { spawnSync } from 'node:child_process';
const image = 'demo.azurecr.io/carparts@sha256:' + 'a'.repeat(64);
const commit = 'b'.repeat(40);
function verify(patch, expectedImage = image) {
  const directory = mkdtempSync(join(tmpdir(), 'carparts-approval-'));
  const file = join(directory, 'approval.json');
  writeFileSync(file, JSON.stringify({image, commit, approver: 'release-manager', approvedAt: '2026-09-30T17:00:00Z', buildUrl: 'http://localhost:8080/job/test/1/', ...patch}));
  const result = spawnSync(process.execPath, ['ci/verify-approval.mjs', file, expectedImage, commit]);
  rmSync(directory, {recursive: true});
  return result.status;
}
test('aprovação válida é aceita', () => assert.equal(verify({}), 0));
test('digest diferente é recusado', () => assert.notEqual(verify({}, image + '0'), 0));
test('commit diferente é recusado', () => assert.notEqual(verify({commit: 'c'.repeat(40)}), 0));
test('usuário não autorizado é recusado', () => assert.notEqual(verify({approver: 'other'}), 0));
test('data inválida é recusada', () => assert.notEqual(verify({approvedAt: 'invalid'}), 0));
