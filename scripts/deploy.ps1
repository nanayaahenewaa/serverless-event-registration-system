param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("dev", "prod")]
    [string]$Stage
)

$ErrorActionPreference = "Stop"

Write-Host "==> Running unit tests..." -ForegroundColor Cyan
python -m pytest tests/unit/ -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Aborting deployment." -ForegroundColor Red
    exit 1
}

Write-Host "==> Linting..." -ForegroundColor Cyan
flake8 src/ --max-line-length=100 --extend-ignore=E203
if ($LASTEXITCODE -ne 0) {
    Write-Host "Lint failed. Aborting deployment." -ForegroundColor Red
    exit 1
}

Write-Host "==> Validating SAM template..." -ForegroundColor Cyan
sam validate --lint
if ($LASTEXITCODE -ne 0) {
    Write-Host "Template validation failed. Aborting deployment." -ForegroundColor Red
    exit 1
}

Write-Host "==> Building..." -ForegroundColor Cyan
sam build
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host "==> Deploying to $Stage..." -ForegroundColor Cyan

if ($Stage -eq "prod") {
    $confirm = Read-Host "You are about to deploy to PRODUCTION. Type 'yes' to continue"
    if ($confirm -ne "yes") {
        Write-Host "Deployment cancelled." -ForegroundColor Yellow
        exit 0
    }
    sam deploy --stack-name event-registration-ticketing-prod `
        --capabilities CAPABILITY_IAM --no-confirm-changeset `
        --no-fail-on-empty-changeset --resolve-s3 `
        --parameter-overrides Stage=prod ThrottlingRateLimit=20 ThrottlingBurstLimit=40 LogRetentionDays=30
} else {
    sam deploy --stack-name event-registration-ticketing-dev `
        --capabilities CAPABILITY_IAM --no-confirm-changeset `
        --no-fail-on-empty-changeset --resolve-s3 `
        --parameter-overrides Stage=dev
}

Write-Host "==> Deployment complete." -ForegroundColor Green
