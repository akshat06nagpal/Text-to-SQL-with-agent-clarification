\# Text-to-SQL Agent with a Clarification Engine



A command-line agent that answers plain-English questions about a SQLite database.

When a question is ambiguous (for example, "top customers": by revenue or by number

of purchases?), it asks follow-up questions before writing any SQL, instead of

silently guessing.



Built as a learning project, using the Chinook sample database (a digital music store).



\## How it works



```

question

&#x20;  -> clarification check   (is this ambiguous? if so, ask the user)

&#x20;  -> SQL generation        (LLM writes a SQLite query from the schema)

&#x20;  -> validation            (only a single read-only SELECT is allowed)

&#x20;  -> read-only execution   (row limit + time limit)

&#x20;  -> one self-correction attempt if the query fails

```



\## Safety



\- The generated SQL is parsed with `sqlglot`, and anything other than a single

&#x20; `SELECT` is rejected (no `DROP`, `DELETE`, `UPDATE`, multiple statements, etc.).

\- The database is opened in read-only mode, so writes fail even if validation missed something.

\- Results are capped at 100 rows, and queries are aborted after 5 seconds.



\## Project structure



| File | Purpose |

|---|---|

| `schema.py` | Reads tables, columns, foreign keys and sample rows into text for the LLM |

| `llm.py` | The only file that calls the LLM (Gemini); includes retries and a local cache |

| `clarify.py` | Decides whether a question needs clarification and asks the user |

| `sql\_generator.py` | Turns a (clarified) question into SQL, and fixes failed queries |

| `validator.py` | Allows only a single safe SELECT statement |

| `executor.py` | Runs SQL read-only with row and time limits |

| `main.py` | The full interactive pipeline |

| `eval\_cases.py`, `evaluate.py` | Hand-written test set and evaluation script |

| `test\_validator.py` | Offline tests for the safety layer |



\## Setup



Requires Python 3.9+ and a free Gemini API key from Google AI Studio.



```

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

```



Set your API key:



```

\# Command Prompt

set GEMINI\_API\_KEY=your-key-here



\# PowerShell

$env:GEMINI\_API\_KEY = "your-key-here"

```



Then run:



```

python main.py

```



Example questions to try:

\- `How many tracks are in the Rock genre?` (clear, answered directly)

\- `Who are the top customers?` (ambiguous, the agent asks what "top" means)



The model name is set in one place (`MODEL` in `llm.py`). Model names change over

time, so update it if the API reports the model is not found.



\## Evaluation



The test set has 22 hand-written questions: 15 clear ones with gold SQL, and 7

deliberately ambiguous ones. Results are compared by the rows returned, not the

SQL text.



```

python evaluate.py --check-gold   # run the gold queries only (no API calls)

python evaluate.py --max 8        # run up to 8 new cases (saves progress)

python evaluate.py --report       # print saved results

```



\*\*Results:\*\* \_to be filled in after running the evaluation\_



\## Limitations



\- Built and tested only on the Chinook schema (11 tables). The whole schema is

&#x20; sent in the prompt, so larger databases would need table retrieval.

\- The free Gemini tier has a small daily request limit, so evaluation runs are

&#x20; spread over several days (progress and LLM replies are cached locally).

\- The clarification step relies on the LLM's judgement, so it can over-ask or

&#x20; under-ask. The evaluation measures both.



\## Credits



Uses the Chinook sample database. Source: https://github.com/lerocha/chinook-database.

