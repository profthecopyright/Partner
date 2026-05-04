# Backend Test Workflow

Behavior tests are fixture-driven. Add bridge bidding examples to YAML files under `backend/tests/cases/` instead of editing Python test methods.

`backend/tests/test_cases.md` is the human-readable translation of the fixture cases. Update it in the same checkpoint whenever a fixture case changes.

## Bidding Cases

Add cases to `backend/tests/cases/bidding.yaml`.

Minimal shape:

```yaml
cases:
  - name: short_unique_name
    system: expert_2over1
    auction: 1NP
    hand: S74HKJ832DA762CQ5
    environment:
      dealer: n
      vulnerability: none
      scoring: IMP
    expected:
      call: 2D
```

Optional expectations include:

- `origin.rule_id`
- `origin.gadget_id`
- `origin.qualified_rule_id`
- `public_meaning.alertable`
- `compared_candidate_calls`
- `diagnostics`
- `diagnostics_include`
- `selected_algorithm`
- `semantic_fact_types`
- `semantic_fact_origins`
- `selected_criteria_include`

## Hand Parser Cases

Add compact-hand parser cases to `backend/tests/cases/hands.yaml`.

```yaml
valid:
  - name: repeated_suit_sections_are_concatenated
    hand: S9S8HAKQJD7654C432
    expected:
      spades: '98'

invalid:
  - name: repeated_known_card
    hand: SASAHKQJTD987C654
    error_contains: Repeated card
```

Raw hand strings use suit markers `S H D C` and rank text after each marker. Suit order is flexible. `10` and `T` both mean ten. `X` means an unknown small card placeholder. `-` marks a void suit section. Dictionary-shaped hands are not accepted as public/test input.

## Matcher Cases

Add pattern-expansion cases to `backend/tests/cases/matcher.yaml`.

```yaml
cases:
  - name: seat_positions_expand_any_pattern
    context:
      auction_pattern: "1HP"
      seat_positions: [3, 4]
    matches:
      - PP1HP
      - PPP1HP
    rejects:
      - 1HP
      - P1HP
```

## Run Tests

From the project root:

```text
$env:PYTHONPATH='backend'; C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover backend\tests
```
