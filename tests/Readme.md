# Testing

## Command Line
```
# install dependencies
pip install requests pytest

# settings
export PROVIDER_EDC_BASE_URL=http://myserver:8186/api/v1/data
export PROVIDER_EDC_API_KEY=12345
export NR_OF_ASSETS=10

# run the test - requires a 'clean' EDC environment
python ./test_data_management_api.py 
```

# Some Testing Results

|nr of assets   | 0.1.1 raw catalog file size (postgres)    | 0.0.6 raw catalog size (in-memory)    |
|:-------------:|:-----------------------------------------:|:-------------------------------------:|
|**10**         | < 1 MB (asset:prop:id **100**)            | < 1 MB  (asset:prop:id 10)            |
|**50**         | 63 MB  (asset:prop:id **2500**)           | < 1 MB  (asset:prop:id 50)            |
|100            | 495 MB                                    | < 1 MB  (asset:prop:id 100)           |
|200            | out of heap space                         | < 1 MB  (asset:prop:id 200)           |

In () the number of matches of `asset:prop:id` in the catalog result.

Result with a 1:1:1 relation, meaning 1 asset -> 1 policy -> 1 contractdefinition.



# Vscode Testing
In your `.vscode/settings.json` add
```
"python.envFile": "${workspaceFolder}/.env"
```
and add the necessary `ENV` to there.
E.g.
```
PROVIDER_EDC_BASE_URL=http://myserver:8186/api/v1/data
PROVIDER_EDC_API_KEY=12345
```

### running tests in vscode
Do NOT run from top level. This will run into `missing module` problems.
Run from `tests` directory structure and it works.

### vscode test file naming
It seems Vscode only allows numbers at the end of the filename to be detected automatically, e.g.
`test_24_something.py` is NOT detected, whereas `test_something_24.py` is detected.
