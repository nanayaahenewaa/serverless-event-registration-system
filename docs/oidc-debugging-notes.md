# OIDC Authentication Debugging Notes

## Symptom
GitHub Actions deploy workflow consistently failed at the "Configure AWS
credentials via OIDC" step with: `Not authorized to perform
sts:AssumeRoleWithWebIdentity`, despite the IAM trust policy, OIDC provider
configuration, and GitHub secrets all appearing correct on inspection.

## Ruled Out
- Trust policy document content (verified via AWS CLI, matched exactly)
- OIDC provider client ID list and thumbprint (verified correct)
- GitHub environment-scoped secrets shadowing repository secrets (dev
  environment had no secrets configured)
- Secret value corruption/length (confirmed correct length: 68 characters)

## Root Cause
GitHub's "immutable subject claims" feature (enabled by default on private
repositories at the time) appends numeric owner/repo IDs to the `sub` claim:

    repo:OWNER@OWNER_ID/REPO@REPO_ID:environment:ENV

instead of the commonly-documented format:

    repo:OWNER/REPO:environment:ENV

This was only discoverable by manually requesting and decoding the actual
OIDC JWT token issued to the workflow run, since AWS's error message gives
no detail about which specific claim failed to match.

## Fix
Updated the IAM trust policy's `StringLike` condition on
`token.actions.githubusercontent.com:sub` to match the actual claim format
including the numeric IDs.

## Diagnostic Technique (Reusable)
Add a temporary step to decode the token directly:

    - name: Debug OIDC token claims
      run: |
        curl -sSL -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
          "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.amazonaws.com" \
        | jq -r '.value' | cut -d '.' -f2 | base64 --decode 2>/dev/null | jq .

## Note on Branch Protection
Classic branch protection rules on private GitHub repositories are not
enforced on the free tier. This repository was made public partway through
Phase 3 to enable real enforcement. Repository owners retain bypass
permissions on classic protection rules by default; this was left enabled
for a solo-maintainer project rather than fully locking out the owner.