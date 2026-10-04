# Sample Job Dataset

`jobs_dataset.csv` contains 20 illustrative early-career and internship records for local matching demonstrations. Every bundled record uses `source_type=sample_dataset`; organizations and openings are examples, not verified employers or live vacancies. CareerAssist does not scrape job sites or call a paid job API.

## Adding a record

Add one CSV row with all of these columns, keeping commas inside quoted CSV fields:

- `job_id`: unique identifier.
- `job_title`: role name used for title search.
- `company`: organization label. Mark illustrative organizations clearly.
- `job_type`: for example `Internship`, `Entry-level`, or `Graduate program`.
- `experience_level`: for example `Internship`, `Entry-level`, or `Fresh graduate`.
- `location`: short location or work arrangement such as `Remote` or `Hybrid`.
- `required_skills`: comma-separated skill phrases used for exact overlap.
- `preferred_skills`: comma-separated optional skill phrases.
- `job_description`: concise responsibilities and requirements.
- `application_url`: leave empty unless you are adding a real, verified link.
- `source_type`: use `sample_dataset` for demonstrations; use an accurate source label for any records you independently verify.

The loader checks the required headers when the app starts loading jobs. The matcher does not treat a score as a hiring probability.
