# IMC Prosperity 3

This repository contains the [IMC Prosperity 3](https://prosperity.imc.com/) code of my solo team named "camel_case".

Final position: 25th overall, 8th in Europe, 1st in the Netherlands.

I released several open-source tools during the competition, all based on my open-source tooling for Prosperity 2:
- [jmerle/imc-prosperity-3-visualizer](https://github.com/jmerle/imc-prosperity-3-visualizer) is a visualizer for results of submissions and local backtests (available online at [jmerle.github.io/imc-prosperity-3-visualizer/](https://jmerle.github.io/imc-prosperity-3-visualizer/)).
- [jmerle/imc-prosperity-3-backtester](https://github.com/jmerle/imc-prosperity-3-backtester) is a backtester that allows locally running algorithms on the provided data files.
- [jmerle/imc-prosperity-3-submitter](https://github.com/jmerle/imc-prosperity-3-submitter) is a CLI that allows submitting algorithms from the command-line.
- [jmerle/imc-prosperity-3-leaderboard](https://github.com/jmerle/imc-prosperity-3-leaderboard) is an alternative leaderboard viewer (available online at [jmerle.github.io/imc-prosperity-3-leaderboard/](https://jmerle.github.io/imc-prosperity-3-leaderboard/)).

I've also written an optimizer, available in the [jmerle/imc-prosperity-3-optimizer](https://github.com/jmerle/imc-prosperity-3-optimizer) repository, which I planned to open-source but never actually got to a state where I was comfortable doing so. It's in a usable state, I used it for some rounds, but it's a bit rough around the edges, partially undocumented, and lacking some key optimizations.

## Project structure

```
.
├── logs                Archive of submission and end-of-round logs
├── prosperity3
│   ├── algorithms      Algorithm code for algo rounds
│   │   ├── empty.py    An algorithm that does nothing
│   │   └── hybrid.py   The file I worked on during algo rounds
│   ├── analysis        Notebooks for algo rounds
│   ├── manual          Notebooks for manual rounds
│   └── submissions     Archive of code submitted to algo rounds
└── README.md           You are here
```

## Round results

### Profit / loss

| Round | Overall | Manual | Algo | Round |
|-|-|-|-|-|
| 1 (before rerun) | 49,731 | 44,340 | 5,391 | 49,731 |
| 1 (after rerun) | 105,941 | 44,340 | 61,601 | 105,941 |
| 2 (before hardcoding update) | 219,072 | 33,087 | 80,043 | 113,130 |
| 2 (after hardcoding update) | 219,072 | 33,087 | 80,043 | 113,130 |
| 3 (before manual update) | 404,906 | 53,430 | 132,403 | 185,833 |
| 3 (after manual update) | 404,906 | 53,430 | 132,403 | 185,833 |
| 4 | 591,357 | 51,801 | 134,650 | 186,451 |
| 5 | 981,993 | 36,998 | 353,637 | 390,636 |

### Leaderboard positions

| Round | Overall | Manual | Algo | Country (NL) |
|-|-|-|-|-|
| 1 (before rerun) | 1,508 | 272 | 1,759 | 57 |
| 1 (after rerun) | 14 | 272 | 14 | 2 |
| 2 (before hardcoding update) | 53 | 698 | 44 | 4 |
| 2 (after hardcoding update) | 53 | 698 | 43 | 4 |
| 3 (before manual update) | 168 | 574 | 180 | 5 |
| 3 (after manual update) | 161 | 456 | 180 | 5 |
| 4 | 83 | 517 | 89 | 2 |
| 5 | 25 | 599 | 18 | 1 |

### Links

| Round | Code | Submission visualized | Final visualized |
|-|-|-|-|
| 1 (before rerun) | [Link](https://github.com/jmerle/imc-prosperity-3/blob/master/prosperity3/submissions/round1.py) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round1-submission.log) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round1-final-before-rerun.log) |
| 1 (after rerun) | Same as above | Same as above | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round1-final-after-rerun.log) |
| 2 (before hardcoding update) | [Link](https://github.com/jmerle/imc-prosperity-3/blob/master/prosperity3/submissions/round2.py) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round2-submission.log) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round2-final-before-rerun.log) |
| 2 (after hardcoding update) | Same as above | Same as above | Same as above |
| 3 (before manual update) | [Link](https://github.com/jmerle/imc-prosperity-3/blob/master/prosperity3/submissions/round3.py) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round3-submission.log) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round3-final.log) |
| 3 (after manual update) | Same as above | Same as above | Same as above |
| 4 | [Link](https://github.com/jmerle/imc-prosperity-3/blob/master/prosperity3/submissions/round4.py) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round4-submission.log) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round4-final.log) |
| 5 | [Link](https://github.com/jmerle/imc-prosperity-3/blob/master/prosperity3/submissions/round5.py) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round5-submission.log) | [Link](https://jmerle.github.io/imc-prosperity-3-visualizer/?open=https://raw.githubusercontent.com/jmerle/imc-prosperity-3/master/logs/round5-final.log) |

### Profit / loss by product

| Round | RAINFOREST_RESIN | KELP | SQUID_INK | CROISSANTS | JAMS | DJEMBES | PICNIC_BASKET1 | PICNIC_BASKET2 | VOLCANIC_ROCK | VOLCANIC_ROCK_VOUCHER_9500 | VOLCANIC_ROCK_VOUCHER_9750 | VOLCANIC_ROCK_VOUCHER_10000 | VOLCANIC_ROCK_VOUCHER_10250 | VOLCANIC_ROCK_VOUCHER_10500 | MAGNIFICENT_MACARONS |
|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|-|
| 1 (before rerun) | 18,312 | 4,952 | -17,873 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 (after rerun) | 38,970 | 4,363 | 18,268 | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 (before hardcoding update) | 37,000 | 5,181 | 894 | -3,003 | 10,581 | -4,045 | 39,940 | -6,504 | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 (after hardcoding update) | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 (before manual update) | 36,939 | 4,667 | -7,326 | 0 | -34,429 | 0 | 13,912 | -5,964 | 105,806 | 24,176 | 14,334 | -11,632 | -6,595 | -1,485 | N/A |
| 3 (after manual update) | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | Same as above | N/A |
| 4 | 37,575 | 4,383 | 0 | 0 | 0 | 0 | 14,790 | 0 | 48,195 | 26,414 | 27,482 | -18,349 | -5,840 | 0 | 0 |
| 5 | 38,865 | 5,846 | 5,695 | 18,307 | 0 | 0 | 6,010 | 0 | 109,744 | 29,976 | 30,601 | 28,517 | 5,727 | -2,677 | 77,028 |
