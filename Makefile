.PHONY: gitleaks
gitleaks:
	gitleaks --repo-path=$(PWD) --config=gitleaks.toml \
		--report=gitleaks-report.json --redact
