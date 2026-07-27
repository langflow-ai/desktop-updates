# Promove uma release de QA para produção.
# Uso: make release_1.10.2
#   1. Copia qa-releases/v<versão>/ para releases/v<versão>/
#   2. Regenera latest.json a partir do qa_latest.json (notes, pub_date, urls)
#      Binários rastreados por LFS (*.msi, *.tar.gz — ver .gitattributes) saem
#      apontando para media.githubusercontent.com; raw.githubusercontent.com
#      devolveria o ponteiro do LFS em vez do arquivo.
#   3. Adiciona a versão no topo do versions.json

release_%: check_lfs
	@python3 scripts/promote_release.py $*

# Sem o git-lfs os binários entram inteiros no commit e o push é recusado
# (limite de 100 MB do GitHub).
check_lfs:
	@git lfs version >/dev/null 2>&1 || { \
		echo "❌ git-lfs não encontrado — instale com 'brew install git-lfs && git lfs install'"; \
		exit 1; \
	}

.PHONY: release_% check_lfs
