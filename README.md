# codespotter

codespotter is a simple CLI tool that you can use to critically review the changes in your last commit using AI. Your code is safe, as it won't be used to train any models and will not be stored on our servers.

* Your repo's files remain unchanged, both during the installation and when you use the tool.
* You won't need to set up any local key.

## How to use

Here is how to install and use the script on macOS.

1. Download the script into your PATH:

   ```bash
   curl -fsSL https://raw.githubusercontent.com/marcellofuschi/codespotter/main/codespotter.sh -o ./codespotter
   chmod +x ./codespotter
   sudo mv ./codespotter /usr/local/bin/codespotter
   ```

2. Get a review on your latest commit:

   ```bash
   cd path/to/repo
   codespotter
   ```

## Optional: Set up as a Git post‑commit hook

You may find it useful to just run the script after each commit. Here's how to do it automatically.

If your repo already has a `.git/hooks/post-commit` file, just append the `codespotter` command to it.

Otherwise, run this in your project's directory:
```bash
mkdir -p .git/hooks
cat > .git/hooks/post-commit << 'EOF'
#!/usr/bin/env bash
codespotter
EOF
chmod +x .git/hooks/post-commit
```

## Uninstalling codespotter

Remove the codespotter script from your machine:
```bash
rm /usr/local/bin/codespotter
```
