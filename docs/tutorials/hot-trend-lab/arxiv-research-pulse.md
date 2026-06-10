# arXiv Research Pulse

arXiv turns research attention into a measurable public time series. The useful
question is not whether a topic is "good"; it is whether the public preprint
stream changed enough to deserve a closer read.

## Research questions

| Question | DeTime component | Reader action |
|---|---|---|
| Which categories are structurally growing? | `trend` | prioritize a monthly field scan |
| Which categories are deadline-driven? | `season` | compare against conference calendars before writing |
| Which categories had unusual bursts? | `residual` | inspect titles and abstracts for the event behind the spike |
| Which topic deserves a column this week? | trend score plus residual event rank | open the query notebook and build a source card |

## Query protocol

The category notebook uses arXiv category queries such as:

| Query | Label | Main caveat |
|---|---|---|
| `cat:cs.AI` | artificial intelligence | broad category with mixed subfields |
| `cat:cs.LG` | machine learning | high volume can hide smaller subtopic moves |
| `cat:cs.CL` | language and LLMs | language-model releases can cluster around deadlines |
| `cat:cs.CV` | computer vision and video models | conference submission cycles matter |
| `cat:stat.ML` | statistical machine learning | overlaps with `cs.LG` for some methods |
| `cat:q-bio.QM` | quantitative biology methods | smaller base rate makes residuals more volatile |
| `cat:q-fin.ST` | statistical finance | useful comparison category for trading examples |
| `cat:econ.EM` | econometrics | lower volume requires careful spike reading |

The notebooks count monthly windows from the first day of each month to that
month's end. Cross-listed papers can appear in more than one category view, so
category charts should be read as field-specific public activity rather than a
deduplicated paper inventory.

The agent-topic notebook uses phrase queries such as `all:"AI agent"`,
`all:"coding agent"`, `all:"tool use"`, and `all:"agentic workflow"`. Query
wording is part of the measurement. If a phrase changes, treat the resulting
chart as a new series.

## Deadline context

Submission volume often clusters around conference deadlines and camera-ready
periods. A category spike should be read against the relevant calendar before it
is described as a research shift. The safest article structure is:

1. state the query and date window;
2. show the trend, seasonal cadence, and residual event;
3. inspect the top titles or abstracts behind the event;
4. say whether the spike looks deadline-driven, launch-driven, or topic-driven.

Paper counts are publication activity. They are not peer-review quality,
benchmark performance, or community consensus.

Non-core categories such as `q-bio.QM`, `q-fin.ST`, and `econ.EM` are included
as comparison baselines. They make it easier to see whether an AI spike is field
specific, cross-disciplinary, or part of a broader submission-cycle effect.

## Notebooks

Use [01 arXiv category pulse](notebooks/01_arxiv_category_pulse.md) for the
category view and [02 arXiv agent research pulse](notebooks/02_arxiv_agent_research_pulse.md)
for query-based agent topics.
