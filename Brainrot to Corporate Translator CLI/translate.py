#!/usr/bin/env python3

import sys
import os

if sys.platform == "win32":
    os.system("chcp 65001 > nul 2>&1")
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

import json
import re
import argparse
import random
from pathlib import Path

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.align import Align
    from rich.text import Text
    from rich.columns import Columns
    from rich import box
except ImportError:
    print("Error: 'rich' is not installed. Run:  pip install rich")
    sys.exit(1)

console = Console(legacy_windows=False)

RANDOM_EMAILS = [
    """\
Hi Team,

As we circle back on our Q3 synergy initiatives, I wanted to touch base regarding \
the low-hanging fruit we identified in our last alignment session. Going forward, \
let's ensure all stakeholders are leveraging our core competencies to move the needle \
on our key deliverables.

Action items: Please drill down into your pain points and provide value-add \
recommendations before our next deep dive. Let's take this offline if needed.

Best,
Chad from Finance""",

    """\
Dear All,

I wanted to proactively reach out to facilitate a paradigm shift in how we approach \
our bandwidth constraints. At the end of the day, our robust and scalable solutions \
need to be more agile. Let's ideate on best practices to ensure seamless delivery of \
our bleeding-edge, disruptive innovations. Let's align on this ASAP.

Regards,
Brenda, Director of Synergies""",

    """\
Hi,

Just wanted to loop you in on our deep dive around stakeholder synergy. We need to \
move the needle on transparency and leverage our core competencies. Please touch base \
with me to drill down on the pain points and circle back with your action items by EOD.

Per my last email, this is mission critical going forward. Thank you for your patience.

Thanks,
Derek""",

    """\
Team,

As per our last call, let's pivot our strategy and boil the ocean on ideation for our \
next paradigm shift. The bleeding-edge approach we've been exploring is a real game \
changer. Let's take this to the next level — reach out to all stakeholders to ensure \
we have the bandwidth to deliver this seamlessly and at scale.

Best,
Karen, VP of Innovative Synergies""",
]


def load_dictionary() -> dict:
    dict_path = Path(__file__).parent / "dictionary.json"
    try:
        with open(dict_path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[bold red]✗[/bold red] [red]dictionary.json not found.[/red] Keep it in the same folder as translate.py.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        console.print(f"[bold red]✗[/bold red] [red]dictionary.json is corrupted:[/red] {e}")
        sys.exit(1)


def translate(text: str, mapping: dict) -> tuple[str, int]:
    result = text
    total = 0
    for phrase in sorted(mapping.keys(), key=len, reverse=True):
        pattern = re.compile(r'\b' + re.escape(phrase) + r'\b', re.IGNORECASE)
        result, n = pattern.subn(mapping[phrase], result)
        total += n
    return result, total


def print_banner():
    console.print()
    console.print(
        Panel(
            Align.center(
                "[bold bright_magenta]Brainrot[/bold bright_magenta]"
                "[bold white] ↔ [/bold white]"
                "[bold bright_cyan]Corporate[/bold bright_cyan]"
                "[bold white] Translator[/bold white]\n"
                "[dim]making corp speak actually comprehensible (or not)[/dim]"
            ),
            box=box.DOUBLE_EDGE,
            border_style="bright_magenta",
            padding=(0, 6),
        )
    )
    console.print()


def print_translation(
    original: str,
    translated: str,
    from_label: str,
    to_label: str,
    count: int,
    accent: str,
):
    console.print(
        Panel(
            f"[dim]{original}[/dim]",
            title=f"[dim white] {from_label} [/dim white]",
            border_style="dim white",
            box=box.ROUNDED,
            padding=(1, 2),
        )
    )

    console.print(Align.center(f"[{accent}]▼  translating  ▼[/{accent}]"))
    console.print()

    if count == 0:
        no_match = (
            "[dim]No brainrot detected — suspiciously professional.[/dim]"
            if accent == "bright_cyan"
            else "[dim]No corporate speak detected — you're already speaking fluent internet.[/dim]"
        )
        console.print(
            Panel(
                Align.center(no_match),
                title=f"[{accent}] {to_label} [/{accent}]",
                border_style=accent,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )
    else:
        console.print(
            Panel(
                f"[bold {accent}]{translated}[/bold {accent}]",
                title=f"[{accent}] {to_label} [/{accent}]",
                border_style=accent,
                box=box.ROUNDED,
                padding=(1, 2),
            )
        )

    replaced_str = f"[dim]{count} phrase{'s' if count != 1 else ''} translated[/dim]"
    console.print(Align.right(replaced_str))
    console.print()


def main():
    parser = argparse.ArgumentParser(
        prog="translate",
        description="Brainrot ↔ Corporate — a two-way corporate jargon translator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python translate.py --mode brainrot \"Let's circle back on this synergy\"\n"
            "  python translate.py --mode corporate \"no cap, this is bussin fr\"\n"
            "  python translate.py --random"
        ),
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["brainrot", "corporate"],
        default="brainrot",
        metavar="MODE",
        help="brainrot = corp→slang  |  corporate = slang→corp  (default: brainrot)",
    )
    parser.add_argument(
        "--random", "-r",
        action="store_true",
        help="translate a random corporate email to brainrot for laughs",
    )
    parser.add_argument(
        "text",
        nargs="*",
        help="text to translate (wrap multi-word input in quotes)",
    )

    args = parser.parse_args()
    dictionary = load_dictionary()

    print_banner()

    if args.random:
        email = random.choice(RANDOM_EMAILS)
        translated, count = translate(email, dictionary["corp_to_slang"])
        print_translation(email, translated, "Corporate Email", "Brainrot Edition", count, "bright_green")
        return

    if not args.text:
        console.print("[yellow]No input provided.[/yellow] Pass some text, or try [bold]--random[/bold] for a laugh.\n")
        parser.print_help()
        return

    input_text = " ".join(args.text)

    if args.mode == "brainrot":
        translated, count = translate(input_text, dictionary["corp_to_slang"])
        print_translation(input_text, translated, "Corporate", "Brainrot", count, "bright_green")
    else:
        translated, count = translate(input_text, dictionary["slang_to_corp"])
        print_translation(input_text, translated, "Brainrot", "Corporate", count, "bright_cyan")


if __name__ == "__main__":
    main()
