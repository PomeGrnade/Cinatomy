# Contributing to Cinatomy

Thanks for wanting to improve this. Here's how to help.

---

## Suggest a new dimension

Open an issue with the title **"[Dimension] your-idea-here"** and answer:

1. What does this dimension measure, in one sentence?
2. What's the 1-to-5 scale anchor (what does a 1 look like? a 5?)
3. Why can't it be derived from an existing dimension?
4. Which 3–5 films would you use to sanity-check it?

Good past examples of dimensions that got added: `photosensitivity_warnings`, `animal_harm`, `trailer_or_spoiler`. These came directly from user needs, not from the original design.

---

## Report a bad score

If a film's score on a specific dimension seems clearly wrong, open an issue with:

- Film title
- Dimension name
- Current value
- What you'd expect and why (e.g. "Memento scores 2 on `cognitive_requirement` but it requires active tracking of two timelines simultaneously — should be 4 or 5")

Note: scores are LLM-generated subjective reads, not ground truth, so "different from my opinion" is not a bug. The bar for a report is "clearly inconsistent with critical consensus."

---

## Extend the dataset

Want to add more films? The pipeline is fully open:

```bash
git clone https://github.com/YOUR_USERNAME/cinatomy
cd cinatomy
pip install -r requirements.txt
export GEMINI_API_KEY="your_key"

# Add film titles to input_movies.csv, then:
python generate_profiles.py
```

PRs with additional films are welcome — please include the input CSV and verify the output has no missing values before submitting.

---

## Code / pipeline improvements

Standard flow: fork → branch → PR. Please keep PRs focused — one thing at a time.

The only hard rule: don't change `generate_profiles.py` in a way that breaks the Pydantic schema, since that would make the output incompatible with the existing dataset.

---

## Questions

Use **GitHub Discussions**, not Issues, for open-ended questions ("I want to build X on top of this — any advice?"). Issues are for bugs and concrete proposals.
