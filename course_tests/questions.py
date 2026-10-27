import ast
import inspect
import math
from .core import test, script, has, calls, calls_attr, func_calls

# ======================================================
# 1. Variables & Basic Math
# ======================================================
script("q1", "a, b = 15, 4\nprint(a // b, a % b)",
       overrides=[{"a": 20, "b": 3}, {"a": 7, "b": 7}, {"a": 100, "b": 9}])

script("q2", "x, y = 5, 10\nx, y = y, x\nprint(x, y)",
       overrides=[{"x": 1, "y": 2}, {"x": -3, "y": 8}])

# q3: no test (predict)

# ======================================================
# 2. Strings & Conditions
# ======================================================
script("q4", "s = 'python'\nprint(s[::-1])",
       overrides=[{"s": "hello"}, {"s": "abc"}],
       rules=[lambda t: not has(t, ast.Slice)])

script("q5", "word = 'radar'\nprint(word == word[::-1])",
       overrides=[{"word": "level"}, {"word": "hello"}, {"word": "a"}])

script("q6", "n = 7\nprint('Even' if n % 2 == 0 else 'Odd')",
       overrides=[{"n": 10}, {"n": 0}, {"n": -3}],
       rules=[lambda t: not has(t, ast.IfExp)])

script("q7", "score = 85\nprint('Pass' if score >= 50 else 'Fail')",
       overrides=[{"score": 50}, {"score": 49}, {"score": 0}, {"score": 100}])

# ======================================================
# 3. Loops
# ======================================================
script("q8", "total = 0\nfor i in range(1, 6): total += i\nprint(total)",
       rules=[lambda t: not has(t, ast.For),
              lambda t: calls(t, "sum")])

script("q9", "nums = [14, 89, 42, 6]; m = nums[0]\nfor x in nums: m = x if x > m else m\nprint(m)",
       overrides=[{"nums": [5, 3, 9, 1]}, {"nums": [-5, -2, -9]}],
       rules=[lambda t: calls(t, "max"),
              lambda t: not has(t, ast.For)])

script("q10", "count = 0\nfor x in [3, 8, 12, 5, 6]: count += (1 if x % 2 == 0 else 0)\nprint(count)",
       rules=[lambda t: not has(t, ast.For)])

script("q11", "res = 1\nfor _ in range(4): res *= 2\nprint(res)",
       rules=[lambda t: has(t, ast.Pow),
              lambda t: calls(t, "pow"),
              lambda t: not has(t, ast.For)])

# q12: no test (predict)

# ======================================================
# 4. Lists & Tuples
# ======================================================
script("q13", "nums = [1, 2, 3]\nprint([x * 2 for x in nums])",
       overrides=[{"nums": [5]}, {"nums": [0, -1, 4]}, {"nums": []}],
       rules=[lambda t: not has(t, ast.ListComp)])

script("q14", "res = []\nfor x in [1, 2, 2, 3, 3]: (res.append(x) if x not in res else None)\nprint(res)",
       rules=[lambda t: calls(t, "set"),
              lambda t: not has(t, ast.For)])

script("q15", "coords = (10, 20)\nx, y = coords\nprint(x, y)",
       overrides=[{"coords": (1, 2)}, {"coords": (-5, 0)}],
       rules=[lambda t: not any(isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Tuple)
                                and isinstance(n.value, ast.Name) for n in ast.walk(t))])

# q16: no test (predict)

# ======================================================
# 5. Dictionaries & Sets
# ======================================================
script("q17", "counts = {}\nfor ch in 'banana': counts[ch] = counts.get(ch, 0) + 1\nprint(counts)",
       rules=[lambda t: not (has(t, ast.Dict) or calls(t, "dict")),
              lambda t: calls(t, "Counter"),
              lambda t: not has(t, ast.For)])

script("q18", "print(list(set([1, 2, 3]) & set([2, 3, 4])))", sort=True,
       rules=[lambda t: not (has(t, ast.BitAnd) or calls_attr(t, "intersection"))])

script("q19", "grades = {'Ali': 90, 'Sara': 75}; top = 'Ali'\nfor name in grades: top = name if grades[name] > grades[top] else top\nprint(top)",
       overrides=[{"grades": {"Ali": 50, "Sara": 75, "Omar": 60}},
                  {"grades": {"Ali": 10, "Sara": 20, "Omar": 99}}])

# q20: no test (predict)

# ======================================================
# 6. Functions
# ======================================================
@test("q21")
def _(t, is_even):
    t(is_even(4) is True)
    t(is_even(7) is False)
    t(is_even(0) is True)
    t(is_even(-2) is True and is_even(-3) is False)


@test("q22")
def _(t, calc_avg):
    t(not func_calls(calc_avg, "sum"))
    t(math.isclose(calc_avg([10, 20, 30]), 20.0))
    t(math.isclose(calc_avg([1, 2]), 1.5))
    t(math.isclose(calc_avg([5]), 5))


@test("q23")
def _(t, calc_bill):
    t(math.isclose(calc_bill(100), 114.0))
    t(math.isclose(calc_bill(200), 228.0))
    t(math.isclose(calc_bill(50, 0.1), 55.0))
    t(math.isclose(calc_bill(0), 0))


# q24: no test (predict)

@test("q25")
def _(t, square):
    t(callable(square))
    t(getattr(square, "__name__", "") == "<lambda>")
    t(square(6) == 36)
    t(square(0) == 0 and square(-3) == 9)
    t(math.isclose(square(1.5), 2.25))


# ======================================================
# 7. OOP
# ======================================================
def _mk_student(cls, name, score):
    n = len(inspect.signature(cls).parameters)
    return cls(name, score) if n >= 2 else cls(score)


@test("q26")
def _(t, Student):
    s = Student("Omar", 95)
    t(s.name == "Omar")
    t(s.score == 95)
    u = Student("Sara", 40)
    t(u.name == "Sara" and u.score == 40)


@test("q27")
def _(t, Student):
    t(hasattr(Student, "is_passed"))
    t(_mk_student(Student, "Omar", 70).is_passed() is True)
    t(_mk_student(Student, "A", 50).is_passed() is True)
    t(_mk_student(Student, "B", 49).is_passed() is False)
    t(_mk_student(Student, "C", 0).is_passed() is False)


@test("q28")
def _(t, BankAccount):
    a = BankAccount()
    t(a.get_balance() == 0)
    a.deposit(50)
    t(a.get_balance() == 50)
    a.deposit(25)
    t(a.get_balance() == 75)
    t(not hasattr(a, "balance"))
    t(hasattr(a, f"_{type(a).__name__}__balance"))
    try:
        a.__balance
        private = False
    except AttributeError:
        private = True
    t(private)


@test("q29")
def _(t, Employee, Developer):
    t(Employee("Ali").name == "Ali")
    t(issubclass(Developer, Employee))
    d = Developer("Abdo", "Python")
    t(d.name == "Abdo")
    t(d.lang == "Python")
    t(isinstance(d, Employee))


@test("q30")
def _(t, Shape, Square):
    t(Shape().area() == 0)
    t(issubclass(Square, Shape))
    t(Square(4).area() == 16)
    t(Square(5).area() == 25)
    t(Square.area is not Shape.area)
