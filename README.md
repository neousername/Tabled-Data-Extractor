# Table Data Extractor

main script passes the PNG's from "Screenshots" directory to the gemini model which returns a json dictionary based on the data. To be able to convert the data cleanly to an excel format all headers to the dictionary MUST be specified inside of the ai_prompt.py file and adjusted according to the tabled data.

- USE cleanup_cloud.py to clean remaining files in case of premature interuption
- USE json_to_excel.py after all PNG's are analyzed.
- STORE your API Key inside of a creds.py file (WHICH SHOULD BE INCLUDED IN .gitignore)

There are 20 workers passing the pictures to the server in parallel. Adjust the amount in the main.py script as needed.
