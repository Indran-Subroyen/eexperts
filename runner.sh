#!/bin/bash

# ====== VARIABLES ======
RUNNER_VERSION="2.317.0"
RUNNER_NAME="indran-runner"
REPO_URL="https://github.com/Indran-Subroyen/eexperts"
TOKEN=" A6Z6CJNUGXP6FNC7ADGZLCTJZZBYQ"
RUNNER_LABELS="self-hosted,linux,indran"

# ====== CREATE DIRECTORY ======
mkdir -p ~/actions-runner
cd ~/actions-runner || exit

# ====== DOWNLOAD RUNNER ======
curl -o actions-runner-linux-x64.tar.gz -L \
https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# ====== EXTRACT ======
tar xzf actions-runner-linux-x64.tar.gz

# ====== CONFIGURE RUNNER ======
./config.sh \
  --url $REPO_URL \
  --token $TOKEN \
  --name $RUNNER_NAME \
  --labels $RUNNER_LABELS \
  --unattended \
  --replace

# ====== INSTALL AS SERVICE ======
sudo ./svc.sh install
sudo ./svc.sh start

echo "✅ Runner setup complete!"