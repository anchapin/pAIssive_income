"""Simple test file to verify that pytest is working."""

import pytest
from decimal import Decimal


class TestSimpleMath:
    """Simple test cases for basic math operations."""

    def test_addition(self):
        """Test that addition works."""
        # Basic addition
        assert 1 + 1 == 2
        assert 0 + 0 == 0
        assert -1 + 1 == 0
        assert -1 + -1 == -2

        # Decimal addition
        assert Decimal('1.1') + Decimal('2.2') == Decimal('3.3')
        assert Decimal('0.1') + Decimal('0.2') == Decimal('0.3')

        # Large numbers
        assert 999999 + 1 == 1000000
        assert -999999 + -1 == -1000000

    def test_subtraction(self):
        """Test that subtraction works."""
        # Basic subtraction
        assert 3 - 1 == 2
        assert 1 - 1 == 0
        assert 0 - 1 == -1
        assert -1 - 1 == -2

        # Decimal subtraction
        assert Decimal('3.3') - Decimal('1.1') == Decimal('2.2')
        assert Decimal('0.3') - Decimal('0.1') == Decimal('0.2')

        # Large numbers
        assert 1000000 - 1 == 999999
        assert -1000000 - 1 == -1000001

    def test_multiplication(self):
        """Test that multiplication works."""
        # Basic multiplication
        assert 2 * 3 == 6
        assert 0 * 5 == 0
        assert -2 * 3 == -6
        assert -2 * -3 == 6

        # Decimal multiplication
        assert Decimal('2.5') * Decimal('2') == Decimal('5.0')
        assert Decimal('0.1') * Decimal('0.1') == Decimal('0.01')

        # Large numbers
        assert 1000 * 1000 == 1000000
        assert -1000 * 1000 == -1000000

    def test_division(self):
        """Test that division works."""
        # Basic division
        assert 6 / 3 == 2
        assert 0 / 5 == 0
        assert -6 / 3 == -2
        assert -6 / -3 == 2

        # Decimal division
        assert Decimal('5.0') / Decimal('2') == Decimal('2.5')
        assert Decimal('0.1') / Decimal('2') == Decimal('0.05')

        # Large numbers
        assert 1000000 / 2 == 500000
        assert -1000000 / 2 == -500000

    def test_division_by_zero(self):
        """Test that division by zero raises an error."""
        with pytest.raises(ZeroDivisionError):
            _ = 1 / 0

        with pytest.raises(ZeroDivisionError):
            _ = Decimal('1') / Decimal('0')

    def test_power(self):
        """Test that power operations work."""
        # Basic power
        assert 2 ** 3 == 8
        assert 2 ** 0 == 1
        assert 2 ** -1 == 0.5

        # Decimal power
        assert Decimal('2') ** Decimal('3') == Decimal('8')
        assert Decimal('2') ** Decimal('0') == Decimal('1')
        assert Decimal('2') ** Decimal('-1') == Decimal('0.5')

    def test_modulo(self):
        """Test that modulo operations work."""
        # Basic modulo
        assert 5 % 2 == 1
        assert 6 % 2 == 0
        assert -5 % 2 == 1
        assert 5 % -2 == -1

        # Decimal modulo
        assert Decimal('5.5') % Decimal('2') == Decimal('1.5')
        assert Decimal('6.0') % Decimal('2') == Decimal('0.0')

    def test_floor_division(self):
        """Test that floor division works."""
        # Basic floor division
        assert 5 // 2 == 2
        assert -5 // 2 == -3
        assert 5 // -2 == -3
        assert -5 // -2 == 2

        # Decimal floor division
        assert Decimal('5.5') // Decimal('2') == Decimal('2')
        assert Decimal('-5.5') // Decimal('2') == Decimal('-3')
