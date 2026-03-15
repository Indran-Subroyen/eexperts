# CI/CD Pipeline

## Overview

```
Push to main → CI (test → build → push) → CD (dev → staging → prod)
```

## Workflows

| File | Purpose | Trigger |
|------|---------|---------|
| `ci.yml` | Run tests, build Docker image, push to dev registry | Push to main, PRs |
| `cd.yml` | Deploy to dev → staging → prod | After CI passes on main, or manual dispatch |
| `deployment.yml` | Reusable deploy logic (called by cd.yml) | Not triggered directly |

## Environment Setup

Create three environments in GitHub repo settings:
**Settings → Environments**

| Environment | Auto deploy | Approval required |
|-------------|-------------|-------------------|
| dev | Yes | No |
| staging | Yes | No |
| production | No | Yes — add required reviewers |

## Variables Reference

### Workflow-level (set in ci.yml)

| Variable | Value | Description |
|----------|-------|-------------|
| `IMAGE_NAME` | `gists-api` | Docker image name |
| `PYTHON_VERSION` | `3.12` | Python version for tests |

### Environment variables (set per environment in GitHub Settings)

Set these under **Settings → Environments → [env name] → Environment variables**:

| Variable | Example (dev) | Example (staging) | Example (prod) |
|----------|--------------|-------------------|----------------|
| `ACR_LOGIN_SERVER` | `acrdev.azurecr.io` | `acrstaging.azurecr.io` | `acrprod.azurecr.io` |
| `AKS_RESOURCE_GROUP` | `rg-dev` | `rg-staging` | `rg-prod` |
| `AKS_CLUSTER_NAME` | `aks-dev` | `aks-staging` | `aks-prod` |

### Environment secrets (set per environment in GitHub Settings)

Set these under **Settings → Environments → [env name] → Environment secrets**:

| Secret | Description |
|--------|-------------|
| `ACR_USERNAME` | Azure Container Registry username |
| `ACR_PASSWORD` | Azure Container Registry password |
| `AZURE_CLIENT_ID` | Service principal / managed identity client ID |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

## How Variables Are Scoped

```yaml
# In the workflow, when a job specifies an environment:
jobs:
  deploy:
    environment: dev    # ← this scopes vars.* and secrets.* to dev

    steps:
      - run: echo ${{ vars.ACR_LOGIN_SERVER }}
        # resolves to acrdev.azurecr.io (dev value)
```

Same workflow, same code — different values per environment. This is why `deployment.yml` works for all three environments without any if/else logic.

## Manual Dispatch

CD can be triggered manually via **Actions → CD → Run workflow**:

| Input | Description | Default |
|-------|-------------|---------|
| `deploy_dev` | Deploy to dev | true |
| `deploy_staging` | Deploy to staging | true |
| `deploy_prod` | Deploy to production | false |
| `image_tag` | Image tag (git SHA) to deploy | required |

This allows deploying to specific environments without going through the full chain — useful for hotfixes or redeploying a previous version.
