#!/bin/bash
cd ~/Documents/Claude/Projects/Bestie
git add -A
git commit -m "update $(date '+%d/%m/%Y %H:%M')"
git push
netlify deploy --dir=. --prod
