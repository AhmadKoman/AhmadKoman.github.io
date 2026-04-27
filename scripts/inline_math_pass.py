#!/usr/bin/env python3
r"""
Rewrite `_posts/2026-04-27-bottom-up-corn.md` prose around single-line display math.

Goal: reduce the repetitive “sentence ending with ':' then a $$ block” rhythm by folding
short, single-line formulas into the preceding paragraph as inline math \( ... \).

This script is intentionally conservative:
- Never touches multi-line display equations (matrices, pipelines, etc.).
- Skips YAML front matter.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POST = ROOT / "_posts" / "2026-04-27-bottom-up-corn.md"


ARROW_CHAIN_RE = re.compile(r"\\rightarrow")
DANGLING_VERB_BEFORE_COLON_RE = re.compile(r",\s*giving\s*$", flags=re.IGNORECASE)


def strip_trailing_colon(sentence: str) -> str:
    base = sentence.rstrip()
    if base.endswith(":"):
        base = base[:-1].rstrip()

    # Avoid doubled punctuation like ", ... ."
    while len(base) >= 2 and base[-2:] in {",.", ",?", ",!", ".."}:
        base = base[:-1].rstrip()

    return base


def fold_sentence(sentence: str, tex: str) -> str:
    """
    Fold `tex` into `sentence`, which is assumed to end with ':' (possibly with stray commas).
    """
    base = strip_trailing_colon(sentence)

    # Sometimes the prose ends with an incomplete verb before the ':' ("..., giving:").
    tail_strip = DANGLING_VERB_BEFORE_COLON_RE.sub("", base).rstrip()

    low = tail_strip.lower().rstrip(".,;:")
    tex_strip = tex.strip()

    inline = f"\\( {tex_strip} \\)"

    base_for_join = tail_strip

    def comma_then_inline() -> str:
        return f"{base_for_join}, {inline}"

    def natural_definition_join() -> str:
        """
        Prefer em dashes for definitional sentences that used to end with ':'.

        This avoids the repetitive "... is, \\( ... \\)." rhythm.
        """
        base_trim = base_for_join.rstrip().rstrip(",")

        low_trim = base_trim.lower()

        if low_trim.endswith(" is"):
            stem = base_trim[: -len(" is")].rstrip()
            return f"{stem} is {inline}"

        if low_trim.endswith(" are"):
            stem = base_trim[: -len(" are")].rstrip()
            return f"{stem} are {inline}"

        if low_trim.endswith(" signal is therefore"):
            stem = base_trim[: -len(" signal is therefore")].rstrip()
            return f"{stem} signal is therefore {inline}"

        if low_trim.endswith(" is therefore"):
            stem = base_trim[: -len(" is therefore")].rstrip()
            return f"{stem} is therefore {inline}"

        if low_trim.endswith(" therefore"):
            stem = base_trim[: -len(" therefore")].rstrip()
            stem_low2 = stem.lower()
            if stem_low2.endswith(" is"):
                stem2 = stem[: -len(" is")].rstrip()
                return f"{stem2} is therefore {inline}"

            return f"{stem} therefore {inline}"

        # Catch-all definitional forms like "The X is:", "The convention is:", etc.
        return comma_then_inline() + "."

    if low.startswith("let "):
        stem_low = base_for_join.lower()
        if stem_low.endswith(" be"):
            stem = base_for_join[: -len(" be")].rstrip()
            return f"{stem} be {inline}"

        return f"{base_for_join}, so {inline}."

    if low.startswith("substituting"):
        # Typical source text: "Substituting ... gives:"
        if low.endswith(" gives"):
            stem = base_for_join[: -len(" gives")].rstrip()
            # Avoid inserting an awkward comma before "which" when the stem already ends with one.
            if stem.endswith(","):
                stem = stem[:-1].rstrip()
            stem_tail = stem.lower()
            if stem_tail.endswith("substituting the economic components of net carry"):
                return f"Substituting the economic components of net carry gives {inline}."

            return f"{stem}, which gives {inline}."

        tail = base_for_join.strip()
        tail_low = tail.lower()
        if tail_low.endswith("substituting the economic components of net carry"):
            return f"Substituting the economic components of net carry gives {inline}."

        if "substituting" in low and "balance sheet relation" in low:
            stem = base_for_join.strip()
            stem_low = stem.lower()
            if stem_low.endswith("relation"):
                stem3 = stem[: -len("relation")].rstrip().rstrip(",")
                stem3_low = stem3.lower()
                if stem3_low.endswith("the full balance sheet"):
                    stem4 = stem3[: -len("the full balance sheet")].rstrip()
                    stem4_low = stem4.lower()
                    if stem4_low.endswith(" gives"):
                        stem4 = stem4[: -len(" gives")].rstrip()
                    return f"{stem4} gives the full balance sheet relation, which expands to {inline}."

        return f"{base_for_join}, giving {inline}."

    if low.endswith(" written as"):
        stem = base_for_join[: -len(" written as")].rstrip()
        # Avoid doubling verbs like "... written as is ..."
        stem_low = stem.lower()
        if stem_low.endswith(" can therefore be"):
            stem = stem[: -len(" can therefore be")].rstrip()
            return f"{stem} can therefore be written as {inline}"
        if stem_low.endswith(" can be"):
            stem = stem[: -len(" can be")].rstrip()
            return f"{stem} can be written as {inline}"

        return f"{stem} is written as {inline}"

    if low.endswith(" must estimate"):
        stem = base_for_join[: -len(" must estimate")].rstrip()
        return f"{stem} must estimate {inline}"

    if low.endswith(" therefore built as"):
        stem = base_for_join[: -len(" therefore built as")].rstrip()
        stem_low = stem.lower()
        if stem_low.endswith(" is"):
            stem = stem[: -len(" is")].rstrip()
        elif stem_low.endswith(" are"):
            stem = stem[: -len(" are")].rstrip()

        return f"{stem} is therefore {inline}"

    if low.endswith(" built as"):
        stem = base_for_join[: -len(" built as")].rstrip()
        stem_low = stem.lower()
        if stem_low.endswith(" is"):
            stem = stem[: -len(" is")].rstrip()
        elif stem_low.endswith(" are"):
            stem = stem[: -len(" are")].rstrip()

        return f"{stem} is {inline}"

    if low.endswith(" carry period is"):
        stem = base_for_join[: -len(" carry period is")].rstrip()
        return f"{stem} carry period is {inline}"

    if low.endswith(" economic identity"):
        stem = base_for_join[: -len(" economic identity")].rstrip()
        return f"{stem} economic identity {inline}"

    if low.endswith(" balance sheet relation"):
        stem = base_for_join[: -len(" balance sheet relation")].rstrip()
        stem_low = stem.lower()
        if stem_low.endswith("the full"):
            stem2 = stem[: -len("the full")].rstrip().rstrip(",")
            stem2_low = stem2.lower()
            if stem2_low.endswith("gives"):
                stem3 = stem2[: -len("gives")].rstrip().rstrip(",")
                return f"{stem3} gives the full balance sheet relation, which expands to {inline}."

        return f"{stem} balance sheet relation {inline}."

    if low.endswith(" total use"):
        stem = base_for_join[: -len(" total use")].rstrip()
        return f"{stem} total use {inline}"

    if low.endswith(" total supply"):
        stem = base_for_join[: -len(" total supply")].rstrip()
        return f"{stem} total supply {inline}"

    if low.endswith(" near contract"):
        stem = base_for_join[: -len(" near contract")].rstrip()
        return f"{stem} near contract {inline}"

    if low.endswith(" far contract"):
        stem = base_for_join[: -len(" far contract")].rstrip()
        return f"{stem} far contract {inline}"

    if low.endswith(" carry multiplier"):
        stem = base_for_join[: -len(" carry multiplier")].rstrip()
        return f"{stem} carry multiplier {inline}"

    if low.endswith(" carry term"):
        stem = base_for_join[: -len(" carry term")].rstrip()
        return f"{stem} carry term {inline}"

    if low.endswith(" nearby value"):
        stem = base_for_join[: -len(" nearby value")].rstrip()
        return f"{stem} nearby value {inline}"

    if low.endswith(" fitted log price"):
        stem = base_for_join[: -len(" fitted log price")].rstrip()
        return f"{stem} fitted log price {inline}"

    if low.endswith(" observed market price is"):
        stem = base_for_join[: -len(" observed market price is")].rstrip()
        return f"{stem} observed market price is {inline}"

    if low.endswith(" pricing target is"):
        stem = base_for_join[: -len(" pricing target is")].rstrip()
        return f"{stem} pricing target is {inline}"

    if low.endswith(" model estimate is"):
        stem = base_for_join[: -len(" model estimate is")].rstrip()
        return f"{stem} model estimate is {inline}"

    if low.endswith(" ethanol estimate is"):
        stem = base_for_join[: -len(" ethanol estimate is")].rstrip()
        return f"{stem} ethanol estimate is {inline}"

    if low.endswith(" export estimate is"):
        stem = base_for_join[: -len(" export estimate is")].rstrip()
        return f"{stem} export estimate is {inline}"

    if low.endswith(" feed residual estimate is"):
        stem = base_for_join[: -len(" feed residual estimate is")].rstrip()
        return f"{stem} feed residual estimate is {inline}"

    if low.endswith(" anchor estimate is"):
        stem = base_for_join[: -len(" anchor estimate is")].rstrip()
        return f"{stem} anchor estimate is {inline}"

    if low.endswith(" log price"):
        stem = base_for_join[: -len(" log price")].rstrip()
        return f"{stem} log price {inline}"

    if low.endswith(" mispricing score"):
        stem = base_for_join[: -len(" mispricing score")].rstrip()
        return f"{stem} mispricing score {inline}"

    if low.endswith(" entry condition"):
        stem = base_for_join[: -len(" entry condition")].rstrip()
        return f"{stem} entry condition {inline}"

    if low.endswith(" exit condition"):
        stem = base_for_join[: -len(" exit condition")].rstrip()
        return f"{stem} exit condition {inline}"

    if low.endswith(" exit"):
        stem = base_for_join[: -len(" exit")].rstrip()
        return f"{stem} exit {inline}"

    if low.endswith(" unit"):
        stem = base_for_join[: -len(" unit")].rstrip()
        return f"{stem} unit {inline}"

    if low.endswith(" contribution"):
        stem = base_for_join[: -len(" contribution")].rstrip()
        return f"{stem} contribution {inline}"

    if low.endswith(" prior"):
        stem = base_for_join[: -len(" prior")].rstrip()
        return f"{stem} prior {inline}"

    if low.endswith(" delivery month is"):
        stem = base_for_join[: -len(" delivery month is")].rstrip()
        return f"{stem} delivery month is {inline}"

    if low.endswith(" angle gives"):
        stem = base_for_join[: -len(" angle gives")].rstrip()
        return f"{stem} angle gives {inline}"

    if low.endswith(" annual cycle"):
        stem = base_for_join[: -len(" annual cycle")].rstrip()
        return f"{stem} annual cycle {inline}"

    if low.endswith(" earlier returns"):
        stem = base_for_join[: -len(" earlier returns")].rstrip()
        return f"{stem} earlier returns {inline}"

    if low.endswith(" raw sign"):
        stem = base_for_join[: -len(" raw sign")].rstrip()
        return f"{stem} raw sign {inline}"

    if low.endswith(" tightness signal"):
        stem = base_for_join[: -len(" tightness signal")].rstrip()
        return f"{stem} tightness signal {inline}"

    # Avoid "... verb, \\( ... \\)." when the verb wants a direct object without a comma.
    if low.endswith(" was"):
        stem = base_for_join[: -len(" was")].rstrip()
        return f"{stem} was {inline}."

    if low.endswith(" were"):
        stem = base_for_join[: -len(" were")].rstrip()
        return f"{stem} were {inline}."

    if low.endswith(" covered"):
        stem = base_for_join[: -len(" covered")].rstrip()
        return f"{stem} covered {inline}."

    if low.endswith(" gives"):
        stem = base_for_join[: -len(" gives")].rstrip()
        stem_clean = stem.rstrip(",")

        # Avoid turning gerund subjects into comma splices ("Collecting ... gives ...").
        stem_clean_low = stem_clean.lower()
        if stem_clean_low.endswith("ing") or stem_clean.strip().lower().startswith(
            ("carrying ", "collecting ", "converting ", "combining ", "adding ", "subtracting ")
        ):
            return f"{stem_clean} gives {inline}."

        return f"{stem_clean}, which gives {inline}."

    if "approximated" in low:
        return comma_then_inline() + "."

    if "moving " in low or "isolate" in low:
        return comma_then_inline() + "."

    if (
        "built by" in low
        or "built from" in low
        or "dividing " in low
        or "subtracting " in low
        or "adding " in low
        or "multiplying " in low
    ):
        return comma_then_inline() + "."

    if low.startswith("therefore,"):
        # Avoid ugly doubled commas when the sentence already trails with ", ..."
        inner = base_for_join[len("Therefore,") :].strip()
        return f"Therefore {inner}, {inline}."

    if low.startswith("therefore "):
        return comma_then_inline() + "."

    if "derivative" in low or "\\partial" in tex:
        return comma_then_inline() + "."

    # Plain definitional lines ("The X is:", "For that reason ... estimate:")
    return natural_definition_join()


def transform(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    in_front_matter = False
    front_done = False

    while i < len(lines):
        line = lines[i]

        if not front_done:
            if line.strip() == "---":
                in_front_matter = not in_front_matter
                out.append(line)
                i += 1
                if not in_front_matter:
                    front_done = True
                continue
            out.append(line)
            i += 1
            continue

        # Detect: prose line ending with ':' + blank + $$ ... $$ (single line inside)
        if (
            i + 3 < len(lines)
            and lines[i].strip().endswith(":")
            and lines[i + 1].strip() == ""
            and lines[i + 2].strip() == "$$"
        ):
            prose = lines[i]
            j = i + 3
            body_lines: list[str] = []
            while j < len(lines) and lines[j].strip() != "$$":
                body_lines.append(lines[j])
                j += 1
            if j >= len(lines) or lines[j].strip() != "$$":
                out.append(line)
                i += 1
                continue

            if len(body_lines) != 1:
                out.extend(lines[i : j + 1])
                i = j + 1
                continue

            tex = body_lines[0].strip()

            # Keep arrow-chain summaries as display math for scanning (usually wide).
            if ARROW_CHAIN_RE.search(tex):
                out.extend(lines[i : j + 1])
                i = j + 1
                continue

            folded = fold_sentence(prose, tex)

            # Insert exactly one blank line around folded paragraphs (avoid triple blanks).
            if out and out[-1].strip() != "":
                out.append("")
            out.append(folded)
            out.append("")
            i = j + 1
            continue

        out.append(line)
        i += 1

    return out


def main() -> None:
    text = POST.read_text(encoding="utf-8")
    lines = text.splitlines()

    ends_with_nl = text.endswith("\n")

    new_lines = transform(lines)
    new_text = "\n".join(new_lines)
    new_text += "\n"

    POST.write_text(new_text, encoding="utf-8")


if __name__ == "__main__":
    main()
