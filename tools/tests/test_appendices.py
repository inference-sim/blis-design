"""Appendices A and C and the size of the latest version, checked against v1.0.0's built page.

Each rule is a function that returns a list of problems, so a test can hand it a
deliberately broken input and see it fail, then hand it the real page and see it pass.
"""
import pathlib
import re
import tempfile
import unittest

from support import REPO, LATEST, LATEST_DIR

V1 = REPO / "v1.0.0/blis-target-design.html"
V2 = REPO / f"{LATEST_DIR}/blis-target-design.html"
EXCEPTIONS = REPO / "tools/size-exceptions.txt"

# The same pattern tools/check.py uses for a rule that is defined (not merely cited).
DEFINED = re.compile(
    r'<span class="inv">([A-Z]+(?:-[A-Z]+)?-?\d+)</span>\s*(?:<b>|<span class="stmt">| [A-Z])')
INDEXED = re.compile(
    r'<span class="inv">([A-Z]+(?:-[A-Z]+)?-?)(\d+)</span>(?:–(?:<span class="inv">)?(\d+)(?:</span>)?)?')

FATES = {"kept", "changed", "merged", "retired"}
# Retirement is allowed for X10 (no bottom-up merge), the KVS family (the KV-store
# repository is out of scope) and any rule named here after the maintainer agrees.
RETIRE_PREFIXES = ("KVS-",)
RETIRE_CANDIDATES = {"X10"}


def section(page, ident, next_ident=None):
    start = page.index(f'<h2 id="{ident}"')
    if next_ident and f'<h2 id="{next_ident}"' in page:
        return page[start:page.index(f'<h2 id="{next_ident}"')]
    end = page.find("</main>", start)
    return page[start:end if end > 0 else len(page)]


def split_appendix(page):
    """The page without Appendix A, and Appendix A's text."""
    a, b = page.index('<h2 id="appA"'), page.index('<h2 id="appB"')
    return page[:a] + page[b:], page[a:b]


def defined_ids(page):
    body, _ = split_appendix(page) if '<h2 id="appA"' in page else (page, "")
    return set(DEFINED.findall(body))


def expand_indexed(text):
    """Every rule ID an appendix lists, with ranges such as X1-9 expanded."""
    out = set()
    for prefix, first, last in INDEXED.findall(text):
        for n in range(int(first), int(last or first) + 1):
            out.add(f"{prefix}{n}")
    return out


def appendix_c_rows(page):
    """[(v1 id, fate, v2 id text, reason)] from the built Appendix C."""
    text = section(page, "appC")
    rows = []
    for tr in re.findall(r"<tr>(.*?)</tr>", text, re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)
        if len(cells) == 4:
            plain = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
            rows.append(tuple(plain))
    return rows


def row_ids(v1):
    """The identifiers a row stands for: `KVS-1 to KVS-7` is seven."""
    m = re.fullmatch(r"([A-Z]+(?:-[A-Z]+)?-?)(\d+) to \1(\d+)", v1)
    if m:
        return [f"{m.group(1)}{n}" for n in range(int(m.group(2)), int(m.group(3)) + 1)]
    return [v1]


def appendix_c_problems(v1_ids, v2_ids, rows):
    """Each v1.0.0 ID has one row with its fate, or has no row and is defined again (kept)."""
    problems = []
    seen = {}
    for v1, fate, v2, reason in rows:
        ids = row_ids(v1)
        for one in ids:
            seen[one] = seen.get(one, 0) + 1
        if fate not in FATES:
            problems.append(f"{v1}: fate {fate!r} is not one of {sorted(FATES)}")
        if fate == "merged" and v2 not in v2_ids:
            problems.append(f"{v1}: merged into {v2!r}, which {LATEST_DIR} does not define")
        if fate == "changed" and v2 not in v2_ids:
            problems.append(f"{v1}: changed as {v2!r}, which {LATEST_DIR} does not define")
        if fate == "retired" and not all(i in RETIRE_CANDIDATES or i.startswith(RETIRE_PREFIXES) for i in ids):
            problems.append(f"{v1}: retired, but it is not a retirement candidate")
        if not reason:
            problems.append(f"{v1}: no reason")
    for v1 in sorted(v1_ids):
        n = seen.get(v1, 0)
        if n > 1:
            problems.append(f"{v1}: {n} rows, expected at most 1")
        if n == 0 and v1 not in v2_ids:
            problems.append(f"{v1}: 0 rows and {LATEST_DIR} does not define it, so it is not kept")
    for v1 in sorted(set(seen) - set(v1_ids)):
        problems.append(f"{v1}: a row for an ID v1.0.0 does not define")
    return problems


def idmap_entries():
    """{v1 id: fate} from the source's id maps, for the fates that need a row."""
    out = {}
    for path in sorted((REPO / LATEST_DIR / "src/_idmap").glob("*.tsv")):
        for line in path.read_text().splitlines()[1:]:
            cells = line.split("\t")
            if len(cells) >= 2 and cells[1] in ("changed", "merged", "retired"):
                out[cells[0]] = cells[1]
    return out


def idmap_problems(entries, rows):
    """Every ID the id map says changed, merged or retired must have a row with that fate."""
    fates = {}
    for v1, fate, _, _ in rows:
        for one in row_ids(v1):
            fates[one] = fate
    return [f"{v1}: the id map says {fate}, the appendix says {fates.get(v1, 'nothing')}"
            for v1, fate in sorted(entries.items()) if fates.get(v1) != fate]


def unindexed(defined, appendix_a_text):
    return sorted(defined - expand_indexed(appendix_a_text))


def measure(page):
    return {
        "rule_ids": len(defined_ids(page)),
        "sections": len(re.findall(r'<h2 id="', page)),
        "kilobytes": len(page.encode()) // 1024,
    }


def read_exceptions(path):
    """{metric: reason} from lines of the form `metric: reason`; # starts a comment."""
    out = {}
    if pathlib.Path(path).is_file():
        for line in pathlib.Path(path).read_text().splitlines():
            line = line.split("#", 1)[0].strip()
            if ":" in line:
                key, reason = (s.strip() for s in line.split(":", 1))
                if reason:
                    out[key] = reason
    return out


def size_problems(v1, v2, exceptions):
    return [f"{key}: {v2[key]} exceeds v1.0.0's {v1[key]} and is not listed in size-exceptions.txt"
            for key in v1 if v2[key] > v1[key] and key not in exceptions]


class TestAppendixC(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v1_ids = defined_ids(V1.read_text())
        cls.page = V2.read_text()
        cls.v2_ids = defined_ids(cls.page)
        cls.rows = appendix_c_rows(cls.page)
        cls.entries = idmap_entries()

    def test_appendix_c_covers_every_v1_id(self):
        self.assertEqual(appendix_c_problems(self.v1_ids, self.v2_ids, self.rows), [])

    def test_a_missing_changed_or_retired_row_is_reported(self):
        for ident in ("X1", "X10"):
            rows = [r for r in self.rows if r[0] != ident]
            self.assertTrue(any(p.startswith(ident + ":") for p in
                                idmap_problems(self.entries, rows)), ident)

    def test_a_missing_retired_row_is_also_an_undefined_kept_id(self):
        rows = [r for r in self.rows if r[0] != "X10"]
        problems = appendix_c_problems(self.v1_ids, self.v2_ids, rows)
        self.assertTrue(any(p.startswith("X10:") for p in problems), problems)

    def test_a_kept_id_that_is_no_longer_defined_is_reported(self):
        kept = sorted(i for i in self.v1_ids if i not in {x for r in self.rows for x in row_ids(r[0])})
        self.assertTrue(kept)
        problems = appendix_c_problems(self.v1_ids, self.v2_ids - {kept[0]}, self.rows)
        self.assertTrue(any(p.startswith(kept[0] + ":") for p in problems), problems)

    def test_the_id_map_agrees_with_the_appendix(self):
        self.assertTrue(self.entries)
        self.assertEqual(idmap_problems(self.entries, self.rows), [])

    def test_a_kept_row_is_not_a_fate(self):
        v1, _, v2, reason = self.rows[0]
        problems = appendix_c_problems(self.v1_ids, self.v2_ids, [(v1, "kept", v2, reason)] + self.rows[1:])
        self.assertTrue(any("not one of" in p for p in problems), problems)

    def test_a_duplicate_row_is_reported(self):
        problems = appendix_c_problems(self.v1_ids, self.v2_ids, self.rows + [self.rows[0]])
        self.assertTrue(any("2 rows" in p for p in problems), problems)

    def test_an_unknown_fate_is_reported(self):
        v1, _, v2, reason = self.rows[0]
        problems = appendix_c_problems(self.v1_ids, self.v2_ids, [(v1, "dropped", v2, reason)] + self.rows[1:])
        self.assertTrue(any("not one of" in p for p in problems), problems)

    def test_a_merge_into_an_undefined_id_is_reported(self):
        v1, _, _, reason = self.rows[0]
        problems = appendix_c_problems(self.v1_ids, self.v2_ids, [(v1, "merged", "ZZZ-9", reason)] + self.rows[1:])
        self.assertTrue(any("does not define" in p for p in problems), problems)

    def test_retiring_an_ordinary_rule_is_reported(self):
        v1, _, _, reason = next(r for r in self.rows if r[0] == "X7")
        problems = appendix_c_problems(self.v1_ids, self.v2_ids, [(v1, "retired", "", reason)] +
                                       [r for r in self.rows if r[0] != "X7"])
        self.assertTrue(any("not a retirement candidate" in p for p in problems), problems)

    def test_the_known_retirements_are_recorded(self):
        fates = {i: r[1] for r in self.rows for i in row_ids(r[0])}
        for ident in ["X10"] + [f"KVS-{n}" for n in range(1, 8)]:
            self.assertEqual(fates.get(ident), "retired", ident)
        self.assertEqual(fates.get("T-P1"), "merged")


class TestAppendixA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = V2.read_text()
        cls.defined = defined_ids(cls.page)
        cls.appendix = split_appendix(cls.page)[1]

    def test_every_v2_rule_is_indexed(self):
        self.assertEqual(unindexed(self.defined, self.appendix), [])

    def test_a_dropped_identifier_is_reported(self):
        broken = self.appendix.replace('<span class="inv">COV-1</span>–<span class="inv">13</span>',
                                       '<span class="inv">COV-1</span>–<span class="inv">12</span>')
        self.assertNotEqual(broken, self.appendix)
        self.assertEqual(unindexed(self.defined, broken), ["COV-13"])

    def test_ranges_expand(self):
        self.assertEqual(expand_indexed('<span class="inv">X1</span>–<span class="inv">3</span>, '
                                        '<span class="inv">T-M1</span>–2'), {"X1", "X2", "X3", "T-M1", "T-M2"})

    def test_appendix_a_lists_no_retired_rule(self):
        listed = expand_indexed(self.appendix)
        self.assertEqual(sorted(listed - self.defined), [])


class TestSize(unittest.TestCase):
    def test_v2_is_not_larger_than_v1(self):
        v1, v2 = measure(V1.read_text()), measure(V2.read_text())
        self.assertEqual(size_problems(v1, v2, read_exceptions(EXCEPTIONS)), [])

    def test_an_unlisted_excess_is_reported(self):
        v1 = {"rule_ids": 10, "sections": 5, "kilobytes": 100}
        v2 = {"rule_ids": 11, "sections": 5, "kilobytes": 99}
        self.assertEqual(len(size_problems(v1, v2, {})), 1)
        self.assertEqual(size_problems(v1, v2, {"rule_ids": "a reason"}), [])

    def test_an_exception_without_a_reason_does_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "size-exceptions.txt"
            path.write_text("rule_ids:\n# a comment\n")
            self.assertEqual(read_exceptions(path), {})
            path.write_text("sections: Appendix C maps every earlier rule  # note\n")
            self.assertEqual(list(read_exceptions(path)), ["sections"])


if __name__ == "__main__":
    unittest.main()
