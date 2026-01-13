# Agentic Design Patterns

Project repository for Agentic Design Patterns.
Tutorials are based on "Agentic Design Patterns" written by Antonio Gulli.

## Setup

This project requires **Python 3.11** (or 3.12) due to dependency constraints with `crewai`.

1. **Create/Activate Environment**:
   ```bash
   conda create -n agentic_env python=3.11
   conda activate agentic_env
   ```

2. **Install Dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Google Cloud SDK Setup**:
   The project uses Google Cloud services. Install the SDK and configure your path:
   
   - Download and run the installer (we recommend `~/google-cloud-sdk`)
   - Ensure your `.zshrc` (or equivalent) includes the SDK paths:
     ```bash
     # The next line updates PATH for the Google Cloud SDK.
     if [ -f '/Users/<username>/google-cloud-sdk/path.zsh.inc' ]; then . '/Users/<username>/google-cloud-sdk/path.zsh.inc'; fi

     # The next line enables shell command completion for gcloud.
     if [ -f '/Users/<username>/google-cloud-sdk/completion.zsh.inc' ]; then . '/Users/<username>/google-cloud-sdk/completion.zsh.inc'; fi
     ```
   - Initialize the SDK:
     ```bash
     gcloud init
     ```

   > [!TIP]
   > If you encounter permission issues with `.zshrc` during installation, ensure the file is owned by your user: `sudo chown $(whoami):staff ~/.zshrc`
