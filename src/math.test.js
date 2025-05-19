const assert = require('assert');
const { add, subtract, multiply, divide } = require('./math');

describe('Math functions', function () {
  describe('add', function () {
    it('should add two positive numbers correctly', function () {
      assert.strictEqual(add(2, 3), 5);
    });

    it('should add a positive and a negative number correctly', function () {
      assert.strictEqual(add(2, -3), -1);
    });

    it('should add two negative numbers correctly', function () {
      assert.strictEqual(add(-2, -3), -5);
    });
  });

  describe('subtract', function () {
    it('should subtract two numbers correctly', function () {
      assert.strictEqual(subtract(5, 3), 2);
    });

    it('should handle negative results', function () {
      assert.strictEqual(subtract(3, 5), -2);
    });
  });

  describe('multiply', function () {
    it('should multiply two positive numbers correctly', function () {
      assert.strictEqual(multiply(2, 3), 6);
    });

    it('should multiply a positive and a negative number correctly', function () {
      assert.strictEqual(multiply(2, -3), -6);
    });

    it('should multiply two negative numbers correctly', function () {
      assert.strictEqual(multiply(-2, -3), 6);
    });
  });

  describe('divide', function () {
    it('should divide two numbers correctly', function () {
      assert.strictEqual(divide(6, 3), 2);
    });

    it('should handle decimal results', function () {
      assert.strictEqual(divide(5, 2), 2.5);
    });

    it('should throw an error when dividing by zero', function () {
      assert.throws(() => {
        divide(5, 0);
      }, /Division by zero is not allowed/);
    });
  });
});