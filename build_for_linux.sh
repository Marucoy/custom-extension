#!/bin/bash
set -e

echo "🏗️ Passo 1: Build com dt-sdk..."
dt-sdk build

echo ""
echo "📦 Passo 2: Corrigindo charset-normalizer para Linux..."

cd dist
SIGNED_FILE="custom_mongodb.atlas.connection-0.0.1.zip"

# Criar diretório limpo
rm -rf temp_work
mkdir temp_work

# Extrair arquivo assinado (extension.zip + extension.zip.sig)
echo "📂 Extraindo ${SIGNED_FILE}..."
unzip -q "${SIGNED_FILE}" -d temp_work

cd temp_work

# Extrair extension.zip
echo "📂 Extraindo extension.zip..."
mkdir extension_content
unzip -q extension.zip -d extension_content

# Agora temos: extension_content/{activationSchema.json, extension.yaml, lib/}
LIB_PATH="extension_content/lib"

echo ""
echo "📦 Wheels atuais:"
ls -1 "$LIB_PATH"

# Remover charset macOS
echo ""
echo "🗑️ Removendo charset_normalizer macOS..."
rm -f "$LIB_PATH"/charset_normalizer*macosx*.whl

# Baixar charset Linux
echo "📥 Baixando charset_normalizer Linux..."
pip download \
  charset-normalizer \
  -d "$LIB_PATH" \
  --platform manylinux2014_x86_64 \
  --python-version 3.10 \
  --only-binary=:all: \
  --no-deps

echo ""
echo "✅ Wheels corrigidos:"
ls -1 "$LIB_PATH"

# Reempacotar extension.zip (com arquivos na raiz, sem pasta wrapper)
echo ""
echo "📦 Reempacotando extension.zip..."
cd extension_content
zip -qr ../extension_new.zip *
cd ..

# Substituir extension.zip
rm -f extension.zip
mv extension_new.zip extension.zip

# Remover diretório temporário
rm -rf extension_content

# Verificar que temos apenas 2 arquivos
echo ""
echo "📋 Arquivos finais (devem ser 2):"
ls -la

# Criar arquivo final
echo ""
echo "📦 Criando arquivo final..."
zip -q ../temp_final.zip extension.zip extension.zip.sig

cd ..

# Assinar
echo "🔐 Assinando extensão corrigida..."
dt ext sign \
  --src temp_final.zip \
  --output custom_mongodb.atlas.connection-0.0.1-linux.zip \
  --key ~/.dynatrace/certificates/developer.pem \
  --force

# Limpar
rm -rf temp_work temp_final.zip

cd ..

echo ""
echo "✅ Build completo!"
echo ""
echo "📋 Verificando estrutura final..."
echo "=== NÍVEL 1 (arquivo assinado) ==="
unzip -l dist/custom_mongodb.atlas.connection-0.0.1-linux.zip
echo ""
echo "=== NÍVEL 2 (dentro do extension.zip) ==="
unzip -p dist/custom_mongodb.atlas.connection-0.0.1-linux.zip extension.zip | unzip -l -
echo ""
echo "🎯 Verificando charset_normalizer:"
unzip -p dist/custom_mongodb.atlas.connection-0.0.1-linux.zip extension.zip | unzip -l - | grep "charset_normalizer"
echo ""
echo "🚀 Arquivo pronto: dist/custom_mongodb.atlas.connection-0.0.1-linux.zip"
