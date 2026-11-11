from main import division
import pytest

def test_division():
    # Test case 1: Normal division
    div = division(10, 2)
    assert div.divide() == 5

    # Test case 2: Division by zero
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        div = division(10, 0)
        div.divide()
    

if __name__ == "__main__":
    test_division()