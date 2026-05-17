import { expect, test } from '@playwright/test';

const API_PORT = process.env.LEXI_E2E_API_PORT || '8010';
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || `http://127.0.0.1:${API_PORT}/api/v1`;
const UUID_PATTERN = /[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}/i;

function escapePdfText(value) {
  return value.replaceAll('\\', '\\\\').replaceAll('(', '\\(').replaceAll(')', '\\)');
}

function buildTextPdf(lines) {
  const textStream = [
    'BT',
    '/F1 10 Tf',
    '50 760 Td',
    '14 TL',
    ...lines.flatMap((line) => [`(${escapePdfText(line)}) Tj`, 'T*']),
    'ET',
  ].join('\n');

  const objects = [
    '<< /Type /Catalog /Pages 2 0 R >>',
    '<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
    '<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
    '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
    `<< /Length ${Buffer.byteLength(textStream)} >>\nstream\n${textStream}\nendstream`,
  ];

  let pdf = '%PDF-1.4\n';
  const offsets = [0];

  for (const [index, object] of objects.entries()) {
    offsets.push(Buffer.byteLength(pdf));
    pdf += `${index + 1} 0 obj\n${object}\nendobj\n`;
  }

  const xrefOffset = Buffer.byteLength(pdf);
  pdf += `xref\n0 ${objects.length + 1}\n`;
  pdf += '0000000000 65535 f \n';

  for (const offset of offsets.slice(1)) {
    pdf += `${String(offset).padStart(10, '0')} 00000 n \n`;
  }

  pdf += `trailer\n<< /Root 1 0 R /Size ${objects.length + 1} >>\nstartxref\n${xrefOffset}\n%%EOF\n`;

  return Buffer.from(pdf, 'utf8');
}

function buildSampleLeasePdf() {
  return buildTextPdf([
    'Ontario Standard Lease Residential tenancy agreement governed by the Residential Tenancies Act Ontario and reviewed by the Landlord and Tenant Board.',
    'Landlord: Alex Smith',
    'Tenant: Jane Doe',
    'Rental unit: 123 King Street, Toronto, ON',
    'Lease term start date: 01/01/2026',
    'Lease term end date: 12/31/2026',
    'Monthly rent: $2450 per month',
    '1. Rent payment. The tenant must pay monthly rent on the first day of each month.',
    '2. Maintenance and repair. The landlord is responsible for maintenance and repair of the rental unit.',
    '3. Entry and access. The landlord may enter for inspection only with lawful notice.',
    '4. Utilities. Hydro, water, gas, and electricity responsibilities are listed in this lease.',
    '5. Notice to end. Either party must follow Ontario notice requirements to terminate the lease.',
    '6. Subletting. The tenant may request assignment or sublet approval in writing.',
  ]);
}

function buildUnsupportedPdf() {
  return buildTextPdf([
    'Bakery Operations Packet',
    'Weekly bakery production report for the downtown kitchen team.',
    'Croissant batches were counted before opening, muffin trays were labeled, and delivery crates were checked against supplier invoices.',
    'The afternoon notes cover oven cleaning, refrigerator temperature logs, packaging counts, staff training reminders, ingredient substitutions, and customer feedback.',
    'Community event orders include fruit tarts, sandwich platters, coffee service, seasonal menu experiments, and a checklist for tomorrow morning.',
    'The closing summary records register reconciliation, broken tray replacement, pantry restocking, and schedule notes for the next production cycle.',
  ]);
}

async function activeDocumentId(page) {
  const documentLine = page.locator('.status-line').filter({ hasText: 'Document:' });
  await expect(documentLine).toContainText(UUID_PATTERN);

  const text = await documentLine.textContent();
  const match = text.match(UUID_PATTERN);
  expect(match).toBeTruthy();

  return match[0];
}

async function registerFromPublicHome(page, email, password) {
  await page.getByRole('button', { name: 'Start with a Document' }).click();
  await page.getByRole('button', { name: 'Register' }).click();
  await page.getByLabel('Email').fill(email);
  await page.getByLabel('Password').fill(password);
  await page.getByRole('button', { name: 'Create account' }).click();

  await expect(page.getByText(email)).toBeVisible();
  await expect(page.getByText('Signed in', { exact: true })).toBeVisible();
}

test.describe('Live lease verification flow', () => {
  test.setTimeout(60000);

  test('registers, uploads, consents, processes, displays results, and deletes using the live API', async ({ page, request }) => {
    const email = `lease-e2e-ui-${Date.now()}@example.com`;
    const password = 'lease-proof-password';

    await page.goto('/');
    await page.getByRole('button', { name: 'I understand' }).click();

    await registerFromPublicHome(page, email, password);

    const accessToken = await page.evaluate(() => window.localStorage.getItem('lexi_access_token'));
    expect(accessToken).toBeTruthy();

    await page.locator('#file-upload').setInputFiles({
      name: 'sample-ontario-lease.pdf',
      mimeType: 'application/pdf',
      buffer: buildSampleLeasePdf(),
    });
    await page.locator('.chat-input-form').getByRole('button', { name: 'Upload document' }).click();

    const documentId = await activeDocumentId(page);

    await page.getByRole('button', { name: 'Submit consent' }).click();

    await expect(page.locator('.status-line').filter({ hasText: 'Status:' })).toContainText('complete', {
      timeout: 15000,
    });
    await expect(page.locator('.status-line').filter({ hasText: 'Type:' })).toContainText('ontario_residential_lease');
    await expect(page.getByText('Monthly rent: $2450', { exact: true }).first()).toBeVisible();
    await expect(page.getByText('Lease start: 2026-01-01')).toBeVisible();
    await expect(page.getByText('Lease end: 2026-12-31')).toBeVisible();
    await expect(
      page.getByText(/This ontario residential lease names Jane Doe as tenant and Alex Smith as landlord/)
    ).toBeVisible();
    await expect(page.locator('.summary-section').getByText(/includes clauses about .*maintenance/)).toBeVisible();
    await expect(page.locator('.summary-section').getByText(/entry and access/)).toBeVisible();
    await expect(page.getByText('RiskSense', { exact: true })).toBeVisible();
    await expect(page.getByText('Attention signals', { exact: true })).toBeVisible();
    await expect(page.getByText(/RiskSense found \d+ attention signal/)).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Rent payment timing' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Landlord entry wording' })).toBeVisible();

    const liveResults = await request.get(`${API_BASE}/documents/${documentId}/results`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(liveResults.ok()).toBe(true);

    const resultsPayload = await liveResults.json();
    expect(resultsPayload.metadata.tenant_names).toEqual(['Jane Doe']);
    expect(resultsPayload.metadata.landlord_names).toEqual(['Alex Smith']);
    expect(resultsPayload.total_clauses).toBeGreaterThanOrEqual(6);
    expect(resultsPayload.risk_sense).toBeTruthy();
    expect(resultsPayload.risk_sense.risks.length).toBeGreaterThanOrEqual(1);
    expect(resultsPayload.risk_sense.confidence_rollup.overall).toBeGreaterThan(0);
    expect(resultsPayload.risk_sense.risks.some((risk) => risk.rule_id === 'landlord_access')).toBe(true);
    const riskLanguage = [
      resultsPayload.risk_sense.top_risks_summary,
      ...resultsPayload.risk_sense.risks.map((risk) => `${risk.title} ${risk.reason}`),
    ].join(' ').toLowerCase();
    for (const phrase of [
      'illegal',
      'unlawful',
      'unenforceable',
      'will win',
      'will lose',
      'will be evicted',
      'must sign',
      'do not sign',
    ]) {
      expect(riskLanguage).not.toContain(phrase);
    }

    const history = await request.get(`${API_BASE}/documents`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(history.ok()).toBe(true);
    const historyPayload = await history.json();
    expect(historyPayload.documents).toHaveLength(1);
    expect(historyPayload.documents[0].document_id).toBe(documentId);
    expect(historyPayload.documents[0].filename).toBe('sample-ontario-lease.pdf');
    expect(historyPayload.documents[0].job_status).toBe('complete');
    expect(historyPayload.documents[0].document_type).toBe('ontario_residential_lease');
    expect(historyPayload.documents[0].extracted_text).toBeUndefined();
    expect(historyPayload.documents[0].clauses).toBeUndefined();

    await expect(page.getByRole('button', { name: /sample-ontario-lease\.pdf/ })).toBeVisible();
    await page.getByLabel('Situation context (optional)').fill('My landlord told me rent might be $3000.');
    await page.getByRole('textbox', { name: 'Question' }).fill('What is the monthly rent?');
    await page.getByRole('button', { name: 'Ask', exact: true }).click();
    await expect(page.getByText(/From this document: "Monthly rent: \$2450 per month"/)).toBeVisible();
    await expect(page.getByText('Source 1')).toBeVisible();
    await expect(page.getByText(/kept separate from the document evidence/)).toBeVisible();

    await page.getByRole('textbox', { name: 'Question' }).fill('Does this document say parking is included?');
    await page.getByRole('button', { name: 'Ask', exact: true }).click();
    await expect(page.getByText(/I don't know from this document/)).toBeVisible();

    const groundedAsk = await request.post(`${API_BASE}/documents/${documentId}/ask`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: {
        question: 'What is the monthly rent?',
        user_context: 'My landlord told me rent might be $3000.',
      },
    });
    expect(groundedAsk.ok()).toBe(true);
    const groundedAskPayload = await groundedAsk.json();
    expect(groundedAskPayload.is_answered).toBe(true);
    expect(groundedAskPayload.answer).toContain('$2450');
    expect(groundedAskPayload.answer).not.toContain('$3000');
    expect(groundedAskPayload.citations[0].text).toContain('$2450');

    const otherEmail = `lease-e2e-ui-other-${Date.now()}@example.com`;
    const otherRegister = await request.post(`${API_BASE}/auth/register`, {
      data: { email: otherEmail, password },
    });
    expect(otherRegister.status()).toBe(201);

    const otherLogin = await request.post(`${API_BASE}/auth/login`, {
      form: { username: otherEmail, password },
    });
    expect(otherLogin.status()).toBe(200);
    const otherAccessToken = (await otherLogin.json()).access_token;

    const crossUserResults = await request.get(`${API_BASE}/documents/${documentId}/results`, {
      headers: { Authorization: `Bearer ${otherAccessToken}` },
    });
    expect(crossUserResults.status()).toBe(404);

    const crossUserJob = await request.get(`${API_BASE}/jobs/${documentId}/status`, {
      headers: { Authorization: `Bearer ${otherAccessToken}` },
    });
    expect(crossUserJob.status()).toBe(404);

    const crossUserHistory = await request.get(`${API_BASE}/documents`, {
      headers: { Authorization: `Bearer ${otherAccessToken}` },
    });
    expect(crossUserHistory.status()).toBe(200);
    expect((await crossUserHistory.json()).documents).toEqual([]);

    const crossUserAsk = await request.post(`${API_BASE}/documents/${documentId}/ask`, {
      headers: { Authorization: `Bearer ${otherAccessToken}` },
      data: { question: 'What is the monthly rent?' },
    });
    expect(crossUserAsk.status()).toBe(404);

    const crossUserDelete = await request.delete(`${API_BASE}/documents/${documentId}`, {
      headers: { Authorization: `Bearer ${otherAccessToken}` },
    });
    expect(crossUserDelete.status()).toBe(404);

    await page.getByRole('button', { name: 'Delete document' }).click();

    await expect(page.getByText('Drop your document here or click to upload')).toBeVisible();
    await expect(page.getByText('No documents yet. Upload a lease to begin.')).toBeVisible();

    const deletedResults = await request.get(`${API_BASE}/documents/${documentId}/results`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(deletedResults.status()).toBe(404);

    const deletedJob = await request.get(`${API_BASE}/jobs/${documentId}/status`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(deletedJob.status()).toBe(404);

    const deletedHistory = await request.get(`${API_BASE}/documents`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(deletedHistory.status()).toBe(200);
    expect((await deletedHistory.json()).documents).toEqual([]);
  });

  test('shows a safe unsupported state for random supported-format content', async ({ page, request }) => {
    const email = `unsupported-e2e-ui-${Date.now()}@example.com`;
    const password = 'lease-proof-password';

    await page.goto('/');
    await page.getByRole('button', { name: 'I understand' }).click();
    await registerFromPublicHome(page, email, password);

    const accessToken = await page.evaluate(() => window.localStorage.getItem('lexi_access_token'));
    expect(accessToken).toBeTruthy();

    await page.locator('#file-upload').setInputFiles({
      name: 'bakery-operations.pdf',
      mimeType: 'application/pdf',
      buffer: buildUnsupportedPdf(),
    });
    await page.locator('.chat-input-form').getByRole('button', { name: 'Upload document' }).click();

    const documentId = await activeDocumentId(page);
    await page.getByRole('button', { name: 'Submit consent' }).click();

    await expect(page.getByText('Unsupported by Lexi', { exact: true })).toBeVisible();
    await expect(
      page.getByText('Lexi could not identify this as a supported document type yet.')
    ).toBeVisible();
    await expect(page.getByText(/100\.0% confidence/)).toBeVisible();
    await expect(page.getByText(/unsupported by Lexi right now/)).toBeVisible();
    await expect(page.getByRole('textbox', { name: 'Question' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Ask' })).toHaveCount(0);

    const unsupportedResults = await request.get(`${API_BASE}/documents/${documentId}/results`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    });
    expect(unsupportedResults.ok()).toBe(true);
    const unsupportedPayload = await unsupportedResults.json();
    expect(unsupportedPayload.document_type).toBe('unknown');
    expect(unsupportedPayload.summary).toBeNull();
    expect(unsupportedPayload.risk_sense).toBeNull();
    expect(unsupportedPayload.clauses).toEqual([]);

    const unsupportedAsk = await request.post(`${API_BASE}/documents/${documentId}/ask`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { question: 'What does this document say about rent?' },
    });
    expect(unsupportedAsk.status()).toBe(400);
    expect((await unsupportedAsk.json()).detail).toContain('unsupported by Lexi');

    await page.getByRole('button', { name: 'Delete document' }).last().click();
    await expect(page.getByText('Drop your document here or click to upload')).toBeVisible();
  });
});
