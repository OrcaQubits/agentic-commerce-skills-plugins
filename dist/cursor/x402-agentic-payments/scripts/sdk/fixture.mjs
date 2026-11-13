// Real SDK local signatures and HTTP negotiation; facilitator is mocked.
import assert from 'node:assert/strict';
import { generatePrivateKey, privateKeyToAccount } from 'viem/accounts';
import { verifyTypedData } from 'viem';
import { authorizationTypes } from '@x402/evm';
import { SettlementGuard } from './settlement_guard.mjs';
import { x402Client, x402HTTPClient } from '@x402/core/client';
import { x402ResourceServer, x402HTTPResourceServer } from '@x402/core/server';
import { ExactEvmScheme as ClientScheme } from '@x402/evm/exact/client';
import { ExactEvmScheme as ServerScheme } from '@x402/evm/exact/server';

globalThis.fetch = async () => { throw new Error('Network forbidden in offline fixture'); };
const account = privateKeyToAccount(generatePrivateKey());
const network = 'eip155:84532';
const asset = '0x036CbD53842c5426634e7929541eC2318f3dCF7e';
const payTo = '0x1111111111111111111111111111111111111111';
let outcome = 'success';
let settlements = 0;
const facilitator = {
  getSupported: async () => ({kinds: [{x402Version: 2, scheme: 'exact', network}], extensions: [], signers: {}}),
  verify: async () => outcome === 'invalid' ? {isValid: false, invalidReason: 'fixture_rejected'} : {isValid: true, payer: account.address},
  settle: async () => {
    settlements++;
    if (outcome === 'unknown') throw new Error('fixture: transport lost after submission');
    return {success: outcome !== 'rejected', network, transaction: outcome === 'rejected' ? '' : 'synthetic-transaction',
      payer: account.address, ...(outcome === 'rejected' ? {errorReason: 'fixture_rejected'} : {})};
  },
};
const server = new x402ResourceServer(facilitator).register(network, new ServerScheme());
const http = new x402HTTPResourceServer(server, {'GET /paid': {
  accepts: [{scheme: 'exact', network, payTo,
    price: {amount: '1000', asset, extra: {name: 'USDC', version: '2'}}}],
  description: 'Synthetic offline fixture', mimeType: 'application/json',
}});
await http.initialize();
const client = new x402HTTPClient(new x402Client().register(network, new ClientScheme(account)));
function context(paymentHeader) {
  return {method: 'GET', path: '/paid', paymentHeader, adapter: {
    getHeader: name => name.toLowerCase() === 'payment-signature' ? paymentHeader : undefined,
    getMethod: () => 'GET', getPath: () => '/paid', getUrl: () => 'https://merchant.example/paid',
    getAcceptHeader: () => 'application/json', getUserAgent: () => 'offline-fixture',
  }};
}
const challenge = await http.processHTTPRequest(context());
assert.equal(challenge.type, 'payment-error');
assert.equal(challenge.response.status, 402);
const required = client.getPaymentRequiredResponse(name => challenge.response.headers[name] ?? challenge.response.headers[name.toUpperCase()], challenge.response.body);
assert.equal(required.x402Version, 2);
assert.equal(required.accepts[0].amount, '1000');
assert.equal(required.accepts[0].payTo.toLowerCase(), payTo.toLowerCase());
const payload = await client.createPaymentPayload(required);
assert.equal(payload.payload.authorization.to.toLowerCase(), payTo.toLowerCase());
const signed = {address: account.address, domain: {name: 'USDC', version: '2', chainId: 84532, verifyingContract: asset},
  types: authorizationTypes, primaryType: 'TransferWithAuthorization',
  message: payload.payload.authorization, signature: payload.payload.signature};
assert.equal(await verifyTypedData(signed), true, 'local EIP-712 signature verifies');
assert.equal(await verifyTypedData({...signed, message: {...signed.message, value: '1001'}}), false, 'changed amount invalidates signature');
const encoded = client.encodePaymentSignatureHeader(payload);
const paymentHeader = encoded['PAYMENT-SIGNATURE'] ?? encoded['payment-signature'];
assert.ok(paymentHeader);

outcome = 'invalid';
assert.equal((await http.processHTTPRequest(context(paymentHeader))).type, 'payment-error');
assert.equal(settlements, 0, 'verification rejection must never settle');
outcome = 'success';
const verified = await http.processHTTPRequest(context(paymentHeader));
assert.equal(verified.type, 'payment-verified');
const guard = new SettlementGuard();
const perform = id => guard.settleOnce(id, verified.paymentPayload,
  () => http.processSettlement(verified.paymentPayload, verified.paymentRequirements),
  result => result.errorReason === 'fixture_rejected');
const settled = await perform('success-operation');
assert.equal(settled.state, 'settled');
assert.ok(Object.keys(settled.result.headers).some(k => k.toLowerCase() === 'payment-response'));
const settledCount = settlements;
assert.equal((await perform('success-operation')).state, 'settled');
assert.equal(settlements, settledCount, 'duplicate completed operation does not settle again');

outcome = 'rejected';
const rejected = await perform('rejected-operation');
assert.equal(rejected.state, 'rejected');
outcome = 'unknown';
const before = settlements;
const uncertain = await Promise.all([perform('unknown-operation'), perform('unknown-operation')]);
assert.ok(uncertain.every(r => r.state === 'unknown'));
assert.equal((await perform('unknown-operation')).state, 'unknown');
assert.equal(settlements, before + 1, 'no hidden settlement retry');
await assert.rejects(() => guard.settleOnce('unknown-operation', {...verified.paymentPayload, altered: true}, () => {}, () => false));
console.log('PASS: SDK HTTP negotiation, verified local signature, tampering, rejected verification, distinct mocked settlement states and duplicate/concurrent retry guard; no network or funds used');
