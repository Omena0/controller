import math
from collections.abc import Sequence # Import Sequence

class Vector2:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"

    def __str__(self):
        return f"({self.x}, {self.y})"

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        # Allow adding sequences like tuples/lists
        if isinstance(other, Sequence) and len(other) == 2:
            try:
                return Vector2(self.x + other[0], self.y + other[1])
            except TypeError:
                return NotImplemented # Elements not addable
        return NotImplemented

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
            return self
        # Allow in-place adding sequences like tuples/lists
        if isinstance(other, Sequence) and len(other) == 2:
            try:
                self.x += other[0]
                self.y += other[1]
                return self
            except TypeError:
                return NotImplemented # Elements not addable
        return NotImplemented

    def __radd__(self, other):
        # Handle list/tuple + Vector2
        if isinstance(other, Sequence) and len(other) == 2:
            try:
                # Use __add__ logic which now handles sequences
                return self + other
            except TypeError:
                return NotImplemented # Elements in sequence might not support addition
        # Keep handling 0 + Vector2
        if other == 0:
             return self
        return NotImplemented # Or raise TypeError for other types

    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        # Allow subtracting sequences like tuples/lists
        if isinstance(other, Sequence) and len(other) == 2:
            try:
                return Vector2(self.x - other[0], self.y - other[1])
            except TypeError:
                return NotImplemented # Elements not subtractable
        return NotImplemented

    def __isub__(self, other):
        if isinstance(other, Vector2):
            self.x -= other.x
            self.y -= other.y
            return self
        # Allow in-place subtracting sequences like tuples/lists
        if isinstance(other, Sequence) and len(other) == 2:
            try:
                self.x -= other[0]
                self.y -= other[1]
                return self
            except TypeError:
                return NotImplemented # Elements not subtractable
        return NotImplemented

    def __rsub__(self, other):
        # Handle list/tuple - Vector2
        if isinstance(other, Sequence) and len(other) == 2:
             try:
                 return Vector2(other[0] - self.x, other[1] - self.y)
             except TypeError:
                 return NotImplemented # Elements in sequence might not support subtraction
        # The case Vector2 - Vector2 is handled by __sub__
        # No standard definition for other_type - Vector2 usually
        return NotImplemented

    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return Vector2(self.x * scalar, self.y * scalar)
        # Optional: Implement element-wise multiplication if other is Sequence?
        # if isinstance(scalar, Sequence) and len(scalar) == 2:
        #     try:
        #         return Vector2(self.x * scalar[0], self.y * scalar[1])
        #     except TypeError:
        #         return NotImplemented
        return NotImplemented

    def __imul__(self, scalar):
        if isinstance(scalar, (int, float)):
            self.x *= scalar
            self.y *= scalar
            return self
        # Optional: Implement element-wise in-place multiplication?
        # if isinstance(scalar, Sequence) and len(scalar) == 2:
        #     try:
        #         self.x *= scalar[0]
        #         self.y *= scalar[1]
        #         return self
        #     except TypeError:
        #         return NotImplemented
        return NotImplemented

    def __rmul__(self, scalar):
        # This handles scalar * Vector2, which is standard.
        # Element-wise multiplication (list/tuple * Vector2) is less standard
        # and might be confused with dot product or scalar multiplication.
        # Sticking to scalar multiplication for __rmul__.
        if isinstance(scalar, (int, float)):
            # Use __mul__ logic
            return self * scalar
        return NotImplemented

    def __truediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ZeroDivisionError("division by zero")
            return Vector2(self.x / scalar, self.y / scalar)
        # Optional: Implement element-wise division if other is Sequence?
        # if isinstance(scalar, Sequence) and len(scalar) == 2:
        #     try:
        #         if scalar[0] == 0 or scalar[1] == 0:
        #              raise ZeroDivisionError("division by zero in sequence element")
        #         return Vector2(self.x / scalar[0], self.y / scalar[1])
        #     except TypeError:
        #         return NotImplemented
        return NotImplemented

    def __itruediv__(self, scalar):
        if isinstance(scalar, (int, float)):
            if scalar == 0:
                raise ZeroDivisionError("division by zero")
            self.x /= scalar
            self.y /= scalar
            return self
        # Optional: Implement element-wise in-place division?
        # if isinstance(scalar, Sequence) and len(scalar) == 2:
        #     try:
        #         if scalar[0] == 0 or scalar[1] == 0:
        #              raise ZeroDivisionError("division by zero in sequence element")
        #         self.x /= scalar[0]
        #         self.y /= scalar[1]
        #         return self
        #     except TypeError:
        #         return NotImplemented
        return NotImplemented

    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __eq__(self, other):
        if isinstance(other, Vector2):
            # Use math.isclose for floating-point comparisons
            return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
        # Optional: Compare with list/tuple
        if isinstance(other, Sequence) and len(other) == 2:
             try:
                 return math.isclose(self.x, other[0]) and math.isclose(self.y, other[1])
             except TypeError:
                 return False # Elements not comparable
        return False

    def __len__(self):
        return 2

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        else:
            raise IndexError("Vector2 index out of range")

    def magnitude_squared(self):
        return self.x**2 + self.y**2

    def magnitude(self):
        return math.sqrt(self.magnitude_squared())

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            # Or raise an error, depending on desired behavior for zero vector
            return Vector2(0, 0)
        # Uses self.__truediv__
        return self / mag

    def dot(self, other):
        if isinstance(other, Vector2):
            return self.x * other.x + self.y * other.y
        # Optional: Allow dot product with list/tuple
        if isinstance(other, Sequence) and len(other) == 2:
            try:
                return self.x * other[0] + self.y * other[1]
            except TypeError:
                return NotImplemented # Elements not multipliable/addable
        return NotImplemented





