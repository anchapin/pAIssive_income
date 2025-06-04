/**
 * Unit tests for math utility functions.
 *
 * Tests basic arithmetic operations including edge cases
 * and error conditions.
 */

import assert from 'assert';
import { add, divide, multiply, subtract } from './math.js';

describe('Math functions', () => {
  describe('add', () => {
    it('should add two positive numbers correctly', () => {
      assert.strictEqual(add(2, 3), 5);
    });

    it('should add a positive and a negative number correctly', () => {
      assert.strictEqual(add(2, -3), -1);
    });

    it('should add two negative numbers correctly', () => {
      assert.strictEqual(add(-2, -3), -5);
    });
  });

  describe('subtract', () => {
    it('should subtract two numbers correctly', () => {
      assert.strictEqual(subtract(5, 3), 2);
    });

    it('should handle negative results', () => {
      assert.strictEqual(subtract(3, 5), -2);
    });
  });

  describe('multiply', () => {
    it('should multiply two positive numbers correctly', () => {
      assert.strictEqual(multiply(2, 3), 6);
    });

    it('should multiply a positive and a negative number correctly', () => {
      assert.strictEqual(multiply(2, -3), -6);
    });

    it('should multiply two negative numbers correctly', () => {
      assert.strictEqual(multiply(-2, -3), 6);
    });
  });

  describe('divide', () => {
    it('should divide two numbers correctly', () => {
      assert.strictEqual(divide(6, 3), 2);
    });

    it('should handle decimal results', () => {
      assert.strictEqual(divide(5, 2), 2.5);
    });

    it('should throw error when dividing by zero', () => {
      assert.throws(() => divide(5, 0), Error('Cannot divide by zero'));
    });
  });
});
