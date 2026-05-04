# Human-Readable Test Cases

This document is the readable companion to the YAML fixtures in `backend/tests/cases/`. When a fixture case changes, update this document in the same checkpoint.

## Bidding Cases

All bidding cases use system `expert_2over1`, dealer `n`, vulnerability `none`, and IMP scoring unless otherwise noted.

### transfer_to_hearts_superaccept_is_selected

- Auction: `1NP2DP` (`1N P 2D P`)
- Hand: `♠ AQ74  ♥ KJ83  ♦ A62  ♣ Q5`
- Expected call: `3H`
- Expected rule: `superaccept_hearts`
- Expected gadget: `four_way_jacoby_transfer`
- Expected compared calls: `3H`, `2H`
- Expected semantic facts: `notrump_opening`, `transfer`
- Expected selected criterion includes: `pending_heart_transfer`

### transfer_to_hearts_normal_completion_is_selected

- Auction: `1NP2DP` (`1N P 2D P`)
- Hand: `♠ AKQ  ♥ 83  ♦ Q762  ♣ KJ54`
- Expected call: `2H`
- Expected rule: `complete_hearts`
- Expected semantic facts: `notrump_opening`, `transfer`

### responder_uses_2d_transfer_with_five_hearts

- Auction: `1NP` (`1N P`)
- Hand: `♠ 74  ♥ KJ832  ♦ A762  ♣ Q5`
- Expected call: `2D`
- Expected rule: `transfer_hearts_2D`
- Expected gadget: `four_way_jacoby_transfer`
- Expected selected criterion includes: `jacoby_transfer_heart_length`

### notrump_opening_seat_1

- Auction: empty auction
- Hand: `♠ AQ7  ♥ KJ8  ♦ A762  ♣ Q54`
- Expected call: `1N`
- Expected rule: `open_1N`

### notrump_opening_seat_2

- Auction: `P`
- Hand: `♠ AQ7  ♥ KJ8  ♦ A762  ♣ Q54`
- Expected call: `1N`
- Expected rule: `open_1N`

### notrump_opening_seat_3

- Auction: `PP` (`P P`)
- Hand: `♠ AQ7  ♥ KJ8  ♦ A762  ♣ Q54`
- Expected call: `1N`
- Expected rule: `open_1N`

### notrump_opening_seat_4

- Auction: `PPP` (`P P P`)
- Hand: `♠ AQ7  ♥ KJ8  ♦ A762  ♣ Q54`
- Expected call: `1N`
- Expected rule: `open_1N`

### notrump_2n_opening

- Auction: empty auction
- Hand: `♠ AK7  ♥ KJ8  ♦ AQ76  ♣ K54`
- Expected call: `2N`
- Expected rule: `open_2N`

### one_heart_opening_seat_1_2

- Auction: empty auction
- Hand: `♠ K2  ♥ AKQ87  ♦ 765  ♣ 432`
- Expected call: `1H`
- Expected rule: `open_1H_seat_1_2`

### one_spade_opening_seat_1_2

- Auction: empty auction
- Hand: `♠ AKQ87  ♥ 32  ♦ 765  ♣ K32`
- Expected call: `1S`
- Expected rule: `open_1S_seat_1_2`

### one_club_opening_seat_1_2

- Auction: empty auction
- Hand: `♠ A32  ♥ KQ7  ♦ 865  ♣ K432`
- Expected call: `1C`
- Expected rule: `open_1C_seat_1_2`

### one_diamond_opening_seat_1_2

- Auction: empty auction
- Hand: `♠ A432  ♥ KQ7  ♦ K432  ♣ 65`
- Expected call: `1D`
- Expected rule: `open_1D_seat_1_2`

### one_major_placeholder_seat_3_4

- Auction: `PP` (`P P`)
- Hand: `♠ 432  ♥ 8765  ♦ 765  ♣ 432`
- Environment override: `enable_placeholder_openings: true`
- Expected call: `1H`
- Expected rule: `open_1M_seat_3_4_placeholder`

### one_minor_placeholder_seat_3_4

- Auction: `PPP` (`P P P`)
- Hand: `♠ 432  ♥ 876  ♦ 7654  ♣ 432`
- Environment override: `enable_placeholder_openings: true`
- Expected call: `1C`
- Expected rule: `open_1m_seat_3_4_placeholder`

### strong_two_club_opening

- Auction: empty auction
- Hand: `♠ AKQ  ♥ AKQ  ♦ AKQ7  ♣ 543`
- Expected call: `2C`
- Expected rule: `open_2C`

### weak_two_diamond_opening

- Auction: empty auction
- Hand: `♠ J32  ♥ 87  ♦ KQ9876  ♣ 54`
- Expected call: `2D`
- Expected rule: `open_2D`

### weak_two_heart_opening

- Auction: empty auction
- Hand: `♠ J32  ♥ KQ9876  ♦ 87  ♣ 54`
- Expected call: `2H`
- Expected rule: `open_2H`

### weak_two_spade_opening

- Auction: empty auction
- Hand: `♠ KQ9876  ♥ J32  ♦ 87  ♣ 54`
- Expected call: `2S`
- Expected rule: `open_2S`

### notrump_response_expands_by_seat_position

- Auction: `PP1NP` (`P P 1N P`)
- Hand: `♠ 74  ♥ KJ832  ♦ A762  ♣ Q5`
- Expected call: `2D`
- Expected rule: `transfer_hearts_2D`

### notrump_continuation_expands_by_seat_position

- Auction: `PP1NP2DP` (`P P 1N P 2D P`)
- Hand: `♠ AQ74  ♥ KJ83  ♦ A62  ♣ Q5`
- Expected call: `3H`
- Expected semantic facts: `notrump_opening`, `transfer`

### responder_does_not_use_2d_transfer_with_four_hearts

- Auction: `1NP` (`1N P`)
- Hand: `♠ A74  ♥ KJ83  ♦ A762  ♣ Q5`
- Expected call: `P`
- Expected origin: `two_over_one/two_over_one@0.1.0:default_pass`
- Expected diagnostic contains: `defaulting to P`

### unmatched_auction_defaults_to_pass

- Auction: `1CP1D` (`1C P 1D`)
- Hand: `♠ A74  ♥ KJ83  ♦ A762  ♣ Q5`
- Expected call: `P`
- Expected algorithm: `default_policy`
- Expected diagnostics contain: `Undefined historical call 1D`, `defaulting to P`

## Matcher Cases

### seat_positions_expand_any_pattern

- Context pattern: `1HP`
- Seat positions: `3`, `4`
- Should match: `PP1HP`, `PPP1HP`
- Should reject: `1HP`, `P1HP`

## Hand Parser Cases

### Valid Hands

- `any_suit_order_and_10_alias`
  - Raw: `H8763SK10C2DAKQ987`
  - Parsed: `♠ KT  ♥ 8763  ♦ AKQ987  ♣ 2`
  - HCP: `12`

- `repeated_suit_sections_are_concatenated`
  - Raw: `S9S8HAKQJD7654C432`
  - Parsed: `♠ 98  ♥ AKQJ  ♦ 7654  ♣ 432`
  - HCP: `10`

- `void_marker_and_x_placeholders`
  - Raw: `SAKQJH-DxxxxCxxxxx`
  - Parsed: `♠ AKQJ  ♥ void  ♦ XXXX  ♣ XXXXX`
  - HCP: `10`

### Invalid Hands

- `wrong_card_count`: `SAKQHJT9D876C54` should report `Wrong number of cards`.
- `repeated_known_card`: `SASAHKQJTD987C654` should report `Repeated card`.
- `unknown_symbol`: `SAZHKQJTD987C654` should report `Unknown symbol`.
- `rank_before_suit`: `ASAKQHJT9D876C54` should report `Rank appears before suit marker`.
- `bad_single_one`: `S1HKQJTD987C65432` should report `use 10 or T`.
- `void_marker_with_cards`: `S-AHKQJTD987C654` should report `Void marker`.
- `dictionary_input_rejected`: dictionary-shaped input should report `compact string`.
