# Repo Analyzer and Interactive Description Navigator

##  Repo Analyzer
Entry Point: `python analyze_codebase.py`
- it will generate `analysis files`
    - analyzed_files: local cache of files to prvent rescanning on system error
    - combined_descriptions: the GPT generated descriptsion and filenames
    - unanalyzed _files: files that errored during analysis. Contains the error for troubleshooting

## Interactive Description Navigator
Entry Point: `system_explorer/generate_system_pages.py`
- it will generate a dir with all the web pages. `index.html` is the entry point for the site
- docs contains the files for github pages

# Helpers
- `helpers/reformatAnalyzedFiles.py` reformats the analyzed_files.json filenames if needed
