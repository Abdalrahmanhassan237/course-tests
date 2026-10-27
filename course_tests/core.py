_REG = {}

def test(qid):
    def deco(fn):
        _REG[qid] = fn
        return fn
    return deco

def check(qid, obj):
    if qid not in _REG:
        print(f"⚠️ مفيش سؤال اسمه {qid}")
        return
    try:
        _REG[qid](obj)
        print("✅ Passed — برافو!")
    except AssertionError as e:
        print(f"❌ Failed — {e or 'الناتج مش صح، جرّب تاني'}")
    except Exception as e:
        print(f"❌ Failed — حصل خطأ: {type(e).__name__}: {e}")
