#!/bin/bash
set -e

# Definir nova versão
NEW_VERSION="0.0.18"

echo "🐳 Building Dynatrace Extension v${NEW_VERSION} para x86_64 Linux via Docker..."
echo ""

# Verificar se Docker está rodando
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker não está rodando!"
    exit 1
fi

echo "✅ Docker está rodando"
echo ""

# Atualizar versão nos arquivos
echo "📝 Atualizando versão para ${NEW_VERSION}..."

# Atualizar extension.yaml
sed -i.bak "s/^version: .*/version: ${NEW_VERSION}/" extension/extension.yaml

# Atualizar setup.py
sed -i.bak "s/version='.*'/version='${NEW_VERSION}'/" setup.py
sed -i.bak "s/version=\".*\"/version=\"${NEW_VERSION}\"/" setup.py

echo "✅ Versão atualizada:"
echo "   - extension/extension.yaml: $(grep '^version:' extension/extension.yaml)"
echo "   - setup.py: $(grep "version=" setup.py | head -1)"

# Limpar build anterior
echo ""
echo "🧹 Limpando builds anteriores..."
rm -rf build/ *.egg-info extension/lib/ dist/
rm -f extension/extension.yaml.bak setup.py.bak
mkdir -p dist

echo ""
echo "🏗️ Building no container Linux x86_64 (forçando plataforma)..."
echo ""

docker run --rm \
  --platform linux/amd64 \
  -v "$(pwd)":/work \
  -w /work \
  python:3.10-slim \
  bash -c "
    set -e
    
    echo '📦 Instalando dt-extensions-sdk[cli]...'
    pip install --quiet 'dt-extensions-sdk[cli]'
    
    echo ''
    echo '📥 Baixando dependências para x86_64...'
    mkdir -p extension/lib
    pip download \
      dt-extensions-sdk requests charset-normalizer certifi idna urllib3 \
      -d extension/lib/ \
      --platform manylinux2014_x86_64 \
      --python-version 3.10 \
      --only-binary=:all: \
      --no-deps
    
    echo ''
    echo '🔨 Buildando wheel da extensão...'
    pip wheel --no-deps -w extension/lib/ .
    
    echo ''
    echo '📦 Dependências finais:'
    ls -1 extension/lib/
    
    echo ''
    echo '🔨 Montando extension.zip...'
    mkdir -p dist
    dt ext assemble --source extension --output dist/extension.zip --force
    
    echo ''
    echo '✅ Build concluído!'
  "

echo ""
echo "🔐 Assinando extensão localmente..."
dt ext sign \
  --src dist/extension.zip \
  --output "dist/custom_mongodb.atlas.connection-${NEW_VERSION}.zip" \
  --key ~/.dynatrace/certificates/developer.pem \
  --force

# Limpar extension/lib após build
rm -rf extension/lib

echo ""
echo "🎉 Build completo!"
echo ""
echo "📦 Arquivo final:"
ls -lh dist/custom_mongodb.atlas.connection-*.zip

echo ""
echo "🔍 Verificando charset_normalizer:"
unzip -p "dist/custom_mongodb.atlas.connection-${NEW_VERSION}.zip" extension.zip | unzip -l - | grep "charset_normalizer"

echo ""
echo "✅ Deve aparecer 'x86_64' acima (NÃO 'aarch64')!"
echo "🚀 Pronto para upload: dist/custom_mongodb.atlas.connection-${NEW_VERSION}.zip"
