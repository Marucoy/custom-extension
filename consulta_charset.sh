cd dist

echo "=== Conteúdo do extension.zip ==="
unzip -l custom_mongodb.atlas.connection-0.0.2.zip

echo ""
echo "=== Wheels dentro do extension.zip ==="
unzip -p custom_mongodb.atlas.connection-0.0.2.zip extension.zip | unzip -l - | grep "\.whl$"

echo ""
echo "=== Verificando charset_normalizer especificamente ==="
unzip -p custom_mongodb.atlas.connection-0.0.2.zip extension.zip | unzip -l - | grep "charset"
