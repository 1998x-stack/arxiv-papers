# Latest Papers Emailer

This project automates the process of fetching the latest deep learning, machine learning, and reinforcement learning papers from arXiv. It generates a word cloud from the abstracts and titles of the papers and sends an email with the paper summaries and word cloud image attached.

## Features

- Fetches the latest papers from arXiv categories:
  - Deep Learning
  - Machine Learning
  - Reinforcement Learning
  - Computer Vision
  - Artificial Intelligence
- Generates a word cloud from the paper abstracts and titles.
- Sends a well-formatted email with the paper summaries and the word cloud image attached.
- Automated workflow using GitHub Actions.

## Project Structure

```
project-root/
├── .github/
│   └── workflows/
│       └── send_papers.yml       # GitHub Actions workflow for automation
├── src/
│   ├── __init__.py               # Package initialization file
│   ├── news_email_scheduler.py   # Main script to schedule and send the emails
│   ├── paper_fetcher.py          # Fetches the latest papers from arXiv
│   ├── email_sender.py           # Handles email sending with optional attachments
│   ├── markdown_formatter.py     # Formats papers into markdown for email content
│   ├── wordcloud_generator.py    # Generates word clouds from the paper data
│   └── logger.py                 # Configures logging across the application
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
└── .gitignore                    # Files and directories to be ignored in Git
```

## Setup Instructions

### 1. Clone the Repository

Clone the repository to your local machine using the following command:

```bash
git clone https://github.com/yourusername/your-repo-name.git
```

### 2. Install Dependencies

Navigate to the project directory and install the required Python packages using:

```bash
cd your-repo-name
pip install -r requirements.txt
```

### 3. Configure Environment Variables

You need to set up email credentials as environment variables or GitHub Secrets to send the emails:

- `EMAIL_USERNAME`: Your email address (e.g., example@gmail.com).
- `EMAIL_PASSWORD`: Your email password or app-specific password.

For GitHub Actions, you can configure these values as secrets by navigating to:
`Settings > Secrets and Variables > Actions > New repository secret`.

### 4. Running the Script Locally

You can run the script locally for testing by using:

```bash
python src/news_email_scheduler.py
```

This will fetch the latest papers, generate a word cloud, and send the email.

## GitHub Actions Automation

The project includes a GitHub Actions workflow that automates fetching papers and sending emails at regular intervals.

- The workflow is defined in `.github/workflows/send_papers.yml`.
- The script is scheduled to run daily at 8 AM UTC and will send the email automatically.

To trigger the workflow manually, you can use the "Run Workflow" option in the GitHub Actions interface.

### Workflow Configuration

```yaml
name: Send Latest Papers

on:
  schedule:
    - cron: '0 8 * * *'  # Runs daily at 8 AM UTC
  workflow_dispatch:      # Allows manual triggering

jobs:
  send_papers:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Script
        env:
          EMAIL_USERNAME: ${{ secrets.EMAIL_USERNAME }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: |
          python src/news_email_scheduler.py
```

## Customization

### Modify Paper Categories

You can modify the arXiv categories being queried by editing the `query` in `src/paper_fetcher.py`:

```python
self.query = 'cat:cs.LG+OR+cat:cs.AI+OR+cat:cs.NE+OR+cat:cs.CV'
```

You can refer to [arXiv's category list](https://arxiv.org/category_taxonomy) for more categories.

### Modify Email Recipients

To change the recipients of the email, update the `to_emails` list in `src/news_email_scheduler.py`:

```python
to_emails = ['recipient@example.com']  # Add more emails as needed
```

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.