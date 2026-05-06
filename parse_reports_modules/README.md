# Territory Growth Intelligence MAS

Modular Semrush report pipeline migrated from `main-original.py`.

## Structure

- `main.py` starts the pipeline.
- `app/config/` loads environment settings.
- `app/domains/` reads and cleans domain data.
- `app/browser/` creates the Selenium driver.
- `app/semrush/` contains login, search, navigation, selectors, and export actions.
- `app/processing/` parses CSV files and transforms reports.
- `app/reports/` writes Excel output.
- `app/utils/` contains retry, logging, scrolling, and progress state.

## Commands

```powershell
pip install -r requirements.txt
python main.py --mode full
python main.py --mode download
python main.py --mode process
python main.py --mode process --start 0 --end 5 --months 8
python main.py --mode process --start 10 --amount 5
```

Copy `.env.example` to `.env` and fill Semrush credentials and local paths before running Selenium downloads.
The application loads `.env` automatically with `python-dotenv`.

## Notes

- `--amount` is applied from `--start` when `--end` is not provided.
- `MONTH_YEAR` is the single report year used for Semrush month selection and downloaded file parsing.
- `process` mode skips missing CSV files and writes empty Excel reports with a warning instead of failing on the first absent file.
- `overview` parsing reads existing files from `downloads/overview`.
- Backlinks parsing helpers are legacy/import-only and are not part of the current Selenium export flow.
