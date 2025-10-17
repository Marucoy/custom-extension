cd dist

echo "=========================================="
echo "NÍVEL 1: Arquivo assinado"
echo "=========================================="
unzip -l custom_mongodb.atlas.connection-0.0.1.zip

echo ""
echo "=========================================="
echo "NÍVEL 2: Conteúdo do extension.zip"
echo "=========================================="
unzip -l custom_mongodb.atlas.connection-0.0.1.zip extension.zip
unzip -p custom_mongodb.atlas.connection-0.0.1.zip extension.zip | unzip -l -

echo ""
echo "=========================================="
echo "EXTRAÇÃO COMPLETA PARA ANÁLISE"
echo "=========================================="
rm -rf test_full
mkdir -p test_full

# Extrair arquivo assinado
unzip -q custom_mongodb.atlas.connection-0.0.1.zip -d test_full

echo "=== Raiz do arquivo assinado ==="
ls -la test_full/

echo ""
echo "=== Extraindo extension.zip ==="
cd test_full
unzip -q extension.zip -d extension_extracted

echo ""
echo "=== Conteúdo de extension_extracted/ ==="
ls -la extension_extracted/

echo ""
echo "=== Estrutura completa em árvore ==="
cd extension_extracted
find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'

echo ""
echo "=== Arquivos .whl (wheels) ==="
find . -name "*.whl" -exec ls -lh {} \;

cd ../../..
