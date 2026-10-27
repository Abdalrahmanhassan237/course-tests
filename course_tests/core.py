import ast
import contextlib
import io
import textwrap
import inspect
from IPython import get_ipython

_REG, _SCRIPTS = {}, {}


class _Fail(Exception):
    def __init__(self, n):
        self.n = n


class _T:
    """Counts tests in order: t(condition) -> passes or raises _Fail(n)"""
    def __init__(self):
        self.n = 0

    def __call__(self, cond):
        self.n += 1
        if not cond:
            raise _Fail(self.n)


# ---------- registration ----------
def test(qid):
    """For functions / classes. The test receives (t, *student_objects)."""
    def deco(fn):
        _REG[qid] = fn
        return fn
    return deco


def script(qid, ref, overrides=None, rules=(), sort=False):
    """For print-scripts: compares student's output with the reference solution."""
    _SCRIPTS[qid] = {"ref": ref, "ov": [{}] + (overrides or []),
                     "rules": list(rules), "sort": sort}


# ---------- AST helpers ----------
def has(tree, *types):
    return any(isinstance(n, types) for n in ast.walk(tree))


def calls(tree, name):
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
               and n.func.id == name for n in ast.walk(tree))


def calls_attr(tree, name):
    return any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == name for n in ast.walk(tree))


def func_calls(fn, name):
    try:
        tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
    except Exception:
        return False
    return calls(tree, name)


# ---------- running student code ----------
def _is_lit(node):
    try:
        ast.literal_eval(node)
        return True
    except Exception:
        return False


def _lit(v):
    return ast.parse(repr(v), mode="eval").body


def _override(tree, ov):
    n = 0
    for node in tree.body:
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        t, v = node.targets[0], node.value
        if isinstance(t, ast.Name) and t.id in ov and _is_lit(v):
            node.value = _lit(ov[t.id])
            n += 1
        elif (isinstance(t, ast.Tuple) and isinstance(v, ast.Tuple)
              and len(t.elts) == len(v.elts)):
            for i, (te, ve) in enumerate(zip(t.elts, v.elts)):
                if isinstance(te, ast.Name) and te.id in ov and _is_lit(ve):
                    v.elts[i] = _lit(ov[te.id])
                    n += 1
    return n


def _run(code, ov):
    tree = ast.parse(code)
    tree.body = [
        n for n in tree.body
        if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                and isinstance(n.value.func, ast.Name)
                and n.value.func.id == "check")
    ]
    n = _override(tree, ov) if ov else 0
    ast.fix_missing_locations(tree)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(tree, "<student>", "exec"), {"__name__": "__main__"})
    return buf.getvalue(), n


def _norm(out):
    return "\n".join(l.rstrip() for l in out.strip().splitlines())


def _same(got, exp, sort):
    got, exp = _norm(got), _norm(exp)
    if got == exp:
        return True
    try:
        g, e = ast.literal_eval(got), ast.literal_eval(exp)
    except Exception:
        return False
    if sort:
        try:
            g, e = sorted(g), sorted(e)
        except TypeError:
            return False
    return g == e


# ---------- checkers ----------
def _check_script(qid):
    spec = _SCRIPTS[qid]
    code = get_ipython().history_manager.input_hist_raw[-1]
    try:
        tree = ast.parse(code)
    except SyntaxError:
        raise _Fail(1)
    n = 0
    for ov in spec["ov"]:
        n += 1
        try:
            exp, _ = _run(spec["ref"], ov)
            got, k = _run(code, ov)
        except Exception:
            raise _Fail(n)
        if ov and k == 0:
            continue
        if not _same(got, exp, spec["sort"]):
            raise _Fail(n)
    for bad in spec["rules"]:
        n += 1
        if bad(tree):
            raise _Fail(n)


def check(qid, *objs):
    t = _T()
    try:
        if qid in _SCRIPTS:
            _check_script(qid)
        elif qid in _REG:
            _REG[qid](t, *objs)
        else:
            print(f"Unknown question: {qid}")
            return
        print("✅ All tests passed")
    except _Fail as f:
        print(f"❌ Test {f.n} failed")
    except Exception:
        print(f"❌ Test {t.n + 1} failed")
