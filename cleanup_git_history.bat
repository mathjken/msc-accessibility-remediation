@echo off
echo === Removing tracked large or sensitive files ===
git rm --cached .env
git rm --cached data\violations_urls.csv
git rm --cached violations_urls_critical.csv
git rm --cached data\filtered_violations_131_412.json
git rm --cached filtered_violations_131_412_critical.json

echo === Committing removal ===
git commit -m "Remove large files and .env from Git history"

echo === Rewriting Git history to purge those files ===
git filter-branch --force --index-filter ^
"git rm --cached --ignore-unmatch .env data/violations_urls.csv violations_urls_critical.csv data/filtered_violations_131_412.json filtered_violations_131_412_critical.json" ^
--prune-empty --tag-name-filter cat -- --all

echo === Forcing push to GitHub ===
git push origin --force

echo ✅ Done! Your Git repo is cleaned and pushed.
pause