from unittest import mock
from arxiv_digest import cli


@mock.patch("arxiv_digest.cli.generate_wordcloud")
@mock.patch("arxiv_digest.cli.fetch")
def test_dry_run_no_smtp(mock_fetch, mock_gen):
    mock_fetch.return_value = [
        mock.Mock(title="A study", summary="Abstract body.",
                  authors=["Alice"], link="https://e/1")
    ]
    mock_gen.return_value = "wordcloud.png"
    code = cli.main(["--dry-run", "--categories", "cs.AI"])
    assert code == 0