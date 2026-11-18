# Judge audit

Replay of 100 public labels each; FAIL is the positive class. Floors: κ ≥ 0.6, precision ≥ 0.8, recall ≥ 0.7.

| Judge | TP | FP | FN | TN | κ | Precision | Recall | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| tone_ok | 24 | 4 | 6 | 66 | 0.757 | 0.857 | 0.800 | usable for this replay |
| helpful | 9 | 0 | 21 | 70 | 0.375 | 1.000 | 0.300 | reject as gate |

Tone's observed failure rate 0.28 corrects to 0.30 with Rogan–Gladen. Helpful misses 21 of 30 human failures; its high precision does not compensate for low recall or κ.

| Case | Judge | Human | Adjudication and rubric action |
|---|---|---|---|
| H-008 | PASS | FAIL | Accept human label; define informal address and “check” as inconsistent with the tone standard. |
| H-017 | PASS | FAIL | Accept human label; explicitly cover overly familiar “nha” in refund announcements. |
| H-029 | PASS | FAIL | Accept human label; mark dismissive instructions such as “không cần nhắn thêm”. |
| H-042 | FAIL | PASS | Accept human label; a concise respectful refund and timing statement is acceptable. |
| H-051 | FAIL | PASS | Accept human label; a borrowed word alone is not a tone violation. |

These are adjudications against the supplied labels, not independent new human reviews. The public replay is not a held-out evaluation; obtain new blinded human labels before production use.
