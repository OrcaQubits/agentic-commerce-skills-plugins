// Single-process example only. Production needs durable, atomic operation storage.
import { createHash } from 'node:crypto';

export class SettlementGuard {
  #operations = new Map();

  async settleOnce(operationId, payment, settle, knownRejection) {
    if (typeof operationId !== 'string' || !operationId || operationId.length > 256) {
      throw new Error('A bounded application operation ID is required');
    }
    const fingerprint = createHash('sha256').update(JSON.stringify(payment)).digest('hex');
    const existing = this.#operations.get(operationId);
    if (existing) {
      if (existing.fingerprint !== fingerprint) throw new Error('Operation reused with different payment');
      return existing.promise;
    }
    // Reserve before invoking settle, including synchronous/re-entrant failures.
    const entry = {fingerprint};
    this.#operations.set(operationId, entry);
    entry.promise = Promise.resolve().then(async () => {
      try {
        const result = await settle();
        if (result.success === true) return {state: 'settled', result};
        if (knownRejection(result)) return {state: 'rejected', result};
        return {state: 'unknown'};
      } catch {
        return {state: 'unknown'};
      }
    });
    return entry.promise;
  }
}
