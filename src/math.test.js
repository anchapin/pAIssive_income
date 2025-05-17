const assert = require('assert');
const { add } = require('./math');

describe('add', function () {
  it('should add two numbers correctly', function () {
    assert.strictEqual(add(2, 3), 5);
  });
});