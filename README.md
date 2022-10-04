# Settings

add a `.env` file in the src folder.

```
# Pepipost API key
API_KEY=

# Email settings
FROM_EMAIL=
FROM_NAME=
TO_EMAIL=
TO_NAME=


# Email address the results are sent to
RECEIVER_EMAIL=

```

# Deploy

## Create package

```sh
# Archive virtual environment
cd venv/lib/python3.8/site-packages
zip -r9 ../../../../remote-bot.zip .
cd ../../../../
# Add script to archive
zip -g ./remote-bot.zip -r src
```

## Update Lambda code

```sh
aws lambda update-function-code --function-name remote-bot --zip-file fileb://remote-bot.zip --publish
```