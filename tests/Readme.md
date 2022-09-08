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

The issue with too big catalog size has been resolved. Make sure you have a `criteria` in your `contractdefinition` that matches your asset. If not, the catalog will explode (with product-edc release 0.1.1). Also don't use old expresions like `left` and rather new expression like `operandLeft`. The old writting would cause catalog requests to receive a 500 server error and by thus, making it unreachable.


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
