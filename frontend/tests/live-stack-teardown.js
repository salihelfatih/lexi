import { rmSync } from 'node:fs';

export default async function teardown() {
  const databaseMode = process.env.LEXI_E2E_DATABASE || 'sqlite';
  const apiPort = process.env.LEXI_E2E_API_PORT || '8010';
  const apiTmpRoot = process.env.LEXI_E2E_TMP_ROOT || `/tmp/lexi_playwright_api_${databaseMode}_${apiPort}`;

  rmSync(apiTmpRoot, { recursive: true, force: true });
}
