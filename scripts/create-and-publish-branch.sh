#!/bin/bash

# Script to create and publish the accelerate-with-copilot branch
# Usage: ./create-and-publish-branch.sh

set -e

BRANCH_NAME="accelerate-with-copilot"
BASE_COMMIT="77fbcc4"

echo "Creating branch: $BRANCH_NAME"
echo "Base commit: $BASE_COMMIT"
echo ""

# Check if branch already exists
if git rev-parse --verify "$BRANCH_NAME" >/dev/null 2>&1; then
    echo "✅ Branch '$BRANCH_NAME' already exists locally"
    git checkout "$BRANCH_NAME"
else
    echo "Creating new branch '$BRANCH_NAME' from commit $BASE_COMMIT..."
    git checkout -b "$BRANCH_NAME" "$BASE_COMMIT"
    echo "✅ Branch created successfully"
fi

# Check if branch exists on remote
if git ls-remote --heads origin "$BRANCH_NAME" | grep -q "$BRANCH_NAME"; then
    echo "✅ Branch '$BRANCH_NAME' already exists on remote"
else
    echo ""
    echo "Publishing branch to remote..."
    git push -u origin "$BRANCH_NAME"
    echo "✅ Branch published successfully"
fi

echo ""
echo "Branch '$BRANCH_NAME' is ready!"
echo ""
echo "Verify with:"
echo "  git branch -a | grep $BRANCH_NAME"
