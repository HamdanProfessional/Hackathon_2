#!/usr/bin/env python3
"""Generate Architecture Decision Record (ADR)."""
import argparse
from datetime import datetime
from pathlib import Path
import os

ADR_TEMPLATE = """# {adr_number}: {title}

**Status**: {status}
**Date**: {date}
**Decision Makers**: {decision_makers}
**Tags**: {tags}

---

## Context

{context}

**Problem Statement**:
{problem_statement}

**Constraints**:
{constraints}

---

## Decision

{decision}

**Chosen Option**: {chosen_option}

**Rationale**:
{rationale}

---

## Options Considered

### Option 1: {chosen_option} (CHOSEN)

**Description**:
{option1_description}

**Pros**:
- {option1_pros}

**Cons**:
- {option1_cons}

**Cost/Complexity**: {option1_complexity}

---

### Option 2: {option2_name}

**Description**:
{option2_description}

**Pros**:
- {option2_pros}

**Cons**:
- {option2_cons}

**Cost/Complexity**: {option2_complexity}

---

## Consequences

### Positive
- {consequences_positive}

### Negative
- {consequences_negative}

### Neutral
- {consequences_neutral}

---

## Implementation Notes

**Immediate Actions**:
1. {action1}
2. {action2}

**Migration Path** (if applicable):
{migration_path}

**Testing Strategy**:
{testing_strategy}

**Rollback Plan**:
{rollback_plan}

---

## References

- {reference1}
- {reference2}
"""

def generate_adr(
    title: str,
    context: str,
    problem: str,
    chosen: str,
    rationale: str,
    output_dir: Path,
    status: str = "Proposed"
):
    """Generate a new ADR file."""
    # Find next ADR number
    docs_dir = output_dir / "docs" / "adr"
    docs_dir.mkdir(parents=True, exist_ok=True)

    existing_adrs = sorted([f for f in docs_dir.glob("*.md") if f.name != "README.md"])
    next_num = len(existing_adrs) + 1
    adr_number = f"{next_num:03d}"

    # Create slug
    slug = title.lower().replace(" ", "-").replace("/", "-")[:50]

    # Generate ADR content
    content = ADR_TEMPLATE.format(
        adr_number=adr_number,
        title=title,
        status=status,
        date=datetime.now().strftime("%Y-%m-%d"),
        decision_makers=os.getenv("GIT_AUTHOR_NAME", "Development Team"),
        tags="#arch #backend",
        context=context,
        problem_statement=problem,
        constraints="- Budget constraints\n- Timeline constraints\n- Technical requirements",
        decision=f"We chose to use **{chosen}**.",
        chosen_option=chosen,
        rationale=rationale,
        option1_description=f"{chosen} approach",
        option1_pros="- Benefit 1\n- Benefit 2",
        option1_cons="- Drawback 1\n- Drawback 2",
        option1_complexity="Low/Medium/High",
        option2_name="Alternative approach",
        option2_description="Brief description of alternative",
        option2_pros="- Pro 1\n- Pro 2",
        option2_cons="- Con 1\n- Con 2",
        option2_complexity="Low/Medium/High",
        consequences_positive="- Benefit 1\n- Benefit 2",
        consequences_negative="- Tradeoff 1\n- Tradeoff 2",
        consequences_neutral="- Impact 1",
        action1="Action step 1",
        action2="Action step 2",
        migration_path="Describe migration path if applicable",
        testing_strategy="Describe testing approach",
        rollback_plan="Describe rollback strategy",
        reference1="[Related ADR-XXX]: Title and link",
        reference2="[Spec]: Path to relevant specification"
    )

    # Write ADR file
    adr_file = docs_dir / f"{adr_number}-{slug}.md"
    adr_file.write_text(content)

    print(f"Created ADR: {adr_file}")

    # Update ADR README
    readme = docs_dir / "README.md"
    if readme.exists():
        existing = readme.read_text()
    else:
        existing = "# Architecture Decision Records\n\n"

    new_entry = f"- [{adr_number}] {title} ({status})\n"
    if "- [000]" not in existing:
        existing = existing.replace("# Architecture Decision Records\n\n",
                                 "# Architecture Decision Records\n\n" + new_entry)
    else:
        existing = existing.replace("- [000] Example ADR", new_entry + "- [000] Example ADR")

    readme.write_text(existing)

    return adr_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Architecture Decision Record")
    parser.add_argument("title", help="ADR title")
    parser.add_argument("--context", help="Context and background")
    parser.add_argument("--problem", help="Problem statement")
    parser.add_argument("--chosen", help="Chosen option")
    parser.add_argument("--rationale", help="Rationale for decision")
    parser.add_argument("--status", default="Proposed", help="Status (Proposed/Accepted/Rejected)")
    parser.add_argument("--output", default=".", help="Output directory")

    args = parser.parse_args()

    generate_adr(
        title=args.title,
        context=args.context or "Add context here",
        problem=args.problem or "Describe the problem",
        chosen=args.chosen or "Chosen technology/approach",
        rationale=args.rationale or "Explain why this option was chosen",
        output_dir=Path(args.output),
        status=args.status
    )
