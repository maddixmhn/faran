import assert from 'node:assert/strict';
import test from 'node:test';
import { reviewTermWithdrawal } from './term-review.mjs';

const example = { written: true, requestAt: '2026-12-20T10:00', examsAt: '2026-12-23T08:00',
  council: 'approved', decisionAt: '2026-12-22T15:20', reference: 'test-001' };

for (const [changes, expected] of [
  [{}, 'documented-approval'],
  [{ written: false }, 'missing-written'],
  [{ requestAt: '2026-02-31T10:00' }, 'missing-dates'],
  [{ requestAt: example.examsAt }, 'late-request'],
  [{ council: 'pending' }, 'pending-council'],
  [{ reference: ' ' }, 'missing-decision'],
  [{ decisionAt: '2026-12-19T15:20' }, 'missing-decision'],
  [{ council: 'rejected' }, 'rejected'],
  [{ decisionAt: example.examsAt }, 'late-decision'],
]) {
  test(expected + ' ' + JSON.stringify(changes), () => {
    assert.equal(reviewTermWithdrawal({ ...example, ...changes }).code, expected);
  });
}
