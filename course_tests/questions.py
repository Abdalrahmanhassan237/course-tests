from .core import test

@test("q1")
def _(add):
    assert add(2, 3) == 5, "جرّب add(2, 3)"
    assert add(0, 0) == 0, "جرّب الأصفار"
    assert add(-1, 5) == 4, "الأرقام السالبة؟"

@test("q2")
def _(Counter):
    c = Counter()
    assert c.value == 0, "القيمة الابتدائية لازم تبقى 0"
    c.increment()
    c.increment()
    assert c.value == 2, "increment لازم تزوّد value بواحد"
    c.reset()
    assert c.value == 0, "reset لازم ترجّع value لـ 0"
