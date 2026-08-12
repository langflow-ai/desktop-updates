# Promotes a production build to the update feed.
# Usage: make release-1.11.3   (make release_1.11.3 works too)
#
# Source: prod-release-binaries/, one folder per OS/arch, each holding the
# binary and its detached signature (<binary>.sig):
#   langflow-macos-arm-updater/        -> darwin-aarch64   -> releases/vX/macOS/
#   langflow-macos-universal-updater/  -> darwin-x86_64    -> releases/vX/macOS-x86_64/
#   langflow-windows-msi/              -> windows-x86_64   -> releases/vX/windows/
#
#   1. Copies each binary into releases/v<version>/
#   2. Rebuilds latest.json (notes, pub_date, urls, signatures from the .sig files)
#      LFS-tracked binaries (*.msi, *.tar.gz — see .gitattributes) end up
#      pointing at media.githubusercontent.com; raw.githubusercontent.com
#      would return the LFS pointer instead of the file.
#   3. Prepends the version to versions.json

release-%: check_lfs
	@python3 scripts/promote_release.py $*

# Kept so the older underscore form doesn't break.
release_%: check_lfs
	@python3 scripts/promote_release.py $*

# Without git-lfs the binaries go into the commit whole and the push is
# rejected (GitHub's 100 MB limit).
check_lfs:
	@git lfs version >/dev/null 2>&1 || { \
		echo "❌ git-lfs not found — install it with 'brew install git-lfs && git lfs install'"; \
		exit 1; \
	}

.PHONY: release_% release-% check_lfs
