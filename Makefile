# Promove uma release de QA para produção.
# Uso: make release_1.10.2
#   1. Copia qa-releases/v<versão>/ para releases/v<versão>/
#   2. Regenera latest.json a partir do qa_latest.json (notes, pub_date, urls)
#   3. Adiciona a versão no topo do versions.json

release_%:
	@python3 scripts/promote_release.py $*

.PHONY: release_%
